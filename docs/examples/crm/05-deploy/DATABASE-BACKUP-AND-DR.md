# Database Backup and Disaster Recovery Strategy

## Overview

The database backup strategy balances RPO (Recovery Point Objective) and RTO (Recovery Time Objective) against operational complexity and cost. For the MVP phase, we accept 24-hour RPO and <15-minute RTO.

## Backup Strategy

### Automated RDS Backups

**Configuration**:
- **Frequency**: Daily (AWS RDS automatic backup window)
- **Backup Window**: 03:00–04:00 UTC (low-traffic window for MVP)
- **Retention Period**: 7 days (covers one week of accidental deletions)
- **Multi-AZ**: Single-AZ in MVP (Multi-AZ failover deferred to P1)
- **RPO**: 24 hours (data loss since last backup acceptable for MVP)

**How it Works**:
- RDS creates full snapshot daily during backup window
- Snapshots retained in AWS S3 (managed by RDS, transparent to user)
- Old snapshots deleted after 7 days
- No application downtime during backup

### Manual Snapshots

**When to Create**:
- Before deploying schema migrations
- Before deploying breaking API changes
- Before major operational changes (e.g., resizing RDS instance)

**Example** (via AWS CLI):
```bash
# Create snapshot
aws rds create-db-snapshot \
  --db-instance-identifier crm-postgres \
  --db-snapshot-identifier crm-postgres-pre-migration-2026-05-18

# List snapshots
aws rds describe-db-snapshots

# Snapshots retained indefinitely (manual cleanup required)
# Delete old snapshot after 30 days (if successful)
aws rds delete-db-snapshot \
  --db-snapshot-identifier crm-postgres-pre-migration-2026-05-18
```

## Restore Procedure

### Point-in-Time Restore (PITR)

Restore to any point in the last 7 days (within automated backup retention window):

```bash
# Restore to specific timestamp
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier crm-postgres \
  --db-instance-identifier crm-postgres-restored-2026-05-18 \
  --restore-time 2026-05-17T10:30:00Z
```

### Restore from Snapshot

Restore to exact state at snapshot time:

```bash
# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier crm-postgres-restored \
  --db-snapshot-identifier crm-postgres-pre-migration-2026-05-18
```

### Post-Restore Validation

```bash
# 1. Connect to restored instance
psql -h <restored-db-endpoint> -U crm -d crm_prod

# 2. Validate schema integrity
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
# Expected output: ~15 tables (opportunities, accounts, contacts, etc.)

# 3. Spot-check data integrity
SELECT COUNT(*) FROM opportunities WHERE deleted_at IS NULL;
SELECT COUNT(*) FROM accounts WHERE deleted_at IS NULL;

# 4. Check indexes
SELECT COUNT(*) FROM pg_stat_user_indexes;
# Expected output: ~20 indexes (workspace_id, owner_id, created_at, etc.)

# 5. Check replication/WAL status (if Multi-AZ)
SHOW max_wal_senders;
SHOW max_replication_slots;
```

### Application Failover

Once restored instance validated:

1. **Update application environment variable**:
   ```bash
   # Get restored instance endpoint
   aws rds describe-db-instances --db-instance-identifier crm-postgres-restored \
     --query 'DBInstances[0].Endpoint.Address'
   
   # Update ECS task definition
   aws ecs register-task-definition \
     --cli-input-json file://task-definition-restored.json
   ```

2. **Update service to use new task definition**:
   ```bash
   aws ecs update-service \
     --cluster crm-prod-cluster \
     --service crm-api-service \
     --task-definition crm-api-task:2 \
     --force-new-deployment
   ```

3. **Monitor health checks** (wait 5 minutes for all tasks healthy)

4. **Run smoke tests** against restored database:
   ```bash
   curl https://api.crm.internal/health
   # Expected: 200 OK with database.connected = true
   ```

5. **Decommission old instance** (once confirmed stable):
   ```bash
   aws rds delete-db-instance \
     --db-instance-identifier crm-postgres \
     --skip-final-snapshot
   ```

### Estimated RTO: 10–15 minutes

- Create/restore instance: 3–5 minutes
- Update application config: 2 minutes
- ECS rolling update: 3–5 minutes
- Health check verification: 2 minutes

