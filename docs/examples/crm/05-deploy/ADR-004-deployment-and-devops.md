---
ddx:
  id: ADR-004
  type: architecture-decision-record
  status: resolved
  decision_date: 2026-05-18
  depends_on:
    - ADR-001
    - ADR-003
    - crm.prd
---

# ADR-004: Deployment, Infrastructure, and DevOps Strategy

**Status**: Resolved (2026-05-18)

**Context**: The CRM MVP requires production-grade deployment infrastructure and CI/CD automation. Decisions include:
- Cloud platform (AWS, GCP, Azure)
- Containerization (Docker)
- Infrastructure provisioning (Kubernetes, ECS, App Engine, etc.)
- CI/CD pipeline (GitHub Actions, Cloud Build, etc.)
- Monitoring, logging, and observability
- Secret management
- Database backup and disaster recovery

**Decision Authority**: Architecture Lead / DevOps Lead

## Decision

### 1. Cloud Platform: AWS (Single-Region, us-east-1)

**Chosen**: Amazon Web Services, single region (us-east-1).

**Rationale**:
- **Market dominance**: AWS is the de facto standard for SaaS; team familiarity is highest.
- **Service breadth**: RDS (PostgreSQL), ECR (container registry), ECS (orchestration), CloudWatch (monitoring), Secrets Manager (secrets), S3 (backups).
- **Single-region MVP**: Multi-region is P2+. Single-region (us-east-1) minimizes operational complexity and cost during MVP phase.
- **SLA**: AWS SLA for RDS is 99.95% (5-minute RTO/RPO achievable with Multi-AZ failover; MVP uses single-AZ with daily backups).

**Trade-off**: US-east-1 is geographically distant from non-US users (latency for EU/APAC); deferred to P1+ expansion.

### 2. Containerization: Docker

**Chosen**: Docker + Docker Compose (local development), ECR (registry), ECS Fargate (production orchestration).

**Rationale**:
- **Portability**: Dockerfile encapsulates FastAPI + dependencies; reproducible across dev/staging/production.
- **ECR integration**: AWS-native container registry; tight integration with ECS, IAM, and VPC.
- **No Kubernetes overhead**: ECS Fargate is simpler than self-managed Kubernetes for MVP; pay-per-request pricing aligns with low-traffic early phase.

**Dockerfile Structure** (see `./Dockerfile`):
- Base: `python:3.11-slim`
- Dependencies: FastAPI, SQLAlchemy (async), Pydantic, python-jose, alembic (migrations)
- Entry point: `uvicorn` ASGI server, binds to port 8000
- Health check: `curl /health` endpoint (built into FastAPI)

### 3. CI/CD Pipeline: GitHub Actions

**Chosen**: GitHub Actions (triggers on main branch push).

**Rationale**:
- **Native GitHub integration**: Repository events (push, PR) trigger workflows automatically.
- **No separate infrastructure**: Hosted GitHub runners; no self-managed CI agents.
- **Cost-effective**: Free tier includes 2,000 minutes/month per private repo; sufficient for MVP.
- **Ecosystem**: GitHub Actions Marketplace for standard tasks (Docker build/push, AWS credentials, etc.).

**Pipeline Stages** (see `.github/workflows/deploy.yml`):

1. **Lint** (on every commit):
   - `black` (code formatting)
   - `isort` (import sorting)
   - `flake8` or `ruff` (linting)
   - Exit on failure (no red code deployed)

2. **Build**:
   - `pytest` unit tests (backend logic, ORM mocking)
   - Exit on failure

3. **Integration Test** (Docker-based):
   - Spin up PostgreSQL container
   - Run `pytest` integration tests (real database)
   - Exit on failure

4. **Build Docker Image**:
   - Build image from Dockerfile
   - Tag: `<account-id>.dkr.ecr.us-east-1.amazonaws.com/crm-api:<commit-sha>`
   - Push to ECR

5. **Deploy to Staging** (on main branch):
   - Update ECS task definition with new image tag
   - Rolling update to staging cluster
   - Wait for health check (GET /health returns 200) for 30 seconds
   - Exit on failure

6. **Smoke Test** (in staging):
   - Run smoke test suite against staging API
   - Check: health endpoint, unauthenticated 401 response, workspace isolation
   - Exit on failure (auto-rollback in staging)

7. **Deploy to Production** (on main branch, after staging green):
   - Update ECS task definition with new image tag
   - Rolling update to production cluster
   - Gradual traffic shift (canary: 10% → 50% → 100%)
   - Health checks and CloudWatch alarms monitor each shift
   - Auto-rollback on 5xx error rate spike (>5% in 60s)

### 4. Health Check Endpoint

**Endpoint**: `GET /health`

