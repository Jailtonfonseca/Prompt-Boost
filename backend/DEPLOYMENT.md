# Deployment Guide - Prompt-Boost Backend v2.0.0

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+** - For local development
- **Docker & Docker Compose** - For containerized deployment
- **Kubernetes 1.27+** - For production K8s deployment
- **kubectl** - Kubernetes CLI
- **Helm** (optional) - For package management

### Infrastructure

- **PostgreSQL 15+** - Database
- **Redis 7+** - Caching layer
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization (optional)
- **Alertmanager** - Alert handling (optional)

---

## Local Development

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Start Services with Docker Compose

```bash
# From backend directory
docker compose up -d

# Verify services are running
docker compose ps

# Check logs
docker compose logs -f backend
```

### 3. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

### 4. Run Application

```bash
# Local development
python -m src.main

# With auto-reload
ENVIRONMENT=development python -m src.main
```

### 5. Access Services

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## Docker Deployment

### 1. Build Docker Image

```bash
# Build for production
docker build -t prompt-boost/backend:latest \
  --target production \
  -f backend/Dockerfile \
  backend/

# Build for development
docker build -t prompt-boost/backend:dev \
  --target development \
  -f backend/Dockerfile \
  backend/

# Build with specific tag
docker build -t prompt-boost/backend:v2.0.0 \
  --target production \
  -f backend/Dockerfile \
  backend/
```

### 2. Push to Registry

```bash
# Tag for registry
docker tag prompt-boost/backend:latest ghcr.io/anomalyco/prompt-boost-backend:latest

# Login to registry
docker login ghcr.io

# Push image
docker push ghcr.io/anomalyco/prompt-boost-backend:latest
```

### 3. Run Container

```bash
# Run with environment variables
docker run -d \
  --name prompt-boost-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres:5432/prompt_boost" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e OPENAI_API_KEY="sk-..." \
  -e ENVIRONMENT="production" \
  prompt-boost/backend:latest

# With docker-compose (already configured)
docker compose up -d backend
```

### 4. Verify Container

```bash
# Check logs
docker logs prompt-boost-backend

# Check health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics
```

---

## Kubernetes Deployment

### 1. Prerequisites

```bash
# Verify kubectl access
kubectl cluster-info
kubectl get nodes

# Create namespace
kubectl create namespace prompt-boost
kubectl label namespace prompt-boost monitoring=enabled
```

### 2. Create Secrets

```bash
# Create Kubernetes Secret from template
kubectl create secret generic prompt-boost-secrets \
  --from-literal=database_url="postgresql+asyncpg://user:password@postgres-service:5432/prompt_boost" \
  --from-literal=redis_url="redis://redis-service:6379/0" \
  --from-literal=openai_api_key="sk-..." \
  --from-literal=secret_key="your-jwt-secret-key" \
  -n prompt-boost

# Or apply from file
kubectl apply -f backend/k8s/secrets.yaml -n prompt-boost
```

### 3. Deploy Application

```bash
# Apply ConfigMap
kubectl apply -f backend/k8s/configmap.yaml -n prompt-boost

# Apply RBAC
kubectl apply -f backend/k8s/rbac.yaml -n prompt-boost

# Apply Deployment, Service, and HPA
kubectl apply -f backend/k8s/deployment.yaml -n prompt-boost

# Apply Ingress
kubectl apply -f backend/k8s/ingress.yaml -n prompt-boost

# Verify deployment
kubectl get deployment,service,ingress,pods -n prompt-boost
```

### 4. Monitor Deployment

```bash
# Watch rollout status
kubectl rollout status deployment/prompt-boost-backend -n prompt-boost

# Check pod status
kubectl get pods -n prompt-boost -w

# View pod logs
kubectl logs deployment/prompt-boost-backend -n prompt-boost -f

# Check events
kubectl describe pod <pod-name> -n prompt-boost
```

### 5. Test Application

```bash
# Port forward to local
kubectl port-forward svc/prompt-boost-backend 8000:8000 -n prompt-boost

# Test health
curl http://localhost:8000/health

# Test metrics
curl http://localhost:8000/metrics
```

### 6. Scaling

```bash
# Manual scaling
kubectl scale deployment prompt-boost-backend --replicas=5 -n prompt-boost

# Check HPA status
kubectl get hpa -n prompt-boost
kubectl describe hpa prompt-boost-backend-hpa -n prompt-boost

# Watch HPA activity
kubectl get hpa -n prompt-boost -w
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment: development, staging, production |
| `DEBUG` | `false` | Enable debug mode |
| `DATABASE_URL` | - | PostgreSQL async URL |
| `REDIS_URL` | - | Redis connection URL |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `GEMINI_API_KEY` | - | Google Gemini API key |
| `MAX_TOKENS_PER_DAY` | `100000` | Daily token limit |
| `MAX_TOKENS_PER_USER` | `10000` | Per-user token limit |
| `DEFAULT_MAX_ITERATIONS` | `5` | Default recursion iterations |
| `ENABLE_PROMETHEUS` | `true` | Enable Prometheus metrics |

### ConfigMap

Edit `backend/k8s/configmap.yaml` for non-sensitive configuration:

```yaml
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  CORS_ORIGINS: "https://yourdomain.com"
  MAX_TOKENS_PER_DAY: "100000"
