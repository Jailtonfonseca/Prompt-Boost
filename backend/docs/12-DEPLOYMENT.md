# 12 - Deployment, Docker & CI/CD Pipeline

## 🎯 Objetivo

Documentar estratégia de **deployment**, **containerização** com Docker, e **CI/CD** pipeline com GitHub Actions. Covers:
- Docker image building e optimization
- Kubernetes manifests
- GitHub Actions workflow
- Environment configuration
- Database migrations
- Blue-green deployment

---

## 🐳 Dockerfile

```dockerfile
# Multi-stage build para otimização
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y build-essential

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencies do builder
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

# Copiar código
COPY . .

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Executar aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ⚙️ Environment Configuration

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@db.prod.internal:5432/prompt_boost
REDIS_URL=redis://redis.prod.internal:6379/0

OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

JAEGER_AGENT_HOST=jaeger.monitoring.svc.cluster.local
PROMETHEUS_PUSHGATEWAY=http://pushgateway.monitoring:9091

LOG_LEVEL=INFO
MAX_WORKERS=10
```

---

## ☸️ Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prompt-boost-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prompt-boost
  template:
    metadata:
      labels:
        app: prompt-boost
    spec:
      containers:
      - name: backend
        image: prompt-boost:v2.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/deep
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: prompt-boost-service
spec:
  selector:
    app: prompt-boost
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: prompt-boost-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: prompt-boost-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 🔄 GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=app
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t prompt-boost:${{ github.sha }} .
        docker tag prompt-boost:${{ github.sha }} prompt-boost:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push prompt-boost:${{ github.sha }}
        docker push prompt-boost:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to Kubernetes
      run: |
        mkdir -p $HOME/.kube
        echo ${{ secrets.KUBE_CONFIG }} | base64 -d > $HOME/.kube/config
        kubectl set image deployment/prompt-boost-backend \
          backend=prompt-boost:${{ github.sha }} \
          --namespace=production
        kubectl rollout status deployment/prompt-boost-backend \
          --namespace=production
```

---

## 📝 Database Migrations

```bash
# Rodas migrations ao startup
docker run --rm \
  -e DATABASE_URL=$DB_URL \
  prompt-boost:latest \
  alembic upgrade head

# Ou em Kubernetes hook:
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  template:
    spec:
      containers:
      - name: alembic
        image: prompt-boost:v2.0.0
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
      restartPolicy: Never
```

---

## ✅ Checklist

- [ ] Criar Dockerfile otimizado
- [ ] Configurar Docker Compose local
- [ ] Criar Kubernetes manifests
- [ ] Configurar RBAC policies
- [ ] Adicionar ingress controller
- [ ] Setup GitHub Actions
- [ ] Configurar secrets management (Sealed Secrets)
- [ ] Implementar database migrations
- [ ] Setup monitoring stack (Prometheus, Grafana)
- [ ] Criar runbooks para incidents

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
