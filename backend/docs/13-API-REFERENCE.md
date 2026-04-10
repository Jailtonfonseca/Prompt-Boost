# 13 - API Reference & OpenAPI Specification

## 🎯 Objetivo

Documentar **API REST completa** com OpenAPI 3.0 specification, incluindo todos endpoints, request/response models, e exemplos.

---

## 📋 Endpoints Principais

### POST /recursion/execute

Inicia uma nova execução recursiva.

**Request**:
```json
{
  "prompt": "Resolver problema N-queens com N=8",
  "technique": "tree_of_thoughts",
  "max_iterations": 5,
  "temperature": 0.7,
  "stream": true,
  "provider": "openai"
}
```

**Response (200)**:
```json
{
  "session_id": "sess_550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "created_at": "2025-04-10T14:30:00Z"
}
```

### GET /recursion/session/{session_id}

Obtém status e resultado de uma sessão.

**Response (200)**:
```json
{
  "id": "sess_...",
  "status": "completed",
  "technique": "tree_of_thoughts",
  "final_answer": "A solução é...",
  "quality_score": 0.95,
  "tokens_used": 2450,
  "cost_usd": 0.042,
  "created_at": "2025-04-10T14:30:00Z",
  "completed_at": "2025-04-10T14:30:15Z"
}
```

### POST /verify

Verifica uma resposta com alignment engine.

**Request**:
```json
{
  "content": "Resposta para verificar",
  "original_question": "Pergunta original"
}
```

**Response (200)**:
```json
{
  "status": "pass",
  "alignment_score": 0.92,
  "checks": [
    {
      "type": "logical_consistency",
      "passed": true,
      "confidence": 0.95
    },
    {
      "type": "safety",
      "passed": true,
      "confidence": 0.88
    }
  ]
}
```

### POST /formalize

Formaliza declaração em Lean4.

**Request**:
```json
{
  "statement": "Para todo natural n, n + 0 = n"
}
```

**Response (200)**:
```json
{
  "lean4_code": "theorem nat_add_zero (n : Nat) : n + 0 = n := by\n  induction n with\n  | zero => rfl\n  | succ n ih => simp [ih]",
  "verification_status": "valid",
  "confidence": 0.95
}
```

### GET /providers

Lista providers disponíveis.

**Response (200)**:
```json
{
  "providers": [
    {
      "type": "openai",
      "enabled": true,
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "priority": 0
    },
    {
      "type": "anthropic",
      "enabled": true,
      "models": ["claude-3-opus-20240229"],
      "priority": 1
    }
  ]
}
```

### GET /stats

Estatísticas de uso do usuário.

**Response (200)**:
```json
{
  "total_sessions": 42,
  "total_tokens": 125450,
  "total_cost_usd": 1.87,
  "avg_quality_score": 0.87,
  "by_technique": {
    "tree_of_thoughts": 15,
    "self_refine": 20,
    "mcts": 7
  }
}
```

### WebSocket /ws/{session_id}

Conexão WebSocket para streaming em tempo real.

**Messages**: Confira 10-WEBSOCKET-PROTOCOL.md

---

## 🔐 Autenticação

Todos endpoints exceto `/health` requerem header `Authorization`:

```
Authorization: Bearer sk-user-key-...
```

---

## 📊 Error Responses

```json
{
  "detail": "Descrição do erro",
  "error_code": "INVALID_TECHNIQUE",
  "timestamp": "2025-04-10T14:30:00Z"
}
```

Códigos de erro:
- `400`: Bad request
- `401`: Unauthorized
- `403`: Forbidden (quota excedida)
- `404`: Not found
- `429`: Rate limited
- `500`: Internal server error

---

## 📝 FastAPI Route Definitions

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="Prompt-Boost v2.0")

# Models
class ExecuteRequest(BaseModel):
    prompt: str
    technique: str
    max_iterations: int = 5
    temperature: float = 0.7
    stream: bool = False
    provider: str = "openai"

class SessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: str

# Dependency
async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    api_key = authorization.split(" ")[1]
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401)
    return user

# Routes
@app.post("/recursion/execute")
async def execute_recursion(
    request: ExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """Inicia execução recursiva."""
    session = RecursionSession(
        user_id=current_user.id,
        initial_prompt=request.prompt,
        technique=TechniqueType(request.technique),
        temperature=request.temperature,
        max_iterations=request.max_iterations
    )
    db.add(session)
    db.commit()
    
    # Enqueue para worker
    queue.enqueue('execute_engine', session.id)
    
    return SessionResponse(
        session_id=session.id,
        status=session.status.value,
        created_at=session.created_at.isoformat()
    )

@app.get("/recursion/session/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtém status de sessão."""
    session = db.query(RecursionSession).filter(
        RecursionSession.id == session_id,
        RecursionSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404)
    
    return {
        "id": session.id,
        "status": session.status.value,
        "final_answer": session.final_answer,
        "quality_score": session.quality_score,
        "tokens_used": session.tokens_used,
        "cost_usd": session.cost_usd
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## ✅ Checklist

- [ ] Definir todos Pydantic models
- [ ] Implementar autenticação por API key
- [ ] Adicionar rate limiting por usuário
- [ ] Gerar OpenAPI spec automaticamente
- [ ] Documentar todos endpoints
- [ ] Criar exemplos de request/response
- [ ] Implementar input validation
- [ ] Adicionar query parameter pagination
- [ ] Implementar error handling
- [ ] Testar todos endpoints

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
