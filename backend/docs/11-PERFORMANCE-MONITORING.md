# 11 - Performance Monitoring, Metrics & Observability

## 🎯 Objetivo

Documentar **monitoramento de performance**, **coleta de métricas** e **observabilidade** do backend usando Prometheus, Grafana, e OpenTelemetry. Covers:
- Métricas de execução (latência, throughput)
- Custos LLM (tokens, USD)
- Performance de database
- Health checks e alerts
- Distributed tracing

---

## 📊 Métricas Principais

```python
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# Contadores
recursion_executions_total = Counter(
    'recursion_executions_total',
    'Total de execuções',
    ['technique', 'status']
)

# Latências (em segundos)
recursion_execution_time = Histogram(
    'recursion_execution_seconds',
    'Tempo de execução em segundos',
    ['technique'],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

# Tokens usados
tokens_used = Summary(
    'tokens_used',
    'Tokens utilizados por execução',
    ['provider', 'model']
)

# Custos
cost_usd = Summary(
    'recursion_cost_usd',
    'Custo em USD por execução',
    ['provider']
)

# Gauge: valor que sobe/desce
active_sessions = Gauge(
    'active_sessions',
    'Número de sessões ativas',
    ['technique']
)

# Exemplo de uso
def record_execution(technique: str, provider: str, tokens: int, cost: float, duration: float, success: bool):
    """Registra métrica de execução."""
    status = 'success' if success else 'failed'
    
    recursion_executions_total.labels(
        technique=technique,
        status=status
    ).inc()
    
    recursion_execution_time.labels(technique=technique).observe(duration)
    tokens_used.labels(provider=provider, model='gpt-4').observe(tokens)
    cost_usd.labels(provider=provider).observe(cost)
```

---

## 🔍 Distributed Tracing

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configurar Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Usar traces
def execute_engine(prompt, technique):
    """Executa engine com tracing."""
    
    with tracer.start_as_current_span("execute_engine") as span:
        span.set_attribute("technique", technique)
        span.set_attribute("prompt_length", len(prompt))
        
        # Iterações
        for i in range(5):
            with tracer.start_as_current_span("iteration") as iter_span:
                iter_span.set_attribute("iteration", i)
                
                # Gerar candidatos
                with tracer.start_as_current_span("generate_candidates"):
                    candidates = generate(prompt)
                
                # Avaliar
                with tracer.start_as_current_span("evaluate"):
                    scores = evaluate(candidates)
```

---

## 🏥 Health Checks

```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/health")
async def health():
    """Health check básico."""
    return {"status": "healthy"}

@router.get("/health/deep")
async def deep_health():
    """Verificação completa de dependências."""
    checks = {}
    
    # Database
    try:
        db.execute("SELECT 1")
        checks['database'] = 'healthy'
    except:
        checks['database'] = 'unhealthy'
    
    # LLM Providers
    for provider_type, provider in manager.providers.items():
        try:
            # Testar chamada rápida
            provider.call("test", model="gpt-3.5-turbo", max_tokens=10)
            checks[f'provider_{provider_type}'] = 'healthy'
        except:
            checks[f'provider_{provider_type}'] = 'unhealthy'
    
    # Cache
    try:
        cache.get("health_check")
        checks['cache'] = 'healthy'
    except:
        checks['cache'] = 'unhealthy'
    
    overall = "healthy" if all(v == 'healthy' for v in checks.values()) else "unhealthy"
    
    return {
        "status": overall,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics")
async def metrics():
    """Retorna métricas Prometheus."""
    from prometheus_client import generate_latest
    return generate_latest()
```

---

## 📈 Dashboard Grafana

```json
{
  "dashboard": {
    "title": "Prompt-Boost v2.0",
    "panels": [
      {
        "title": "Execuções por Técnica",
        "targets": [
          {
            "expr": "rate(recursion_executions_total[5m])"
          }
        ]
      },
      {
        "title": "Latência Média (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, recursion_execution_seconds)"
          }
        ]
      },
      {
        "title": "Custo Total por Dia",
        "targets": [
          {
            "expr": "sum(rate(recursion_cost_usd[24h]))"
          }
        ]
      },
      {
        "title": "Taxa de Sucesso",
        "targets": [
          {
            "expr": "recursion_executions_total{status='success'} / recursion_executions_total"
          }
        ]
      }
    ]
  }
}
```

---

## 📍 Logging Estruturado

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Logger com output JSON estruturado."""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **context):
        """Log estruturado."""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.upper(),
            'message': message,
            **context
        }
        
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(entry)
        )

logger = StructuredLogger(__name__)

# Uso
def execute_recursion(session_id, prompt, technique):
    logger.log('info', 'Starting execution', 
        session_id=session_id,
        technique=technique,
        prompt_length=len(prompt)
    )
    
    try:
        result = run_engine(prompt, technique)
        logger.log('info', 'Execution completed',
            session_id=session_id,
            quality_score=result.quality_score,
            tokens_used=result.tokens_total
        )
    except Exception as e:
        logger.log('error', 'Execution failed',
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
```

---

## ✅ Checklist

- [ ] Configurar Prometheus com scrape interval
- [ ] Adicionar métricas principais (execuções, latência, custo)
- [ ] Configurar Jaeger para tracing distribuído
- [ ] Implementar health checks
- [ ] Criar dashboard Grafana
- [ ] Adicionar logging estruturado
- [ ] Configurar alertas (ex: alta latência)
- [ ] Implementar SLIs/SLOs
- [ ] Adicionar profiling (py-spy)

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
