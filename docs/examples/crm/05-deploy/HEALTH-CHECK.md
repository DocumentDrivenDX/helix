# Health Check Endpoint

## Overview

The health check endpoint (`GET /health`) is used by load balancers, orchestrators, and monitoring systems to determine if the API is healthy and ready to serve requests.

## Endpoint Specification

**URL**: `GET /health`

**Authentication**: None (public endpoint)

**Response Code**: `HTTP 200 OK` (healthy) or `HTTP 503 Service Unavailable` (unhealthy)

## Response Schema

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": {
    "connected": true,
    "latency_ms": 15
  },
  "timestamp": "2026-05-18T10:30:00Z"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"healthy"` if all checks pass, `"degraded"` if database unavailable but API is responsive |
| `version` | string | API version (matches Dockerfile/environment) |
| `database.connected` | boolean | `true` if database connection successful |
| `database.latency_ms` | number | Database round-trip latency in milliseconds; `-1` if unreachable |
| `timestamp` | string | ISO 8601 timestamp of check |

## Implementation (FastAPI)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time
import os

router = APIRouter(tags=["health"])

async def get_db() -> AsyncSession:
    # Get async session from dependency
    pass

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for load balancers and monitoring.
    
    Returns:
      - 200 if healthy (database connected)
      - 503 if database unavailable
    """
    start = time.time()
    db_connected = False
    db_latency = -1
    
    try:
        # Lightweight database connectivity check
        result = await db.execute("SELECT 1")
        db_latency = int((time.time() - start) * 1000)
        db_connected = True
    except Exception as e:
        # Log error for monitoring (don't include in response)
        import logging
        logging.warning(f"Health check: database unavailable: {str(e)}")
        db_latency = -1
        db_connected = False
    
    status = "healthy" if db_connected else "degraded"
    response_data = {
        "status": status,
        "version": os.getenv("API_VERSION", "0.1.0"),
        "database": {
            "connected": db_connected,
            "latency_ms": db_latency
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Return 503 if degraded (so load balancer removes unhealthy task)
    status_code = 200 if db_connected else 503
    return JSONResponse(response_data, status_code=status_code)
```

## ECS Health Check Configuration

Task definition includes health check:

```json
{
  "name": "crm-api",
  "healthCheck": {
    "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
    "interval": 30,
    "timeout": 10,
    "retries": 3,
    "startPeriod": 5
  }
}
```

### Health Check Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `interval` | 30s | Probe every 30 seconds |
| `timeout` | 10s | Fail probe if no response within 10 seconds |
| `retries` | 3 | Mark unhealthy after 3 consecutive failures |
| `startPeriod` | 5s | Grace period after container start (5 seconds) |

**Implication**: Task marked unhealthy after 30s × 3 failures = 90 seconds of unresponsiveness.

## Load Balancer Integration (ALB)

Application Load Balancer health check configuration:

```
Protocol: HTTP
Path: /health
Port: 8000
Interval: 30 seconds
Timeout: 10 seconds
Healthy threshold: 2 consecutive passes
Unhealthy threshold: 3 consecutive failures
Matcher: 200
```

**Behavior**:
- ALB removes unhealthy tasks from rotation (no traffic)
- ECS auto-scaling may terminate and replace unhealthy tasks

## Monitoring

### CloudWatch Alarm

Alarm triggers if health endpoint returns non-200 for >2 minutes:

```
Metric: HealthyHostCount / TargetGroupArn
Statistic: Average
Threshold: < 1 (at least 1 healthy task required)
Period: 2 minutes
Action: Page oncall engineer
```

### Sentry Monitoring

Health check failures logged and sent to Sentry:

```python
import sentry_sdk

try:
    # database check
except Exception as e:
    sentry_sdk.capture_exception(e, tags={"component": "health-check"})
```

## Testing

### Local Testing

```bash
# From host machine (API running on localhost:8000)
curl http://localhost:8000/health | jq

# Expected output:
{
  "status": "healthy",
  "version": "0.1.0",
  "database": {
    "connected": true,
    "latency_ms": 12
  },
  "timestamp": "2026-05-18T10:30:00Z"
}
```

### Staging/Production Testing

```bash
PROD_URL="https://api.crm.internal"

# Check health
curl -f $PROD_URL/health

# Verify database connectivity
curl $PROD_URL/health | jq '.database.connected'
# Should output: true
```

### Load Test

```bash
# Simulate 100 concurrent health checks
ab -n 1000 -c 100 https://api.crm.internal/health
```

## Troubleshooting

### Health Check Returns 503

**Cause**: Database connection failed

**Steps**:
1. Check database is running: `aws rds describe-db-instances --db-instance-identifier crm-postgres`
2. Check database credentials in Secrets Manager
3. Verify security group allows access from ECS task
4. Check CloudWatch RDS logs for errors

### Health Check Timeout

**Cause**: Network latency or database slow query

**Steps**:
1. Check database latency: `psql -h <db-endpoint> -U crm -d crm_prod -c "SELECT 1"` (should respond <50ms)
2. Check if slow queries are running: `SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10`
3. If database is slow, check CPU/connections via CloudWatch RDS Enhanced Monitoring

### Task Marked Unhealthy by ECS

**Cause**: 3 consecutive health check failures

**Steps**:
1. Check ECS task logs: `aws logs tail /aws/ecs/crm-api/production --follow`
2. Restart task: `aws ecs update-service --cluster crm-prod --service crm-api-service --force-new-deployment`
