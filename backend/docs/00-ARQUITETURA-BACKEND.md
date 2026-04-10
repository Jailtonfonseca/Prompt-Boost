# 00 - Arquitetura Backend do Prompt-Boost v2.0

## 🎯 Visão Geral

O backend do Prompt-Boost v2.0 é um **sistema de raciocínio recursivo** que permite melhorar prompts usando 7 técnicas LLM avançadas, com **streaming em tempo real**, **múltiplos providers LLM**, e **verificação formal**.

### Princípios Arquiteturais
- **Modularidade**: Cada técnica é um engine independente
- **Extensibilidade**: Fácil adicionar novos engines ou providers
- **Escalabilidade**: WebSocket streaming + async/await
- **Resiliência**: Retry logic, fallback providers, error recovery
- **Observabilidade**: Logging, metrics, tracing

---

## 🏗️ Arquitetura de Componentes

### Visão Geral (Diagrama em Camadas)

```
┌─────────────────────────────────────────────────────────────┐
│ FAST API LAYER (main.py)                                   │
├─────────────────────────────────────────────────────────────┤
│  POST /api/improve-prompt-recursive                         │
│  WS  /ws/recursive                                          │
│  GET /health, /metrics                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ ROUTER LAYER (services/recursion_router.py)               │
├─────────────────────────────────────────────────────────────┤
│  RecursionRouter (Dispatcher)                               │
│  ├─ Route by technique                                      │
│  ├─ Validate config                                         │
│  └─ Stream results to WebSocket                             │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│ ENGINE LAYER (engines/)                                     │
├─────────────────────────────────────────────────────────────┤
│ RecursiveThinkingEngine (Base Class)                        │
│  ├─ SelfRefineEngine        (Self-Refine + Reflexion)      │
│  ├─ TreeOfThoughtsEngine    (ToT + pruning)                 │
│  ├─ GraphOfThoughtsEngine   (GoT + DAG)                     │
│  ├─ MCTSEngine              (Monte Carlo Tree Search)        │
│  ├─ DebateEngine            (Multi-Agent)                   │
│  ├─ AlignmentEngine         (Neural + Symbolic)             │
│  └─ AutoFormalEngine        (NL → Lean4)                    │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│ PROVIDER LAYER (providers/)                                 │
├─────────────────────────────────────────────────────────────┤
│ LLMProvider (Base)                                          │
│  ├─ OpenAIProvider (GPT-4, o1, etc)                        │
│  ├─ AnthropicProvider (Claude)                              │
│  └─ GeminiProvider (Google)                                 │
└────────────┬──────────────────────────────────────────────────┘
             │
┌────────────▼──────────────────────────────────────────────────┐
│ DATA LAYER                                                  │
├─────────────────────────────────────────────────────────────┤
│ Database (SQLAlchemy + PostgreSQL)                          │
│ ├─ Execution (tracking)                                     │
│ ├─ Iteration (each step)                                    │
│ └─ Result (final output)                                    │
│                                                             │
│ Cache (Redis) [Optional]                                    │
│ ├─ Results cache                                            │
│ └─ Embedding cache                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 RecursionRouter: Dispatcher Central

O **RecursionRouter** é o coração da arquitetura. Ele:
1. Recebe request com prompt + técnica
2. Valida configuração
3. Instantia o engine correto
4. Executa com streaming
5. Persiste resultados

### Implementação (Pseudocódigo)

```python
class RecursionRouter:
    """Central dispatcher para técnicas de raciocínio"""
    
    def __init__(self, db_session, provider_factory):
        self.db = db_session
        self.providers = provider_factory
        self.engines = {
            'self_refine': SelfRefineEngine,
            'tot': TreeOfThoughtsEngine,
            'got': GraphOfThoughtsEngine,
            'mcts': MCTSEngine,
            'debate': DebateEngine,
            'alignment': AlignmentEngine,
            'autoformal': AutoFormalEngine
        }
    
    async def execute(self, request: ImprovePromptRequest, ws=None):
        """
        Executa técnica com streaming
        
        Flow:
        1. Validate request
        2. Create execution record
        3. Instantiate engine
        4. Stream results
        5. Persist to database
        """
        execution_id = str(uuid.uuid4())
        
        try:
            # Validação
            self._validate_config(request.config)
            
            # Database record
            execution = await self.db.create_execution(
                id=execution_id,
                technique=request.technique,
                original_prompt=request.prompt,
                config=request.config
            )
            
            # Instantiate engine
            engine_class = self.engines.get(request.technique)
            engine = engine_class(
                provider=self.providers.create(request.config.provider),
                config=request.config
            )
            
            # Execute with streaming
            async for result in engine.run(request.prompt):
                # Stream to WebSocket
                if ws:
                    await ws.send_json(result)
                
                # Update database
                if result['type'] == 'iteration':
                    await self.db.create_iteration(
                        execution_id=execution_id,
                        data=result
                    )
            
            # Finalize
            await self.db.complete_execution(execution_id, result)
            
        except Exception as e:
            await self.db.mark_failed(execution_id, str(e))
            raise