**Response**: HTTP 200 OK

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

**Implementation** (FastAPI):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import time

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    start = time.time()
    try:
        # Test DB connectivity with lightweight query
        await db.execute("SELECT 1")
        db_latency = int((time.time() - start) * 1000)
        db_connected = True
    except Exception:
        db_latency = -1
        db_connected = False
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "version": "0.1.0",
        "database": {
            "connected": db_connected,
            "latency_ms": db_latency
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

**Usage**:
- ECS task definition health check: probe every 30 seconds, 3 consecutive passes = healthy
- Monitoring: CloudWatch alarm if health endpoint returns non-200 for >2 minutes
- Load balancer (ALB) routes traffic only to healthy tasks

### 5. Monitoring and Logging Strategy

#### Error Tracking: Sentry

**Service**: Sentry (https://sentry.io)

**Configuration**:
- DSN injected via environment variable (Secrets Manager)
- Captures: unhandled exceptions, HTTP 5xx errors, async task failures
- Alert on: critical error spike (5+ errors in 5 minutes), high error rate (>1% of requests)

**Integration** (FastAPI):
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlAlchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of requests for performance tracing
    environment=os.getenv("ENV", "production"),
)
```

#### Performance Metrics: CloudWatch

**Metrics** (pushed by application via ASGI middleware):
- **Request latency** (p50, p95, p99):
  - Middleware captures request start → response end
  - Pushed to CloudWatch custom metric `crm-api/request-latency`
  - Alarm: p95 > 2000ms for >5 minutes

- **Database query latency** (p50, p95, p99):
  - SQLAlchemy event hooks capture query duration
  - Pushed to `crm-api/db-query-latency`
  - Alarm: p99 > 5000ms for >5 minutes

- **Active database connections**:
  - SQLAlchemy connection pool metrics
  - Pushed to `crm-api/db-connections`
  - Alarm: if near pool size (default 20), scale horizontally

**Dashboard** (CloudWatch):
- Request latency (p50/p95/p99) over 24h
- Error rate (5xx count) with error type breakdown
- Database latency and connection count
- ECS task CPU/memory utilization
- Sentry error rate and top errors

#### Structured Logging: Python logging + CloudWatch Logs

**Configuration** (in application):
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "workspace_id": getattr(record, "workspace_id", None),
            "user_id": getattr(record, "user_id", None),
            "request_id": getattr(record, "request_id", None),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.root.addHandler(handler)
```

**CloudWatch Logs**:
- ECS task logs streamed to `/aws/ecs/crm-api/production` (log group)
- Each task writes to stream `<task-id>/<container-name>`
- Log retention: 30 days (adjustable)
- Log Insights queries available for filtering by workspace_id, user_id, error type

**Slow Query Log** (PostgreSQL):
- RDS parameter group: `log_min_duration_statement = 1000` (log queries > 1 second)
- Logs visible in RDS event notifications and CloudWatch Logs (via RDS Enhanced Monitoring)
- Alert: if more than 10 slow queries/minute, page oncall

### 6. Database Backup and Disaster Recovery

#### RDS Backup Strategy

**Automated Backups**:
- **Frequency**: Daily (automated RDS backup window: 03:00–04:00 UTC, low-traffic window)
- **Retention**: 7 days (covers one week of history)
- **RPO** (Recovery Point Objective): 24 hours (acceptable for MVP; acceptable per PRD SLA)
- **RTO** (Recovery Time Objective): <15 minutes (restore from latest backup to new RDS instance)

**Manual Snapshots**:
- Pre-deployment snapshot (before deploying schema migrations or application changes)
- Retained indefinitely (or until 30 days post-deployment if successful)

**Restore Procedure**:
1. Create new RDS instance from backup or snapshot (CloudFormation / Terraform)
2. Update application environment variables (DATABASE_URL) to point to new instance
3. Run data validation checks (count of tables, row counts on critical tables)
4. Switch traffic via load balancer (ALB) to new instance
5. Verify health checks passing; monitor for 5 minutes
6. If successful, terminate old instance; if failure, flip back to old instance

**Backup Testing**:
- Monthly: restore backup to non-production environment and run smoke tests
- Document and track results in runbook

#### Point-in-Time Recovery (Multi-AZ)

**MVP Phase**: Single-AZ RDS (us-east-1a) with daily backups. 
**P1 Phase**: Upgrade to Multi-AZ for synchronous standby replica (RTO <1 minute, automatic failover).

### 7. Secret Management: AWS Secrets Manager

**Secrets Stored**:
- `crm/prod/db-password`: PostgreSQL password
- `crm/prod/api-keys`: Third-party API keys (e.g., Sentry DSN, email service)
- `crm/prod/jwt-signing-key`: JWT signing key for session tokens

**Access Control**:
- IAM role `crm-api-ecs-task-role` can read secrets tagged `crm/prod/*`
- No hardcoded secrets in source code (environment variables only)
- No secrets in Dockerfile or Docker image

**Rotation**:
- Database password: rotated automatically by RDS (every 90 days) via Secrets Manager Lambda integration
- API keys: manual rotation via Secrets Manager UI; no auto-rotation (keys have no built-in rotation API)
- JWT key: no rotation needed for stateless JWT; if compromised, re-sign all tokens (P1+ feature)

**Injection into ECS Task**:
- Task definition includes `secrets` field:
  ```json
  {
    "name": "DATABASE_PASSWORD",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:crm/prod/db-password"
  }
  ```
- ECS agent automatically fetches secret and injects into container environment

### 8. Containerization Details

**Dockerfile** (see `./Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./backend /app

# Health check (ECS will probe this)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run uvicorn ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Push**:
```bash
# Build locally
docker build -t crm-api:latest .

# Tag for ECR
docker tag crm-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/crm-api:latest

# Push to ECR (GitHub Actions does this automatically)
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crm-api:latest
```

**Local Development** (`docker-compose.yml`):
```yaml
version: '3.9'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: crm
      POSTGRES_PASSWORD: dev-password
      POSTGRES_DB: crm_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://crm:dev-password@db:5432/crm_dev
      ENV: development
    depends_on:
      - db
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

Run locally: `docker-compose up`

### 9. Deployment Infrastructure (Terraform / CloudFormation)

**Infrastructure Stack** (minimal for MVP):

1. **VPC**: Single VPC in us-east-1 with 2 public subnets + 2 private subnets (HA across AZs)
2. **RDS PostgreSQL 15**:
   - Single-AZ deployment (db.t3.micro or t3.small)
   - Automated backups enabled
   - Multi-AZ failover deferred to P1+
3. **ECS Fargate Cluster**:
   - Task definition: 1 CPU, 2GB RAM (adjust after profiling)
   - Scaling: 2–5 tasks (horizontal auto-scaling based on CPU/memory)
4. **Application Load Balancer (ALB)**:
   - Listens on 443 (HTTPS)
   - TLS certificate from ACM (auto-renewal)
   - Routes to ECS tasks on port 8000
5. **CloudWatch**: Logs, metrics, dashboards, alarms
6. **Secrets Manager**: Store database password, API keys
7. **ECR Repository**: Store Docker images (lifecycle policy: keep latest 10 images)

---

## Implications for Downstream Artifacts

- **CONTRIBUTING.md**: Add section on local development with Docker Compose; how to run migrations, tests in containers.
- **ops/runbook.md**: Deployment procedure, rollback steps, incident response.
- **CI/CD GitHub Actions workflows**: `.github/workflows/deploy.yml` (main pipeline); `.github/workflows/scheduled-backups.yml` (monthly backup restore test).
- **Infrastructure-as-Code**: Terraform or CloudFormation templates (not in MVP scope; manual AWS setup acceptable for pilot).

---

## Alternatives Considered & Rejected

| Option | Why Not Selected |
|--------|------------------|
| **Kubernetes (EKS)** | Operational overhead for MVP; ECS Fargate is simpler and cheaper. Revisit if horizontal scaling becomes bottleneck. |
| **Google Cloud / Azure** | AWS is team default; multicloud is P2+. |
| **Heroku** | Vendor lock-in; less control over secrets, monitoring, database failover. Cost ~$100+/month vs. ~$50–70/month on AWS for MVP. |
| **Self-managed VPS** | No auto-scaling, poor observability, manual patching. Not acceptable for SaaS. |
| **Multi-region MVP** | Adds complexity (cross-region replication, failover orchestration). Single-region is sufficient for initial markets; expand to eu-west-1 in P1. |

---

## Remaining Decisions (Not in This ADR)

- **Infrastructure-as-Code tooling**: Terraform vs. CloudFormation vs. CDK (tracked separately)
- **Cost optimization**: Reserved instances, Savings Plans (tracked after 3 months of usage metrics)
- **Disaster recovery runbook**: Detailed step-by-step (tracked separately; this ADR covers strategy)
- **Load testing**: JMeter / k6 configuration for pre-launch performance validation (tracked separately)

---

## Design Phase Blockers Resolved

- [x] Deployment platform: AWS, single-region (us-east-1)
- [x] Containerization: Docker + ECS Fargate
- [x] CI/CD: GitHub Actions
- [x] Observability: Sentry (errors) + CloudWatch (metrics/logs)
- [x] Database backup: RDS automated backup (7-day retention, daily snapshots)
- [x] Secrets: AWS Secrets Manager
