# Monitoring and Logging Strategy

## Overview

Production monitoring consists of three pillars:

1. **Error Tracking** (Sentry): Captures unhandled exceptions and errors
2. **Performance Metrics** (CloudWatch): Request latency, database performance, resource utilization
3. **Structured Logging** (CloudWatch Logs): Detailed request/response logs for debugging and audit

## 1. Error Tracking: Sentry

### Setup

**Sentry Account**: Create account at https://sentry.io

**Configuration**:
- Organization: CRM
- Project: `crm-api`
- DSN: `https://<key>@sentry.io/<project-id>` (stored in Secrets Manager)

### FastAPI Integration

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import os

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlAlchemyIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    traces_sample_rate=0.1,  # 10% of requests for performance tracing
    profiles_sample_rate=0.1,  # 10% of requests for CPU profiling
    environment=os.getenv("ENV", "production"),
    release=os.getenv("API_VERSION", "0.1.0"),
    attach_stacktrace=True,
)
```

### Captured Events

**Automatic**:
- Unhandled exceptions in request handlers
- Database errors (connection failures, query timeouts)
- Async task failures
- HTTP 5xx errors

**Manual** (add to code):
```python
import sentry_sdk

try:
    # risky operation
    pass
except Exception as e:
    sentry_sdk.capture_exception(
        e,
        tags={
            "component": "payment_gateway",
            "workspace_id": workspace_id,
        }
    )
```

### Alerting Rules

| Rule | Trigger | Action |
|------|---------|--------|
| Error spike | 5+ errors in 5 minutes | Notify #oncall |
| Critical error | Tagged `level:critical` | Page oncall immediately |
| Database error | SQLAlchemy exception | Notify #database-team |
| Auth error | Failed JWT validation | Log only (no alert) |

### Sentry Dashboard Queries

```
# Recent errors by service
service:crm-api

# Errors by workspace (multi-tenant isolation)
tags.workspace_id:[1000 TO 9999]

# Slow transactions (>2s)
transaction.duration:[2000 TO 60000]

# Errors in last 24h
timestamp:[now-24h TO now]
```

## 2. Performance Metrics: CloudWatch

### Metrics to Collect

**Request Metrics** (pushed by application):
- `crm-api/request-latency` (p50, p95, p99, max)
  - Unit: milliseconds
  - Dimensions: `service=crm-api`, `endpoint=/api/opportunities`, `method=GET`
  - Alarm: p95 > 2000ms for >5 minutes

- `crm-api/request-count` (total requests)
  - Unit: count
  - Dimensions: `service=crm-api`, `status_code=200`
  - Alarm: if 0 for >2 minutes (service down)

- `crm-api/error-rate` (5xx / total requests)
  - Unit: percent
  - Alarm: if > 5% for >2 minutes

**Database Metrics**:
- `crm-api/db-query-latency` (p50, p95, p99)
  - Unit: milliseconds
  - Dimensions: `operation=SELECT`, `table=opportunities`
  - Alarm: p99 > 5000ms for >5 minutes

- `crm-api/db-connections` (active connections)
  - Unit: count
  - Alarm: if > 15 (near pool size of 20)

**Resource Metrics** (ECS native):
- CPU utilization (CloudWatch agent)
- Memory utilization (CloudWatch agent)
- Disk utilization
- Network I/O (bytes in/out)

### Middleware Implementation

```python
from fastapi import Request
from time import time
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time()
    
    try:
        response = await call_next(request)
        latency_ms = int((time() - start) * 1000)
        
        # Push metrics to CloudWatch
        cloudwatch.put_metric_data(
            Namespace='crm-api',
            MetricData=[
                {
                    'MetricName': 'request-latency',
                    'Value': latency_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'endpoint', 'Value': request.url.path},
                        {'Name': 'method', 'Value': request.method},
                        {'Name': 'status_code', 'Value': str(response.status_code)},
                    ]
                },
                {
                    'MetricName': 'request-count',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'status_code', 'Value': str(response.status_code)},
                    ]
                }
            ]
        )
        
        return response
    except Exception as e:
        latency_ms = int((time() - start) * 1000)
        cloudwatch.put_metric_data(
            Namespace='crm-api',
            MetricData=[
                {
                    'MetricName': 'request-error',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'endpoint', 'Value': request.url.path},
                        {'Name': 'error_type', 'Value': type(e).__name__},
                    ]
                }
            ]
        )
        raise
```

### Database Metrics Hook

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    query_latency_ms = int(total_time * 1000)
    
    # Extract operation type
    operation = statement.split()[0].upper()  # SELECT, INSERT, UPDATE, DELETE
    
    cloudwatch.put_metric_data(
        Namespace='crm-api',
        MetricData=[
            {
                'MetricName': 'db-query-latency',
                'Value': query_latency_ms,
                'Unit': 'Milliseconds',
                'Dimensions': [
                    {'Name': 'operation', 'Value': operation},
                ]
            }
        ]
    )
```

### CloudWatch Dashboard

