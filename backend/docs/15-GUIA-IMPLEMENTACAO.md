# 15 - Guia de Implementação: Roadmap 4-Fases

## 🎯 Visão Geral

Guia prático para implementação do Prompt-Boost v2.0 backend em **4 fases**, com timeline, dependências, checkpoints e entregáveis.

---

## 📋 Fases de Implementação

### **FASE 1: Foundation (Semanas 1-2)**
**Objetivo**: Arquitetura base, modelos de dados e estrutura de projeto

#### Semana 1: Arquitetura e Setup
```
Tarefas:
├── 1.1 Criar estrutura de diretórios (backend/src/)
├── 1.2 Configurar FastAPI app e routers
├── 1.3 Setup Docker e docker-compose
├── 1.4 Implementar logging centralizado
├── 1.5 Configurar variáveis de ambiente
└── 1.6 Setup GitHub Actions CI/CD básico

Timeline: 5 dias (segunda a sexta)
Dependências: Nenhuma
Entregáveis:
  - backend/src/main.py com FastAPI app funcional
  - docker-compose.yml com PostgreSQL + Redis
  - Workflows CI/CD rodando
  - Estrutura de logs centralizada
```

**Código Referência** (main.py):
```python
# backend/src/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Logger centralizado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Backend iniciado")
    yield
    logger.info("🛑 Backend encerrado")

app = FastAPI(
    title="Prompt-Boost v2.0 Backend",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Semana 2: Modelos e Database
```
Tarefas:
├── 2.1 Implementar SQLAlchemy Base Models
├── 2.2 Criar models: User, RecursionSession, IterationRecord
├── 2.3 Setup Alembic para migrations
├── 2.4 Implementar ConnectionPool com retry logic
├── 2.5 Criar fixtures pytest para database
└── 2.6 Testar migrations e data persistence