```

### Secrets

Edit `backend/k8s/secrets.yaml` for sensitive data:

```yaml
stringData:
  database_url: "postgresql+asyncpg://..."
  openai_api_key: "sk-..."
  secret_key: "your-jwt-secret"
```

**Important**: Use external secrets management in production (Sealed Secrets, External Secrets Operator, or HashiCorp Vault).

---

## Monitoring

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:

```
# HTTP Request Metrics
http_requests_total - Total requests by method, endpoint, status
http_request_duration_seconds - Request latency histogram

# Recursion Metrics
recursion_sessions_total - Total sessions by technique and status
recursion_sessions_running_gauge - Current running sessions
recursion_session_duration_seconds - Session duration histogram

# LLM Metrics
tokens_used_total - Token usage by provider and model
llm_api_calls_total - API calls by provider, model, status
llm_api_errors_total - Errors by provider and error type
llm_api_duration_seconds - API call latency

# Database Metrics
db_query_duration_seconds - Query latency by operation and table
db_connections_gauge - Current connections

# Cache Metrics
cache_hits_total - Cache hits by name
cache_misses_total - Cache misses by name
```

### Setup Prometheus

```bash
# Apply Prometheus config
kubectl create configmap prometheus-config \
  --from-file=backend/k8s/prometheus-config.yaml \
  -n monitoring

# Apply alert rules
kubectl apply -f backend/k8s/prometheus-rules.yaml -n monitoring
```

### Setup Grafana

```bash
# Apply Grafana dashboard
kubectl apply -f backend/k8s/grafana-dashboard.yaml -n monitoring

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Default credentials: admin/admin
```

### Alerts

Pre-configured alerts in `backend/k8s/prometheus-rules.yaml`:

- High request rate (>100 req/s)
- High error rate (>5% errors)
- High latency (P95 > 2s)
- LLM API errors
- Database connection issues
- Session failures
- Low cache hit rate
- High token usage

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod logs
kubectl logs <pod-name> -n prompt-boost

# Check pod events
kubectl describe pod <pod-name> -n prompt-boost

# Common causes:
# - Image pull errors: Check image availability and registry credentials
# - Resource limits: Verify cluster has sufficient resources
# - ConfigMap/Secrets missing: Apply them before deployment
```

#### 2. Database Connection Failed

```bash
# Check database service
kubectl get svc -n prompt-boost

# Test connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h postgres-service -U postgres -d prompt_boost -c "SELECT version();"

# Verify connection string
echo $DATABASE_URL | base64 -d
```

#### 3. Health Check Failing

```bash
# Check health endpoint
kubectl exec <pod-name> -n prompt-boost -- \
  curl -v http://localhost:8000/health

# Check startup logs
kubectl logs <pod-name> -n prompt-boost --previous
```

#### 4. High Memory Usage

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n prompt-boost

# Update resource limits in deployment.yaml:
resources:
  limits:
    memory: "2Gi"  # Increase as needed
```

#### 5. Metrics Not Appearing

```bash
# Check metrics endpoint
kubectl exec <pod-name> -n prompt-boost -- \
  curl http://localhost:8000/metrics | head -20

# Verify Prometheus scraping
# Check Prometheus targets at http://prometheus:9090/targets
```

### Debug Commands

```bash
# Shell into pod
kubectl exec -it <pod-name> -n prompt-boost -- /bin/bash

# Port forward
kubectl port-forward -n prompt-boost pod/<pod-name> 8000:8000

# Stream logs from all pods
kubectl logs -f deployment/prompt-boost-backend -n prompt-boost

# Get deployment history
kubectl rollout history deployment/prompt-boost-backend -n prompt-boost

# Rollback to previous version
kubectl rollout undo deployment/prompt-boost-backend -n prompt-boost
```

### Performance Tuning

```yaml
# Increase replicas
kubectl scale deployment prompt-boost-backend --replicas=10 -n prompt-boost

# Update HPA settings
kubectl patch hpa prompt-boost-backend-hpa -p '{"spec":{"maxReplicas":20}}' -n prompt-boost

# Adjust resource requests/limits
kubectl set resources deployment prompt-boost-backend \
  --requests=cpu=500m,memory=1Gi \
  --limits=cpu=1000m,memory=2Gi \
  -n prompt-boost
```

---

## Production Checklist

- [ ] SSL/TLS certificates configured (cert-manager)
- [ ] Database backups configured
- [ ] Monitoring and alerting active
- [ ] Log aggregation setup (ELK, Loki, etc.)
- [ ] Network policies configured
- [ ] Pod security policies enforced
- [ ] Resource quotas set for namespace
- [ ] RBAC roles properly scoped
- [ ] Secrets encrypted at rest
- [ ] Regular disaster recovery drills
- [ ] Rate limiting configured
- [ ] CORS properly configured for your domain
- [ ] Authentication/Authorization implemented
- [ ] API documentation deployed
- [ ] Health checks validated
- [ ] Metrics and dashboards reviewed

---

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Review logs: `kubectl logs -f deployment/prompt-boost-backend -n prompt-boost`
3. Check metrics: http://localhost:3000 (Grafana)
4. Report issues: https://github.com/anomalyco/prompt-boost/issues
