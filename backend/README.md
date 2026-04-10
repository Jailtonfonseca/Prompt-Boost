# Prompt-Boost v2.0 Backend

Production-grade recursive reasoning platform with 7 LLM techniques, multi-provider support, real-time WebSocket streaming, and enterprise safety verification.

---

## 🎯 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Prompt-Boost.git
cd Prompt-Boost/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys and database credentials

# 5. Initialize database
alembic upgrade head

# 6. Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. Access API
open http://localhost:8000/docs
```

### Docker Compose (Recommended)

```bash
# Start entire stack (FastAPI + PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

---

## 📚 Documentation

Complete backend documentation is available in `/backend/docs/`:

### 🚀 Getting Started
- **[docs/INDEX.md](docs/INDEX.md)** - Master index & navigation guide
- **[docs/00-ARQUITETURA-BACKEND.md](docs/00-ARQUITETURA-BACKEND.md)** - System architecture overview
- **[docs/15-GUIA-IMPLEMENTACAO.md](docs/15-GUIA-IMPLEMENTACAO.md)** - 4-phase implementation roadmap

### 🧠 7 LLM Techniques
1. **[Self-Refine](docs/02-SELF-REFINE-ENGINE.md)** - Iterative refinement with episodic memory
2. **[Tree of Thoughts](docs/03-TOT-GOT-ENGINES.md)** - Structured exploration with beam search
3. **[Graph of Thoughts](docs/03-TOT-GOT-ENGINES.md)** - Complex relationships & merging
4. **[MCTS](docs/04-MCTS-ENGINE.md)** - Monte Carlo Tree Search with rollouts
5. **[Debate](docs/05-DEBATE-ENGINE.md)** - Multi-agent Pro/Con/Judge synthesis
6. **[Alignment](docs/06-ALIGNMENT-ENGINE.md)** - Safety verification & bias detection
7. **[AutoFormal](docs/07-AUTOFORMAL-ENGINE.md)** - NL to Lean4 formalization

### 🔗 Integration
- **[Providers & LLMs](docs/08-PROVIDERS-E-LLMS.md)** - OpenAI, Anthropic, Gemini, Cohere integration
- **[Database Schema](docs/09-DATABASE-SCHEMA.md)** - SQLAlchemy models & migrations
- **[WebSocket Protocol](docs/10-WEBSOCKET-PROTOCOL.md)** - Real-time streaming
- **[API Reference](docs/13-API-REFERENCE.md)** - REST endpoints & OpenAPI spec

### 🚀 Deployment & Monitoring
- **[Performance Monitoring](docs/11-PERFORMANCE-MONITORING.md)** - Prometheus, Grafana, Jaeger
- **[Deployment](docs/12-DEPLOYMENT.md)** - Docker, Kubernetes, CI/CD
- **[Testing Strategy](docs/14-TESTING-STRATEGY.md)** - Unit, integration, E2E, load tests

### 📖 Examples & Reference
- **[Use Cases](docs/16-CASOS-DE-USO-BACKEND.md)** - 7 real-world scenarios with complete examples
- **[Core Engines](docs/01-ENGINES-IMPLEMENTACAO.md)** - Base engine class & 5-step recursion loop

---

## 🏗️ Project Structure

```
backend/
├── docs/                          # Complete documentation (18 files)
│   ├── 00-ARQUITETURA-BACKEND.md
│   ├── 01-ENGINES-IMPLEMENTACAO.md
│   ├── 02-SELF-REFINE-ENGINE.md
│   ├── 03-TOT-GOT-ENGINES.md
│   ├── 04-MCTS-ENGINE.md
│   ├── 05-DEBATE-ENGINE.md
│   ├── 06-ALIGNMENT-ENGINE.md
│   ├── 07-AUTOFORMAL-ENGINE.md
│   ├── 08-PROVIDERS-E-LLMS.md
│   ├── 09-DATABASE-SCHEMA.md
│   ├── 10-WEBSOCKET-PROTOCOL.md
│   ├── 11-PERFORMANCE-MONITORING.md
│   ├── 12-DEPLOYMENT.md
│   ├── 13-API-REFERENCE.md
│   ├── 14-TESTING-STRATEGY.md
│   ├── 15-GUIA-IMPLEMENTACAO.md
│   ├── 16-CASOS-DE-USO-BACKEND.md
│   └── INDEX.md
├── src/                           # Source code (to be created)
│   ├── engines/                   # 7 recursive thinking engines
│   ├── routers/                   # HTTP + WebSocket routes
│   ├── providers/                 # LLM integrations
│   ├── models/                    # Database models
│   ├── services/                  # Business logic
│   └── utils/                     # Helpers & formatters
├── tests/                         # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── migrations/                    # Alembic database migrations
├── k8s/                          # Kubernetes manifests
├── main.py                       # FastAPI application entry
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image
├── docker-compose.yml           # Local development stack
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
COHERE_API_KEY=...

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/prompt_boost
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Monitoring
ENABLE_PROMETHEUS=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
```

