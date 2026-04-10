# Monitoring Guide - Prompt-Boost Backend v2.0.0

## Table of Contents

1. [Monitoring Architecture](#monitoring-architecture)
2. [Metrics Collection](#metrics-collection)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Alerting](#alerting)
6. [Log Aggregation](#log-aggregation)
7. [Performance Profiling](#performance-profiling)

---

## Monitoring Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Prompt-Boost Backend                      │
│              (FastAPI + Prometheus Metrics)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐   ┌─────▼──────┐  ┌────▼────┐
    │Prometheus│   │ Grafana    │  │ Alert   │
    │ Server   │   │ (Dashboards)  │Manager  │
    └──────────┘   └────────────┘  └─────────┘
```

### Metrics Pipeline

1. **Application** generates metrics (FastAPI middleware, custom code)
2. **Prometheus** scrapes metrics every 15 seconds
3. **Grafana** visualizes metrics from Prometheus
4. **Alertmanager** handles and routes alert notifications

---

## Metrics Collection

### Metrics Categories

#### HTTP Metrics

- `http_requests_total` - Total requests by method, endpoint, status
- `http_request_duration_seconds` - Request latency histogram
- `active_users_gauge` - Number of active users

#### Recursion Metrics

- `recursion_sessions_total` - Total sessions by technique and status
- `recursion_sessions_running_gauge` - Current running sessions
- `recursion_session_duration_seconds` - Session duration histogram

#### LLM Metrics

- `tokens_used_total` - Token usage by provider and model
- `llm_api_calls_total` - API calls by provider, model, status
- `llm_api_errors_total` - Errors by provider and error type
- `llm_api_duration_seconds` - API latency histogram

#### Database Metrics

- `db_query_duration_seconds` - Query latency by operation and table
- `db_connections_gauge` - Current database connections

#### Cache Metrics

- `cache_hits_total` - Cache hits by name
- `cache_misses_total` - Cache misses by name

### Accessing Metrics

#### Direct HTTP

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Filter specific metrics
curl http://localhost:8000/metrics | grep http_requests_total

# Export to file
curl http://localhost:8000/metrics > metrics.txt
```

#### Kubernetes

```bash
# Port forward to local
kubectl port-forward svc/prompt-boost-backend 8000:8000 -n prompt-boost

# Then access
curl http://localhost:8000/metrics
```

---

## Prometheus Setup

### 1. Install Prometheus

#### Kubernetes Helm

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  -f backend/k8s/prometheus-config.yaml \
  -n monitoring --create-namespace

# Verify installation
kubectl get pods -n monitoring
```

#### Docker Compose

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./backend/k8s/prometheus-config.yaml:/etc/prometheus/prometheus.yml:ro
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
  networks:
    - default
```

### 2. Configure Scraping

Edit `backend/k8s/prometheus-config.yaml`:

```yaml
scrape_configs:
  - job_name: 'prompt-boost-backend'
    scrape_interval: 10s
    static_configs:
      - targets: ['localhost:8000']
```

### 3. Access Prometheus

```bash
# Local development
open http://localhost:9090

# Kubernetes
kubectl port-forward -n monitoring svc/prometheus-server 9090:9090
open http://localhost:9090
```

### 4. Write Queries

#### Example Queries

```promql
# Request rate (requests/second)
rate(http_requests_total[5m])

# Error rate (5xx errors)
rate(http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Active sessions
recursion_sessions_running_gauge

# Session success rate
rate(recursion_sessions_total{status="completed"}[5m]) / 
rate(recursion_sessions_total[5m])

# Token usage rate (tokens/minute)
rate(tokens_used_total[1m]) * 60

# Cache hit rate
rate(cache_hits_total[5m]) / 
(rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

---

## Grafana Dashboards

### 1. Install Grafana

#### Kubernetes Helm

```bash
# Install Grafana
helm install grafana prometheus-community/grafana \
  -n monitoring --create-namespace

# Get admin password
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

#### Docker Compose

```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
  networks:
    - default
```

### 2. Add Prometheus Data Source

1. Login to Grafana (http://localhost:3000)
2. Go to **Configuration → Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Enter URL: `http://prometheus:9090`
6. Click **Save & Test**

### 3. Import Dashboards

```bash
# Apply Grafana dashboard ConfigMap
kubectl apply -f backend/k8s/grafana-dashboard.yaml -n monitoring

# Dashboard becomes available in Grafana
# Go to Dashboards → Browse → Prompt-Boost Backend Monitoring
```

### 4. Create Custom Dashboards

#### Dashboard Panels

1. **Request Rate** (Graph)
   - Query: `rate(http_requests_total[5m])`
   - Legend: `{{endpoint}}`

2. **Error Rate** (Gauge)
   - Query: `rate(http_requests_total{status=~"5.."}[5m])`
   - Thresholds: 0 (green), 0.05 (yellow), 0.1 (red)

3. **Latency** (Heatmap)
   - Query: `rate(http_request_duration_seconds_bucket[5m])`

4. **Active Sessions** (Stat)
   - Query: `recursion_sessions_running_gauge`

5. **Token Usage** (Graph)
   - Query: `rate(tokens_used_total[1m]) * 60`

---

## Alerting

### 1. Configure Alertmanager

Create `alertmanager-config.yaml`:

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 1h
    - match:
        severity: warning
      receiver: 'warning'

receivers:
  - name: 'default'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'

  - name: 'critical'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#critical-alerts'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'

  - name: 'warning'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#warnings'
```

### 2. Alert Rules

Pre-configured alerts in `backend/k8s/prometheus-rules.yaml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighRequestRate | >100 req/s for 5m | warning |
| HighErrorRate | >5% errors for 2m | critical |
| HighRequestLatency | P95 latency >2s for 5m | warning |
| LLMAPIErrors | >0.1 errors/s for 5m | warning |
| LLMAPISlowResponses | P95 latency >10s | warning |
| DatabaseConnectionHigh | >18 connections for 2m | warning |
| DatabaseQuerySlow | P95 query time >1s for 5m | warning |
| SessionsRunningHigh | >50 sessions for 5m | warning |
| SessionFailureRate | >20% failures for 5m | warning |
| CacheHitRateLow | <50% hit rate for 10m | info |
| HighTokenUsage | >10k tokens/hour | warning |

### 3. Setup Slack Notifications

1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Update alertmanager config with webhook URL
3. Deploy alertmanager:

```bash
kubectl create configmap alertmanager-config \
  --from-file=alertmanager-config.yaml \
  -n monitoring

helm install alertmanager prometheus-community/alertmanager \
  -n monitoring --create-namespace
```

### 4. Testing Alerts

```bash
# Trigger alert manually
kubectl exec -n monitoring prometheus-server-0 -- \
  promtool check config /etc/prometheus/prometheus.yml

# View firing alerts in Prometheus UI
# http://localhost:9090/alerts
```

---

## Log Aggregation

### 1. Kubernetes Native Logging

```bash
# View pod logs
kubectl logs deployment/prompt-boost-backend -n prompt-boost

# Stream logs
kubectl logs -f deployment/prompt-boost-backend -n prompt-boost

# View logs from previous pod
kubectl logs -p deployment/prompt-boost-backend -n prompt-boost

# View logs from specific pod
kubectl logs <pod-name> -n prompt-boost -c backend
```

### 2. ELK Stack Integration

```yaml
# Add Elasticsearch
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node

# Add Logstash
logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

# Add Kibana
kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### 3. Loki + Promtail (Lightweight)

```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/log:/var/log
    - ./promtail-config.yaml:/etc/promtail/config.yml
```

---

## Performance Profiling

### 1. Python Profiling

```python
# In src/main.py
from pyinstrument import Profiler

profiler = Profiler()

@app.middleware("http")
async def profile_middleware(request: Request, call_next):
    if request.query_params.get("profile"):
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        return HTMLResponse(profiler.output_html())
    return await call_next(request)
```

Usage:
```bash
curl http://localhost:8000/api/recursion/execute?profile=true
```

### 2. Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile specific function
python -m memory_profiler src/main.py
```

### 3. Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
# Run: locust -f locustfile.py -u 100 -r 10

# Or use Apache Bench
ab -n 1000 -c 100 http://localhost:8000/health
```

### 4. Check Resource Usage

```bash
# Kubernetes resource usage
kubectl top nodes
kubectl top pods -n prompt-boost

# Docker resource usage
docker stats prompt-boost-backend

# System metrics
ps aux | grep python
top -p $(pgrep -f "python.*main")
```

---

## Dashboard Best Practices

### Key Metrics to Monitor

1. **System Health**
   - Request rate and error rate
   - Response latency (p50, p95, p99)
   - Pod restart count

2. **Business Metrics**
   - Session completion rate
   - Average session duration
   - Techniques usage distribution

3. **Resource Usage**
   - CPU and memory utilization
   - Database connections
   - Cache hit rate

4. **Errors and Reliability**
   - Error rate by endpoint
   - LLM API failures
   - Database query errors

### Alert Response Guide

| Alert | Severity | Action |
|-------|----------|--------|
| HighRequestRate | ⚠️ | Monitor, consider scaling |
| HighErrorRate | 🔴 | Investigate immediately |
| HighRequestLatency | ⚠️ | Check database, cache |
| LLMAPIErrors | ⚠️ | Check provider status |
| DatabaseConnectionHigh | ⚠️ | Check connection leaks |
| SessionFailureRate | ⚠️ | Check engine logs |

---

## Support & Troubleshooting

### Common Issues

**Metrics not appearing:**
- Check Prometheus targets: http://localhost:9090/targets
- Verify pod is running: `kubectl get pods -n prompt-boost`
- Check logs: `kubectl logs -f deployment/prompt-boost-backend -n prompt-boost`

**Alerts not firing:**
- Check alertmanager status: `kubectl get pods -n monitoring`
- Verify alert rules: http://localhost:9090/rules
- Test webhook: `curl -X POST <webhook_url> -d '{}'`

**Grafana not displaying data:**
- Verify Prometheus is running: `kubectl get pods -n monitoring`
- Check data source: Grafana → Configuration → Data Sources
- Try manual query in Prometheus UI

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