```

---

## 📊 Request-Response Flow

### HTTP (REST - Simples)

```
Client                          Server

POST /api/improve-prompt-recursive
{
  "prompt": "...",
  "technique": "self_refine",
  "config": {...}
}
        │
        ├─→ Validate
        ├─→ Create execution record
        ├─→ Run engine (BLOCKING até conclusão)
        │
        ←── RecursionResult (completo)
{
  "final_answer": "...",
  "iterations": [...],
  "tokens_total": 4200,
  "time_ms": 15000,
  ...
}
```

### WebSocket (Real-time - Recomendado)

```
Client                          Server

WS /ws/recursive
│
├─→ CONNECT
│   ←── {"type": "connected", "session_id": "..."}
│
├─→ {"action": "start_reasoning", "prompt": "...", ...}
│   ├─→ {"type": "status", "status": "thinking", "iteration": 1/3}
│   ├─→ {"type": "iteration", "iteration_number": 1, ...}
│   ├─→ {"type": "metrics", "tokens": 320/10000, ...}
│   ├─→ {"type": "status", "status": "thinking", "iteration": 2/3}
│   ├─→ {"type": "iteration", "iteration_number": 2, ...}
│   ├─→ {"type": "metrics", "tokens": 890/10000, ...}
│   ├─→ {"type": "complete", "final_answer": "..."}
│   ←── (conexão fecha)
```

---

## 🧠 Base Engine: Padrão Genérico

Todos os 7 engines herdam de `RecursiveThinkingEngine` que define o padrão:

### Estado e Ciclo

```
INITIALIZE (config, provider)
    ↓
EXECUTE LOOP:
  ├─ GENERATE (criar N candidatos)
  ├─ EVALUATE (avaliar cada um)
  ├─ FEEDBACK (crítica/contexto)
  ├─ REFINE (incorporar feedback)
  ├─ CHECK TERMINATION (parar?)
  └─ → próxima iteração ou finalizar
    ↓
FINALIZE (best solution)
    ↓
YIELD RESULT (RecursionResult)
```

### Classes de Dados

```python
# Estado compartilhado
class RecursionState:
    execution_id: str
    technique: str
    original_prompt: str
    current_prompt: str
    iteration: int
    tokens_used: int
    all_iterations: List[IterationRecord]
    best_solution: Optional[Dict]
    memory_pool: Dict  # Episodic memory

# Um passo
class IterationRecord:
    iteration_number: int
    timestamp: datetime
    generated_candidates: List[str]
    evaluation_scores: List[float]
    selected_best: str
    feedback_from_critic: str
    tokens_this_iteration: int
    extra_data: Dict

# Configuração
class RecursionConfig:
    technique: str
    provider: str
    model: str
    temperature: float
    max_iterations: int
    max_tokens_total: int
    max_time_ms: int
    extra_params: Dict

# Resultado final
class RecursionResult:
    final_answer: str
    iterations_count: int
    tokens_total: int
    time_total_ms: float
    quality_score: float
    rer_score: float
    all_iterations: List[IterationRecord]
    metadata: Dict