Timeline: 5 dias
Dependências: Fase 1
Entregáveis:
  - backend/src/models/*.py (5+ modelos SQLAlchemy)
  - Migrations Alembic testadas
  - Database inicializa automaticamente em Docker
  - Unit tests para models (90%+ coverage)
```

**Checkpoint 1**: Executar `docker-compose up` e verificar POST /health retorna status

---

### **FASE 2: Core Engines (Semanas 3-4)**
**Objetivo**: Implementar os 7 motores de recursão

#### Semana 3: Base Engine + Self-Refine + ToT/GoT
```
Tarefas:
├── 3.1 Implementar RecursiveThinkingEngine base
├── 3.2 Implementar SelfRefineEngine
├── 3.3 Implementar TreeOfThoughtsEngine
├── 3.4 Implementar GraphOfThoughtsEngine
├── 3.5 Unit tests para cada engine (episodic memory)
└── 3.6 Integração com LLM providers (mock)

Timeline: 5 dias
Dependências: Fase 1-2
Entregáveis:
  - backend/src/engines/base.py (~300 linhas)
  - backend/src/engines/{self_refine,tot,got}.py
  - Todos engines passam em testes
  - Exemplos de execução com output
```

**Código Referência** (base engine com episodic memory):
```python
# backend/src/engines/base.py
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

@dataclass
class RecursionConfig:
    initial_prompt: str
    max_iterations: int = 5
    temperature: float = 0.7
    top_k: int = 5
    
@dataclass
class IterationRecord:
    iteration: int
    state: Dict
    candidates: List[str]
    chosen: str
    quality_score: float
    tokens_used: int
    timestamp: datetime = field(default_factory=datetime.now)

class EpisodicMemory:
    def __init__(self):
        self.successful_patterns: Dict[str, float] = {}
        self.failed_patterns: Dict[str, float] = {}
    
    def add_successful_pattern(self, pattern: str, score: float):
        self.successful_patterns[pattern] = max(
            self.successful_patterns.get(pattern, 0), score
        )
    
    def retrieve_similar(self, pattern: str, top_k: int = 5) -> List[str]:
        # Similarity matching (implementar com embeddings)
        return sorted(
            self.successful_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

class RecursiveThinkingEngine:
    def __init__(self, config: RecursionConfig, provider):
        self.config = config
        self.provider = provider
        self.memory = EpisodicMemory()
        self.iterations: List[IterationRecord] = []
    
    async def execute(self) -> Dict:
        """5-step loop: GENERATE → EVALUATE → FEEDBACK → REFINE → TERMINATE"""
        current_state = self.config.initial_prompt
        
        for iteration in range(self.config.max_iterations):
            # GENERATE
            candidates = await self._generate(current_state)
            
            # EVALUATE
            scores = await self._evaluate(candidates)
            
            # FEEDBACK
            feedback = self._compute_feedback(scores)
            
            # REFINE
            current_state = await self._refine(current_state, feedback)
            
            # TERMINATE CHECK
            if await self._should_terminate(scores, iteration):
                break
            
            # Record iteration
            best_candidate = max(zip(candidates, scores), key=lambda x: x[1])[0]
            self.iterations.append(IterationRecord(
                iteration=iteration,
                state={"current": current_state},
                candidates=candidates,
                chosen=best_candidate,
                quality_score=max(scores),
                tokens_used=100  # estimate
            ))
        
        return {
            "final_answer": current_state,
            "quality_score": max([i.quality_score for i in self.iterations]),
            "iterations": len(self.iterations),
            "tokens_total": sum(i.tokens_used for i in self.iterations)
        }
    
    async def _generate(self, state: str) -> List[str]:
        raise NotImplementedError
    
    async def _evaluate(self, candidates: List[str]) -> List[float]:
        raise NotImplementedError
    
    async def _feedback(self, scores: List[float]) -> str:
        raise NotImplementedError
    
    async def _refine(self, state: str, feedback: str) -> str:
        raise NotImplementedError
    
    async def _should_terminate(self, scores: List[float], iteration: int) -> bool:
        return iteration >= self.config.max_iterations - 1 or max(scores) > 0.95
```

#### Semana 4: MCTS + Debate + Alignment + AutoFormal
```
Tarefas:
├── 4.1 Implementar MCTSEngine (rollout policies)
├── 4.2 Implementar DebateEngine (Pro/Con/Judge)
├── 4.3 Implementar AlignmentEngine (verifiers)
├── 4.4 Implementar AutoFormalEngine (Lean4)
├── 4.5 Tests de stress para cada engine
└── 4.6 Benchmarks e RER metrics

Timeline: 5 dias
Dependências: Semana 3
Entregáveis:
  - backend/src/engines/{mcts,debate,alignment,autoformal}.py
  - Todos 7 engines implementados e testados
  - Performance benchmarks documentados
  - RecursionRouter dispatcher implementado
```

**Checkpoint 2**: Executar `pytest tests/unit/test_engines.py -v --cov` e verificar 90%+ coverage

---

### **FASE 3: Integration & APIs (Semanas 5-6)**
**Objetivo**: Conectar engines com providers, WebSocket, e APIs REST

#### Semana 5: Providers e WebSocket
```
Tarefas:
├── 5.1 Implementar ProviderManager (OpenAI, Anthropic, Gemini, etc)
├── 5.2 Token counting e cost calculation
├── 5.3 Implementar fallback logic entre providers
├── 5.4 Setup WebSocket routing (FastAPI)
├── 5.5 Mensagens de streaming em tempo real
└── 5.6 Integração engines → WebSocket

Timeline: 5 dias
Dependências: Fase 1-2
Entregáveis:
  - backend/src/providers/manager.py
  - WebSocket endpoints funcional
  - Messages fluindo em tempo real
  - Integration tests com mock providers
```

**Código Referência** (WebSocket + streaming):
```python
# backend/src/routers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

@router.websocket("/ws/recursion/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        # Receber config inicial
        data = await websocket.receive_text()
        config = json.loads(data)
        
        # Executar engine com streaming
        async for message in stream_recursion(session_id, config):
            await websocket.send_json(message)
    
    except WebSocketDisconnect:
        print(f"Cliente desconectado: {session_id}")

async def stream_recursion(session_id: str, config: dict):
    """Generator que yields mensagens de cada iteração."""
    from app.services.recursion_router import RecursionRouter
    
    router = RecursionRouter()
    
    async for iteration in router.execute_streaming(config):
        yield {
            "type": "iteration_update",
            "session_id": session_id,
            "iteration": iteration["iteration"],
            "current_best": iteration["current_best"],
            "quality_score": iteration["quality_score"],
            "tokens_used": iteration["tokens_used"]
        }
    
    yield {
        "type": "completion",
        "session_id": session_id,
        "final_answer": iteration["final_answer"],
        "quality_score": iteration["quality_score"],
        "total_iterations": iteration["iterations"]
    }
```

#### Semana 6: APIs REST e RecursionRouter
```
Tarefas:
├── 6.1 Implementar RecursionRouter dispatcher
├── 6.2 Criar endpoints REST: /recursion/execute, /recursion/results
├── 6.3 Implementar rate limiting e authentication
├── 6.4 Setup Prometheus metrics collection
├── 6.5 Integração com database para persistência
└── 6.6 E2E tests (Playwright)

Timeline: 5 dias
Dependências: Semana 5, Fase 1-2
Entregáveis:
  - backend/src/routers/{recursion,health}.py
  - RecursionRouter dispatcher
  - REST API completa com OpenAPI docs
  - E2E tests passando
```

**Checkpoint 3**: Executar `pytest tests/integration/test_api.py -v` e testar POST /recursion/execute com diferentes técnicas

---

### **FASE 4: Deployment & Monitoring (Semanas 7-8)**
**Objetivo**: Production-ready deployment com monitoring e observability

#### Semana 7: Monitoring e Performance
```
Tarefas:
├── 7.1 Setup Prometheus + Grafana
├── 7.2 Distribuir tracing com Jaeger
├── 7.3 Health checks e liveness probes
├── 7.4 Alertas para SLAs
├── 7.5 Load testing com Locust (1000+ users)
└── 7.6 Stress testing e capacity planning

Timeline: 5 dias
Dependências: Fase 3
Entregáveis:
  - Prometheus scraping métricas
  - Grafana dashboards
  - Jaeger tracing distribuído
  - Load test relatório (P99 latency, throughput)
```

#### Semana 8: Deployment Final
```
Tarefas:
├── 8.1 Kubernetes manifests (deployment, service, ingress)
├── 8.2 Docker multi-stage build otimizado
├── 8.3 CI/CD pipeline completo (GitHub Actions)
├── 8.4 Secrets management (Sealed Secrets, HashiCorp Vault)
├── 8.5 Database migrations automáticas
├── 8.6 Documentation e runbooks
└── 8.7 Staging e production deployment

Timeline: 5 dias
Dependências: Fase 1-3, Semana 7
Entregáveis:
  - Kubernetes cluster rodando
  - CI/CD deploying automaticamente
  - Runbooks para troubleshooting
  - Production monitoring ativo
```

**Checkpoint 4**: Executar `kubectl apply -f k8s/` e verificar pods rodando, /health respondendo, métricas em Grafana

---

## 📊 Timeline Consolidada

```
Semana 1-2 (FASE 1)  ████░░░░░░░░░░░░░ Setup e Modelos
Semana 3-4 (FASE 2)  ░░████████░░░░░░░░ Core Engines (7x)
Semana 5-6 (FASE 3)  ░░░░░░░░████████░░ Integration & APIs
Semana 7-8 (FASE 4)  ░░░░░░░░░░░░░░████ Deployment & Monitoring

Total: 8 semanas (2 meses)
```

---

## 🔗 Dependências Entre Fases

```
FASE 1 (Setup)
    ↓
FASE 2 (Engines) ─── requer ─→ FASE 1
    ↓
FASE 3 (APIs)   ─── requer ─→ FASE 1, 2
    ↓
FASE 4 (Deploy) ─── requer ─→ FASE 1, 2, 3
```

**Paralelização Possível**:
- Semana 1 + 2: FASE 1 em paralelo com setup inicial
- Semana 3: FASE 2 começa assim que FASE 1 completa
- Semana 5: FASE 3 começa assim que FASE 2 está 50% completa

---

## ✅ Checkpoints e Validação

| Checkpoint | Timing | Validação | Status |
|-----------|--------|-----------|--------|
| **1** | Fim Semana 2 | `docker-compose up` + `/health` | 🔲 |
| **2** | Fim Semana 4 | `pytest tests/unit/ --cov=90%` | 🔲 |
| **3** | Fim Semana 6 | `pytest tests/integration/ --e2e` | 🔲 |
| **4** | Fim Semana 8 | `kubectl get pods` + Grafana ativo | 🔲 |

---

## 🎁 Documentação de Referência

Para cada fase, consultar:
- **FASE 1**: [00-ARQUITETURA-BACKEND.md](00-ARQUITETURA-BACKEND.md)
- **FASE 2**: [01-ENGINES-IMPLEMENTACAO.md](01-ENGINES-IMPLEMENTACAO.md), [02-07 Engine Docs](02-SELF-REFINE-ENGINE.md)
- **FASE 3**: [08-PROVIDERS-E-LLMS.md](08-PROVIDERS-E-LLMS.md), [10-WEBSOCKET-PROTOCOL.md](10-WEBSOCKET-PROTOCOL.md), [13-API-REFERENCE.md](13-API-REFERENCE.md)
- **FASE 4**: [11-PERFORMANCE-MONITORING.md](11-PERFORMANCE-MONITORING.md), [12-DEPLOYMENT.md](12-DEPLOYMENT.md), [14-TESTING-STRATEGY.md](14-TESTING-STRATEGY.md)

---

## 🚀 Quick Start

1. **Clonar repo**: `git clone && cd Prompt-Boost`
2. **FASE 1**: `cd backend && docker-compose up`
3. **FASE 2**: `cd src/engines && python -m pytest`
4. **FASE 3**: `curl -X POST http://localhost:8000/recursion/execute`
5. **FASE 4**: `kubectl apply -f k8s/ && open http://localhost:3000`

---

## 📚 Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/best-practices/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

---

**Última atualização**: 2025
**Versão**: 2.0.0
**Status**: Em Implementação