Create dashboard with:
- Request latency (p50/p95/p99) over 24h
- Error rate (5xx count / total) with trend
- Database latency (p50/p95/p99)
- Database connection count
- ECS task CPU/memory
- Active error count from Sentry
- Database slow queries (>1s)

## 3. Structured Logging: CloudWatch Logs

### Log Format

All logs are JSON-formatted for easy parsing and querying:

```json
{
  "timestamp": "2026-05-18T10:30:00Z",
  "level": "INFO",
  "message": "GET /api/opportunities succeeded",
  "logger": "crm.api.opportunities",
  "request_id": "req-abc123def456",
  "workspace_id": "ws-123",
  "user_id": "usr-456",
  "http_method": "GET",
  "http_path": "/api/opportunities",
  "http_status": 200,
  "duration_ms": 145
}
```

### Python Logging Configuration

```python
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class JSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat() + "Z"
        log_record['level'] = record.levelname
        # Add request context if available
        if hasattr(request, 'state'):
            log_record['request_id'] = getattr(request.state, 'request_id', None)
            log_record['workspace_id'] = getattr(request.state, 'workspace_id', None)
            log_record['user_id'] = getattr(request.state, 'user_id', None)

# Configure root logger
handler = logging.StreamHandler()
formatter = JSONFormatter()
handler.setFormatter(formatter)
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)
```

### Request Context Middleware

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Extract workspace/user from JWT token
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        request.state.workspace_id = payload.get("workspace_id")
        request.state.user_id = payload.get("sub")
    except:
        request.state.workspace_id = None
        request.state.user_id = None
    
    response = await call_next(request)
    return response
```

### CloudWatch Logs Configuration

**Log Group**: `/aws/ecs/crm-api/production`

**Log Stream**: `<task-id>/<container-name>`

**Retention**: 30 days (adjustable)

**Log Insights Queries**:

```
# All errors in last hour
fields @timestamp, message, level
| filter level = "ERROR"
| stats count() by message

# Slow requests
fields @timestamp, http_path, duration_ms
| filter duration_ms > 1000
| sort duration_ms desc

# Errors per workspace
fields workspace_id, level
| filter level = "ERROR"
| stats count() by workspace_id

# Database slow queries
fields @timestamp, duration_ms
| filter logger = "sqlalchemy" and duration_ms > 1000
| stats avg(duration_ms), max(duration_ms) by http_path
```

### Slow Query Log (PostgreSQL)

**RDS Parameter**: `log_min_duration_statement = 1000` (log queries > 1 second)

**View in CloudWatch**: RDS Enhanced Monitoring streams slow logs to `/aws/rds/instance/crm-postgres/error`

## 4. Alerting Rules

| Alert | Metric | Threshold | Duration | Action |
|-------|--------|-----------|----------|--------|
| High Error Rate | error-rate | >5% | 2 min | Page oncall |
| Request Latency High | request-latency (p95) | >2000ms | 5 min | Notify #alerts |
| Database Down | db-connections | 0 | 1 min | Page oncall |
| Slow Queries | db-query-latency (p99) | >5000ms | 5 min | Notify #database-team |
| Task Unhealthy | HealthyHostCount | <1 | 2 min | Auto-restart + page |
| Disk Usage High | disk-utilization | >80% | 10 min | Notify #ops |

## 5. Runbook: Investigating Errors

### High Error Rate (>5%)

1. Check Sentry dashboard: `https://sentry.io/organizations/crm/issues/`
2. Filter to recent errors: `timestamp:[now-1h TO now]`
3. Group by error type: identify root cause
4. Check CloudWatch logs for context: `fields @message | filter level = "ERROR"`
5. If database error: check RDS status, slow query log, CPU/memory
6. If application error: check code changes in latest deploy
7. Rollback if necessary: `aws ecs update-service --cluster crm-prod --service crm-api-service --force-new-deployment` (will use previous task def)

### High Latency (p95 >2000ms)

1. Check CloudWatch metrics: `crm-api/request-latency`
2. Filter to specific endpoint: `dimensions.endpoint = "/api/opportunities"`
3. Check database latency: is database slow?
   - Query: `SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10`
   - Check for missing indexes on (workspace_id, owner_id)
4. Check CPU utilization: is task CPU-bound?
   - If yes, increase task size or scale horizontally
5. Check for slow middleware: request context extraction, auth validation

### Database Connection Issues

1. Check RDS instance status: `aws rds describe-db-instances --db-instance-identifier crm-postgres`
2. Check security group: verify ECS task can connect on port 5432
3. Check connection pool: `SELECT count(*) FROM pg_stat_activity`
4. If pool exhausted (>20 connections), scale up or investigate long-running queries
5. Check RDS CloudWatch metrics: CPU, storage, connections

## 6. Maintenance

**Weekly**:
- Review Sentry dashboard: prioritize recurring errors
- Check CloudWatch dashboard for anomalies

**Monthly**:
- Review slow query log: optimize queries with high impact
- Analyze error trends: identify patterns

**Quarterly**:
- Tune alerting thresholds based on actual baselines
- Review retention policies (logs, metrics, error traces)
