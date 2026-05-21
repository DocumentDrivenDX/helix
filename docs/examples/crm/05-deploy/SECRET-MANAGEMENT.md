# Secret Management

## Overview

All secrets (database passwords, API keys, JWT signing keys, third-party credentials) are stored securely in AWS Secrets Manager and never committed to source code.

## Secrets Inventory

| Secret | Type | Usage | Rotation |
|--------|------|-------|----------|
| `crm/prod/db-password` | String | PostgreSQL authentication | AWS automatic (90 days) |
| `crm/prod/jwt-signing-key` | String | JWT token signing/verification | Manual (no auto-rotation needed) |
| `crm/prod/sentry-dsn` | String | Error tracking | Manual (rare, ~annually) |
| `crm/prod/email-api-key` | String | Email service (SendGrid/AWS SES) | Manual (per provider policy) |
| `crm/prod/stripe-api-key` | String | Payment processing (P1+) | Manual (per Stripe policy) |

## Setup: AWS Secrets Manager

### 1. Create Secrets via AWS Console or CLI

**Via CLI**:
```bash
# Database password
aws secretsmanager create-secret \
  --name crm/prod/db-password \
  --description "PostgreSQL password for production RDS" \
  --secret-string "$(openssl rand -base64 32)" \
  --tags Key=Environment,Value=production Key=Service,Value=crm-api

# JWT signing key
aws secretsmanager create-secret \
  --name crm/prod/jwt-signing-key \
  --description "JWT signing key for session tokens" \
  --secret-string "$(openssl rand -base64 64)" \
  --tags Key=Environment,Value=production Key=Service,Value=crm-api

# Sentry DSN
aws secretsmanager create-secret \
  --name crm/prod/sentry-dsn \
  --description "Sentry error tracking DSN" \
  --secret-string "https://<key>@sentry.io/<project>" \
  --tags Key=Environment,Value=production Key=Service,Value=crm-api

# Email API key
aws secretsmanager create-secret \
  --name crm/prod/email-api-key \
  --description "Email service API key" \
  --secret-string "$(openssl rand -base64 32)" \
  --tags Key=Environment,Value=production Key=Service,Value=crm-api
```

### 2. Create IAM Policy for ECS Task Role