```

---

## 📁 Estrutura de Pastas

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app
│   ├── config.py                        # Pydantic settings
│   ├── models.py                        # Pydantic schemas
│   │
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── base_engine.py               # RecursiveThinkingEngine (abstração)
│   │   ├── self_refine_engine.py        # Self-Refine + Reflexion
│   │   ├── tot_engine.py                # Tree of Thoughts
│   │   ├── got_engine.py                # Graph of Thoughts
│   │   ├── mcts_engine.py               # LLM-MCTS
│   │   ├── debate_engine.py             # Multi-Agent Debate
│   │   ├── alignment_engine.py          # Recursive Alignment
│   │   └── autoformal_engine.py         # AutoFormalization
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── improve.py                   # POST /api/improve-prompt-recursive
│   │   ├── websocket.py                 # WS /ws/recursive
│   │   └── health.py                    # GET /health, /metrics
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                      # LLMProvider (abstração)
│   │   ├── openai_provider.py           # OpenAI (GPT-4, o1, etc)
│   │   ├── anthropic_provider.py        # Claude
│   │   ├── gemini_provider.py           # Google Gemini
│   │   └── provider_factory.py          # Factory pattern
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                    # SQLAlchemy models
│   │   ├── session.py                   # Database connection
│   │   ├── repository.py                # Query logic
│   │   └── migrations.py                # Alembic migrations
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recursion_router.py          # Dispatcher central
│   │   ├── token_counter.py             # Token accounting
│   │   ├── metrics.py                   # Prometheus metrics
│   │   └── llm_service.py               # LLM interactions
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py                # Pydantic validators
│   │   ├── formatters.py                # String formatting
│   │   ├── logging.py                   # Structured logging
│   │   └── constants.py                 # Config constants
│   │
│   └── verifiers/
│       ├── __init__.py
│       ├── lean4_verifier.py            # Lean4 verification
│       └── base_verifier.py             # Verifier interface
│
├── docs/
│   ├── INDEX.md
│   ├── 00-ARQUITETURA-BACKEND.md        # (ESTE ARQUIVO)
│   ├── 01-ENGINES-IMPLEMENTACAO.md
│   ├── 02-SELF-REFINE-ENGINE.md
│   ├── ... (14 mais)
│   └── 16-CASOS-DE-USO-BACKEND.md
│
├── tests/
│   ├── unit/
│   │   ├── test_engines.py
│   │   ├── test_providers.py
│   │   └── test_router.py
│   ├── integration/
│   │   └── test_websocket.py
│   └── e2e/
│       └── test_full_flow.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── .env.example
└── alembic.ini
```

---

## 🔗 Fluxo de Dados Completo

### 1. Cliente (Frontend)

```javascript
// frontend/src/hooks/useRecursiveThinking.js
const ws = new WebSocket('ws://localhost:8000/ws/recursive');
ws.send({
  action: 'start_reasoning',
  prompt: 'Escreva um código...',
  technique: 'self_refine',
  config: {...}
});
```

### 2. WebSocket Handler (Backend)

```python
# backend/src/routers/websocket.py
@app.websocket("/ws/recursive")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    message = await websocket.receive_json()
    # {action: "start_reasoning", prompt: "...", technique: "self_refine", ...}
    
    router = RecursionRouter(db, providers)
    async for result in router.execute(message, ws=websocket):
        await websocket.send_json(result)
```

### 3. Router Dispatcher (Backend)

```python
# backend/src/services/recursion_router.py
async def execute(self, request, ws):
    engine = self.engines[request['technique']](...)
    
    async for iteration_result in engine.run(request['prompt']):
        # Streaming back to frontend
        await ws.send_json(iteration_result)
```

### 4. Engine (Específica)