---

## 🚀 API Endpoints

### Core Recursion API

**Execute Recursion**
```bash
POST /recursion/execute
Content-Type: application/json
Authorization: Bearer {token}

{
  "prompt": "Your prompt here",
  "technique": "tree_of_thoughts",
  "max_iterations": 5,
  "temperature": 0.7,
  "config": {
    "beam_width": 3
  }
}

# Response
{
  "session_id": "sess_12345",
  "final_answer": "...",
  "quality_score": 0.87,
  "iterations": 4,
  "tokens_used": 8942,
  "rer_metric": 0.92
}
```

**Get Session Results**
```bash
GET /recursion/results/{session_id}
Authorization: Bearer {token}
```

**Stream Results via WebSocket**
```javascript
ws://localhost:8000/ws/recursion/{session_id}
```

### Health & Status
```bash
GET /health
GET /stats
GET /docs  # Interactive API documentation
```

See [docs/13-API-REFERENCE.md](docs/13-API-REFERENCE.md) for complete endpoint specification.

---

## 🧪 Testing

### Run All Tests
```bash
# Unit tests
pytest tests/unit/ -v --cov=src --cov-report=html

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v -m e2e

# Load tests (with Locust)
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

See [docs/14-TESTING-STRATEGY.md](docs/14-TESTING-STRATEGY.md) for testing strategy.

---

## 📊 Performance Metrics

### Key Metrics
- **Recursion Efficiency Ratio (RER)**: Quality improvement / tokens used
- **Latency**: P50 < 5s, P99 < 30s (typical)
- **Throughput**: 100+ req/s per instance
- **Token Usage**: ~2K-10K tokens per recursion (depends on technique)

### Monitoring

Prometheus metrics available at `http://localhost:9090`

Grafana dashboards at `http://localhost:3000`

Key dashboards:
- Recursion metrics (executions, quality scores)
- Engine performance (latency per technique)
- Provider costs (by model, by user)
- System health (CPU, memory, database)

See [docs/11-PERFORMANCE-MONITORING.md](docs/11-PERFORMANCE-MONITORING.md) for setup.

---

## 🐳 Docker

### Build Image
```bash
docker build -t prompt-boost-backend:v2.0.0 .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  prompt-boost-backend:v2.0.0
```

### Multi-stage Build
```bash
# Development
docker build --target development -t prompt-boost-backend:dev .

# Production
docker build --target production -t prompt-boost-backend:latest .
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
kubectl version --client

# Create namespace
kubectl create namespace prompt-boost

# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=OPENAI_API_KEY="..." \
  -n prompt-boost
```

### Deploy
```bash
# Apply manifests
kubectl apply -f k8s/ -n prompt-boost

# View deployment
kubectl get pods -n prompt-boost

# Access service
kubectl port-forward svc/backend 8000:8000 -n prompt-boost
```

See [docs/12-DEPLOYMENT.md](docs/12-DEPLOYMENT.md) for complete Kubernetes setup.

---

## 🔄 CI/CD Pipeline

GitHub Actions automatically:
1. Runs tests on every push
2. Builds Docker image on release
3. Deploys to staging on pull request merge
4. Deploys to production on tag push

Pipeline status: See `.github/workflows/`

---

## 📈 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [x] Project setup
- [x] Database schema
- [ ] Core API endpoints

### Phase 2: Engines (Week 3-4)
- [ ] Implement 7 recursive engines
- [ ] Engine testing

### Phase 3: Integration (Week 5-6)
- [ ] LLM provider integration
- [ ] WebSocket streaming
- [ ] API completion

### Phase 4: Deployment (Week 7-8)
- [ ] Monitoring setup
- [ ] Kubernetes deployment
- [ ] Production hardening

See [docs/15-GUIA-IMPLEMENTACAO.md](docs/15-GUIA-IMPLEMENTACAO.md) for detailed roadmap.

---

## 🐛 Troubleshooting

### Common Issues

**Port 8000 already in use**
```bash
lsof -i :8000
kill -9 <PID>
```

**Database connection failed**
```bash
# Check PostgreSQL is running
psql -U postgres -h localhost

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**LLM API errors**
```bash
# Check API keys
echo $OPENAI_API_KEY

# Test provider connection
python -c "from app.providers import ProviderManager; pm = ProviderManager(); pm.test_openai()"
```

**WebSocket connection refused**
```bash
# Ensure FastAPI is running
curl http://localhost:8000/health

# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/test
```

### Logs
```bash
# Development
tail -f app.log

# Docker
docker logs -f backend-container

# Kubernetes
kubectl logs -f deployment/backend -n prompt-boost
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes following [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- Python: PEP 8, type hints required
- Documentation: Docstrings for all public functions
- Tests: >80% coverage required
- Format: `black`, `isort`, `flake8`

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📧 Support

- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@prompt-boost.dev

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Kubernetes](https://kubernetes.io/)

---

**Version**: 2.0.0  
**Last Updated**: 2025-04-10  
**Status**: Development 🚧