**Policy** (`crm-api-ecs-task-role-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/*"
      ],
      "Condition": {
        "StringEquals": {
          "secretsmanager:VersionStage": "AWSCURRENT"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "arn:aws:kms:us-east-1:123456789:key/*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "secretsmanager.us-east-1.amazonaws.com"
        }
      }
    }
  ]
}
```

**Apply Policy**:
```bash
aws iam put-role-policy \
  --role-name crm-api-ecs-task-role \
  --policy-name crm-api-secrets-access \
  --policy-document file://crm-api-ecs-task-role-policy.json
```

### 3. Inject Secrets into ECS Task Definition

**Task Definition** (`task-definition.json`):
```json
{
  "family": "crm-api-task",
  "containerDefinitions": [
    {
      "name": "crm-api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/crm-api:latest",
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/db-password:password::"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/db-url:url::"
        },
        {
          "name": "JWT_SIGNING_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/jwt-signing-key:key::"
        },
        {
          "name": "SENTRY_DSN",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/sentry-dsn:dsn::"
        },
        {
          "name": "EMAIL_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/email-api-key:key::"
        }
      ]
    }
  ],
  "taskRoleArn": "arn:aws:iam::123456789:role/crm-api-ecs-task-role",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole"
}
```

**How it works**:
- ECS agent fetches secrets from Secrets Manager before container starts
- Secrets injected as environment variables (not visible in ECS console)
- Container sees `DATABASE_PASSWORD=<value>` at runtime
- Secrets never appear in logs or CloudTrail API calls

## Local Development

### Development Secrets (non-production)

Create `.env.local` (NOT checked into git):
```bash
# .env.local (local development only)
DATABASE_URL=postgresql+asyncpg://crm:dev-password@localhost:5432/crm_dev
JWT_SIGNING_KEY=dev-key-only-for-testing-not-secure
SENTRY_DSN=https://dev-key@sentry.io/dev-project  # or empty for development
EMAIL_API_KEY=dev-key-only-for-testing
ENV=development
```

**Load in application** (using `python-dotenv`):
```python
from dotenv import load_dotenv
import os

load_dotenv('.env.local')  # Load from .env.local in development

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SIGNING_KEY = os.getenv("JWT_SIGNING_KEY")
SENTRY_DSN = os.getenv("SENTRY_DSN")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
```

**Docker Compose** (for local integration testing):
```yaml
version: '3.9'
services:
  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://crm:dev-password@postgres:5432/crm_dev
      JWT_SIGNING_KEY: dev-key-only-for-testing
      SENTRY_DSN: ""  # Disabled for local dev
      EMAIL_API_KEY: dev-key-only-for-testing
      ENV: development
```

**Never hardcode secrets in Dockerfile or source code.**

## Secret Rotation

### Database Password Rotation (Automatic)

AWS RDS + Secrets Manager integration:

1. Configure RDS to use Secrets Manager for password management
2. Secrets Manager Lambda function rotates password automatically every 90 days
3. During rotation:
   - New password generated
   - RDS password updated
   - Old password invalidated
   - Secrets Manager version incremented

**Setup** (via AWS Console):
1. Secrets Manager → `crm/prod/db-password` → Edit rotation
2. Enable automatic rotation: 30 days
3. Select Lambda function: `SecretsManagerRDSPostgreSQLRotation`
4. Select VPC/security group (must reach RDS)

**Verification**:
```bash
aws secretsmanager describe-secret --secret-id crm/prod/db-password
# Check RotationRules.AutomaticallyAfterDays = 30
```

### API Key Rotation (Manual)

For third-party API keys without auto-rotation:

1. Generate new key from provider (Sentry, SendGrid, etc.)
2. Update secret in Secrets Manager:
   ```bash
   aws secretsmanager update-secret \
     --secret-id crm/prod/sentry-dsn \
     --secret-string "https://<new-key>@sentry.io/<project>"
   ```
3. Wait for ECS tasks to be recreated (or restart tasks manually)
4. Revoke old key from provider

**Timing**: Stagger rotations (e.g., Sentry on 1st of month, Email on 15th)

### JWT Signing Key Rotation (Not Needed)

JWT signing keys are not rotated in the traditional sense:

**Reason**: JWTs are stateless and don't require the same rotation schedule as passwords.

**If compromise is suspected**:
1. Generate new JWT signing key
2. Update `JWT_SIGNING_KEY` in Secrets Manager
3. Restart ECS tasks (will use new key for new tokens)
4. Existing tokens with old key will become invalid (acceptable; users log back in)

## Secret Access Audit

### CloudTrail Logging

All secret access is logged in CloudTrail:

```bash
# Query CloudTrail for secret access
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=crm/prod/db-password \
  --max-results 50
```

**Example output**:
```json
{
  "EventName": "GetSecretValue",
  "EventTime": "2026-05-18T10:30:00Z",
  "Username": "crm-api-ecs-task-role",
  "Resources": [{
    "ARN": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/db-password",
    "ResourceType": "AWS::SecretsManager::Secret"
  }]
}
```

### Access Policy Restrictions

**Principle of Least Privilege**:
- ECS task role can read secrets tagged `crm/prod/*` only
- GitHub Actions CI role can update secrets (limited to staging/dev)
- Admin role required to delete secrets
- Never allow human users direct secret access; use temporary credentials

## Security Best Practices

### DO ✅
- ✅ Store all secrets in Secrets Manager (not in source code, Docker image, or environment)
- ✅ Use IAM roles (not access keys) for ECS tasks
- ✅ Enable CloudTrail logging
- ✅ Rotate passwords every 90 days
- ✅ Use unique secrets for each environment (dev, staging, prod)
- ✅ Use strong, random values (openssl rand -base64 32)
- ✅ Enable encryption in transit (TLS 1.2+)
- ✅ Audit secret access in CloudTrail regularly

### DON'T ❌
- ❌ Commit secrets to git (ever)
- ❌ Pass secrets as command-line arguments (visible in process list)
- ❌ Log secrets (filter sensitive fields before logging)
- ❌ Store secrets in Docker images or Dockerfile
- ❌ Use the same secret for multiple environments
- ❌ Hardcode secrets in application code
- ❌ Share secrets via email or Slack
- ❌ Use weak or human-readable secrets

## Incident Response: Secret Compromise

**If secret is accidentally committed**:
1. Immediately rotate secret:
   ```bash
   aws secretsmanager update-secret --secret-id crm/prod/db-password --secret-string "$(openssl rand -base64 32)"
   ```
2. Force ECS task restart (pick up new secret):
   ```bash
   aws ecs update-service --cluster crm-prod --service crm-api-service --force-new-deployment
   ```
3. Rewrite git history (remove commit with secret):
   ```bash
   # WARNING: destructive operation; coordinate with team
   git filter-branch --tree-filter 'rm -f .env' HEAD
   git push --force-with-lease
   ```
4. Revoke old secret from provider (if applicable)
5. Document incident and update onboarding to prevent recurrence

**If AWS credentials are compromised**:
1. Immediately revoke access keys:
   ```bash
   aws iam delete-access-key --user-name <user> --access-key-id <key>
   ```
2. Audit CloudTrail for unauthorized access
3. Reset all secrets (rotate database password, JWT key, API keys)
4. Investigate scope of damage (what data was accessed?)
5. Notify security team and incident commander

## Secret Lifecycle Checklist

**Deployment Day**:
- [ ] Create all secrets in Secrets Manager
- [ ] Configure ECS task role with read permissions
- [ ] Update task definition with secret references
- [ ] Deploy and verify (health check passes, logs show no secret errors)

**Monthly**:
- [ ] Audit CloudTrail for unusual access patterns
- [ ] Review secret rotation history (automatic passwords should be recent)
- [ ] Check for orphaned secrets (manually created but no longer used)

**Quarterly**:
- [ ] Rotate API keys from third-party providers (even if not required)
- [ ] Audit IAM policies for least-privilege compliance
- [ ] Update documentation if secret structure changes

**Annually**:
- [ ] Security audit of all secrets and access patterns
- [ ] Incident report review (any compromises or near-misses?)