```python
# backend/src/engines/self_refine_engine.py
async def run(self, prompt):
    for iteration in range(self.config.max_iterations):
        # GENERATE
        candidates = await self.provider.generate(prompt, n=3)
        
        # EVALUATE
        scores = await self._evaluate_candidates(candidates)
        best = candidates[argmax(scores)]
        
        # FEEDBACK
        feedback = await self.provider.critique(best, prompt)
        
        # YIELD to WebSocket
        yield {
            'type': 'iteration',
            'iteration_number': iteration + 1,
            'candidates': candidates,
            'scores': scores,
            'best': best,
            'feedback': feedback
        }
        
        # REFINE
        prompt = await self._refine_prompt(prompt, feedback)
    
    yield {
        'type': 'complete',
        'final_answer': prompt
    }
```

### 5. LLM Provider

```python
# backend/src/providers/openai_provider.py
async def generate(self, prompt, n=3):
    response = await client.ChatCompletion.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        n=n,
        temperature=self.temperature
    )
    return [choice.message.content for choice in response.choices]
```

### 6. Database Persistence

```python
# backend/src/database/repository.py
async def create_iteration(self, execution_id, data):
    iteration = Iteration(
        execution_id=execution_id,
        iteration_number=data['iteration_number'],
        generated_candidates=data['candidates'],
        evaluation_scores=data['scores'],
        selected_best=data['best'],
        feedback=data['feedback'],
        tokens_this_iteration=data['tokens']
    )
    await self.db.add(iteration)
    await self.db.commit()
```

---

## 🚀 Escalabilidade & Performance

### Async/Await

```python
# Todas operações I/O são async
async def run(self, prompt):
    # Parallelizar avaliação de candidatos
    scores = await asyncio.gather(
        self._score_candidate(c1),
        self._score_candidate(c2),
        self._score_candidate(c3)
    )
```

### Streaming

```python
# Enviar resultados conforme disponível (não aguardar conclusão)
async for iteration in engine.run(prompt):
    await websocket.send_json(iteration)
    # Frontend mostra progresso em TEMPO REAL
```

### Caching

```python
# Cache provider calls
@cache.cached(timeout=3600)
async def get_embeddings(text):
    return await provider.embed(text)
```

### Rate Limiting

```python
# Limitar requisições por usuário
@router.post("/api/improve-prompt-recursive")
@rate_limit(max_requests=10, window_seconds=60)
async def improve_prompt(request):
    ...
```

---

## 🛡️ Tratamento de Erros

### Camadas de Erro

```
Request Validation Error
    ↓
Provider Error (LLM indisponível)
    ├─ Retry com backoff exponencial
    └─ Fallback para outro provider
    ↓
Timeout Error (execução muito lenta)
    ├─ Cancelar iteração
    └─ Retornar resultado parcial
    ↓
Database Error (persistência falhou)
    ├─ Log para análise
    └─ Retornar ao cliente (sem garantia de persistência)
    ↓
Client Error (WebSocket desconectou)
    ├─ Cleanup de recursos
    └─ Salvar state para reconnection
```

---

## 📊 Métricas Coletadas

```python
# Prometheus metrics
recursion_executions_total        # Counter
recursion_iterations_total        # Counter
recursion_tokens_consumed         # Counter
recursion_execution_duration_ms   # Histogram
recursion_quality_score           # Gauge
recursion_rer_score               # Gauge
provider_api_calls                # Counter
provider_api_errors               # Counter
provider_tokens_used              # Counter
provider_cost_usd                 # Gauge
```

---

## ✅ Próximos Passos

1. **Leia**: 01-ENGINES-IMPLEMENTACAO.md (padrão genérico)
2. **Leia**: 02-08-*-ENGINE.md (técnicas específicas)
3. **Leia**: 08-PROVIDERS-E-LLMS.md (LLM integration)
4. **Implemente**: Backend structure + engines
5. **Teste**: Unit tests de cada engine

---

**Referências Cruzadas**:
- Frontend: `/frontend/docs/02-INTEGRACAO-WEBSOCKET.md`
- Engines: `/backend/docs/01-ENGINES-IMPLEMENTACAO.md`
- Providers: `/backend/docs/08-PROVIDERS-E-LLMS.md`