## Backup Testing

### Monthly Backup Restore Drill

**Schedule**: First Tuesday of every month, 10:00 AM UTC

**Procedure**:
1. Restore latest automated snapshot to test environment
2. Run smoke test suite (queries, schema validation)
3. Compare row counts with production (should match ±100 rows for active records)
4. Document results in runbook
5. Delete test instance

**Automation** (CloudWatch Events + Lambda):
```python
# Lambda function triggered monthly
import boto3

rds = boto3.client('rds')

def lambda_handler(event, context):
    # Restore from latest snapshot
    snapshots = rds.describe_db_snapshots(
        DBInstanceIdentifier='crm-postgres',
        SnapshotType='automated'
    )['DBSnapshots']
    
    latest = sorted(snapshots, key=lambda x: x['CreateTime'])[-1]
    
    try:
        rds.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier='crm-postgres-test-restore',
            DBSnapshotIdentifier=latest['DBSnapshotIdentifier']
        )
        
        # Wait for instance to be available
        waiter = rds.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier='crm-postgres-test-restore')
        
        # Run smoke tests
        # ... (connection, query validation)
        
        # Delete instance
        rds.delete_db_instance(
            DBInstanceIdentifier='crm-postgres-test-restore',
            SkipFinalSnapshot=True
        )
        
        return {"status": "success", "snapshot": latest['DBSnapshotIdentifier']}
    except Exception as e:
        # Notify oncall on failure
        return {"status": "failure", "error": str(e)}
```

## Multi-AZ Failover (P1)

**Upgrade Path** (after MVP stability):

Enable Multi-AZ:
```bash
aws rds modify-db-instance \
  --db-instance-identifier crm-postgres \
  --multi-az \
  --apply-immediately
```

**Benefits**:
- Synchronous standby replica in different AZ
- Automatic failover on primary failure (<1 minute)
- RTO: <1 minute (vs. 15 minutes for restore)
- RPO: 0 (synchronous replication)

**Cost**: ~2x database cost (primary + standby)

## Disaster Recovery Checklist

**Monthly**:
- [ ] Review RDS backup status (automated backups enabled, retention ≥7 days)
- [ ] Verify backup window is outside peak hours
- [ ] Check CloudWatch metrics for backup duration (should be <30 minutes)

**Quarterly**:
- [ ] Run full restore drill (restore to test environment, validate, delete)
- [ ] Update runbook with any lessons learned
- [ ] Review RTO/RPO targets; adjust if needed

**Incident Response**:
- [ ] Database unavailable? Check RDS instance status
- [ ] Data corruption detected? Restore from backup (within 7-day window)
- [ ] Ransomware/malicious deletion? Restore from oldest backup available
- [ ] Region failure? (P1: manual failover to secondary region)

## Backup Storage Cost

**Estimate**:
- Database size: ~500 MB (MVP)
- Daily snapshots: 500 MB × 7 days = 3.5 GB
- Cost: $0.10 per GB/month = ~$0.35/month
- Manual snapshots: retained indefinitely (estimate 5 snapshots × 500 MB = 2.5 GB, ~$0.25/month)

**Total**: ~$0.60/month (negligible)

## Backup Security

**Encryption**:
- RDS encryption at rest: enabled (AES-256)
- Snapshots: encrypted with same key
- Encryption key: AWS KMS (managed by AWS)

**Access Control**:
- Snapshots not publicly accessible
- Only IAM role `crm-db-admin` can create/restore snapshots
- Enable CloudTrail logging for all snapshot operations

## Long-Term Archival (P2)

**Future Consideration**: Copy snapshots to S3 Glacier for long-term retention (>90 days)

```bash
# Export RDS snapshot to S3 (for long-term archival)
aws rds start-export-task \
  --export-task-identifier crm-postgres-export-2026-05-18 \
  --source-arn arn:aws:rds:us-east-1:123456789:db:crm-postgres \
  --s3-bucket-name crm-backups \
  --s3-prefix long-term/
```

**Cost**: Parquet file in S3 Standard (~$0.023/GB/month) or Glacier (~$0.004/GB/month)

For MVP, automated 7-day retention is sufficient; revisit quarterly.
