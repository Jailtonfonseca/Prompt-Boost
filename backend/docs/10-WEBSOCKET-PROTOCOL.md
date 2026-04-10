# 10 - WebSocket Protocol & Real-Time Communication

## 🎯 Objetivo

Documentar o protocolo **WebSocket** para comunicação em tempo real entre cliente e servidor. Permite:
- Streaming de raciocínio progressivo
- Updates em tempo real de iterações
- Cancelamento de execuções
- Feedback interativo
- Reconexão automática

---

## 📐 Arquitetura WebSocket

```
                    CLIENT
                      |
                      | WebSocket (ws://)
                      |
          ┌───────────┴───────────┐
          |                       |
      CONNECT              MESSAGE LOOP
          |                       |
      handshake           ┌───────┴──────────┐
          |               |                  |
          |           SEND                 RECEIVE
          |           (cmd)                (event)
          |             |                    |
          └─────────────┼────────────────────┘
                        |
                    (buffered)
                        |
                        ↓
                      SERVER
              ┌─────────────────────┐
              │ RecursionRouter     │
              │ + Thread Pool       │
              │ + Cache             │
              └─────────────────────┘
                        |
              ┌─────────┴──────────┐
              ↓                    ↓
          Engine             Broadcast
         Execution          to Clients
```

---

## 🔌 Message Types

```python
from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum
import json

class MessageType(Enum):
    """Tipos de mensagem WebSocket."""
    # Client → Server
    EXECUTE = "execute"                # Iniciar execução
    CANCEL = "cancel"                  # Cancelar execução
    SUBSCRIBE = "subscribe"            # Se inscrever em updates
    UNSUBSCRIBE = "unsubscribe"        # Remover inscrição
    PING = "ping"                      # Keep-alive
    
    # Server → Client
    PONG = "pong"                      # Keep-alive resposta
    EXECUTION_STARTED = "execution_started"
    ITERATION_UPDATE = "iteration_update"
    VERIFICATION_UPDATE = "verification_update"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    ERROR = "error"
    STATUS = "status"

@dataclass
class WebSocketMessage:
    """Mensagem WebSocket padrão."""
    type: MessageType
    session_id: str
    timestamp: str
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        """Converte para JSON."""
        return json.dumps({
            'type': self.type.value,
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'payload': self.payload
        })
    
    @classmethod
    def from_json(cls, data: str):
        """Cria a partir de JSON."""
        parsed = json.loads(data)
        return cls(
            type=MessageType(parsed['type']),
            session_id=parsed['session_id'],
            timestamp=parsed['timestamp'],
            payload=parsed['payload']
        )
```

### Message Payloads

```python
# EXECUTE: Client → Server
{
    "type": "execute",
    "session_id": "sess_123",
    "timestamp": "2025-04-10T14:30:00Z",
    "payload": {
        "prompt": "Resolver problema de N-queens",
        "technique": "tree_of_thoughts",
        "max_iterations": 5,
        "temperature": 0.7,
        "stream": true
    }
}

# ITERATION_UPDATE: Server → Client
{
    "type": "iteration_update",
    "session_id": "sess_123",
    "timestamp": "2025-04-10T14:30:05Z",
    "payload": {
        "iteration": 1,
        "candidates": [
            {"id": "c1", "content": "...", "score": 0.8},
            {"id": "c2", "content": "...", "score": 0.6}
        ],
        "selected": "c1",
        "tokens_used": 450,
        "progress": 0.2
    }
}

# EXECUTION_COMPLETED: Server → Client
{
    "type": "execution_completed",
    "session_id": "sess_123",
    "timestamp": "2025-04-10T14:30:15Z",
    "payload": {
        "final_answer": "Solução encontrada...",
        "quality_score": 0.95,
        "tokens_used": 2450,
        "cost_usd": 0.042,
        "execution_time_ms": 15000,
        "iterations": 4
    }
}

# VERIFICATION_UPDATE: Server → Client
{
    "type": "verification_update",
    "session_id": "sess_123",
    "timestamp": "2025-04-10T14:30:10Z",
    "payload": {
        "verification_type": "logical_consistency",
        "status": "pass",
        "alignment_score": 0.92,
        "checks": [
            {"type": "contradiction", "passed": true, "confidence": 0.95},
            {"type": "relevance", "passed": true, "confidence": 0.88}
        ]
    }
}
```

---

## 🔧 Implementação FastAPI + WebSockets

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Set
import asyncio
import json
from datetime import datetime

app = FastAPI()

class ConnectionManager:
    """Gerencia conexões WebSocket e broadcast."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.session_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Aceita e registra nova conexão."""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        print(f"Client connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove conexão."""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"Client disconnected from session {session_id}")
    
    async def broadcast(self, session_id: str, message: WebSocketMessage):
        """Envia mensagem para todos clientes de uma sessão."""
        if session_id not in self.active_connections:
            return
        
        message_json = message.to_json()
        
        # Enviar para todos exceto conexões mortas
        dead_connections = set()
        
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error sending message: {e}")
                dead_connections.add(connection)
        
        # Limpar conexões mortas
        for conn in dead_connections:
            self.disconnect(conn, session_id)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Endpoint WebSocket para raciocínio recursivo."""
    
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_text()
            message = WebSocketMessage.from_json(data)
            
            print(f"[{session_id}] Received {message.type.value}")
            
            # Processar tipo de mensagem
            if message.type == MessageType.EXECUTE:
                # Iniciar execução em background
                task = asyncio.create_task(
                    execute_recursion(
                        session_id,
                        message.payload,
                        manager
                    )
                )
                manager.session_tasks[session_id] = task
            
            elif message.type == MessageType.CANCEL:
                # Cancelar execução
                if session_id in manager.session_tasks:
                    manager.session_tasks[session_id].cancel()
                    await manager.broadcast(
                        session_id,
                        WebSocketMessage(
                            type=MessageType.EXECUTION_FAILED,
                            session_id=session_id,
                            timestamp=datetime.utcnow().isoformat(),
                            payload={'reason': 'Cancelled by user'}
                        )
                    )
            
            elif message.type == MessageType.PING:
                # Keep-alive
                await websocket.send_text(
                    WebSocketMessage(
                        type=MessageType.PONG,
                        session_id=session_id,
                        timestamp=datetime.utcnow().isoformat(),
                        payload={}
                    ).to_json()
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        print(f"Client disconnected from {session_id}")
    
    except asyncio.CancelledError:
        manager.disconnect(websocket, session_id)

async def execute_recursion(
    session_id: str,
    payload: Dict,
    manager: ConnectionManager
):
    """Executa raciocínio recursivo e envia updates."""
    
    from app.services.recursion_router import RecursionRouter
    from datetime import datetime
    
    try:
        router = RecursionRouter()
        
        # Enviar started
        await manager.broadcast(
            session_id,
            WebSocketMessage(
                type=MessageType.EXECUTION_STARTED,
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat(),
                payload={'message': 'Iniciando execução...'}
            )
        )
        
        # Executar com callback para updates
        async def iteration_callback(iteration_data):
            await manager.broadcast(
                session_id,
                WebSocketMessage(
                    type=MessageType.ITERATION_UPDATE,
                    session_id=session_id,
                    timestamp=datetime.utcnow().isoformat(),
                    payload=iteration_data
                )
            )
        
        # Chamar router
        result = await router.execute(
            prompt=payload['prompt'],
            technique=payload['technique'],
            max_iterations=payload.get('max_iterations', 5),
            callback=iteration_callback if payload.get('stream') else None
        )
        
        # Enviar resultado final
        await manager.broadcast(
            session_id,
            WebSocketMessage(
                type=MessageType.EXECUTION_COMPLETED,
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat(),
                payload={
                    'final_answer': result.final_answer,
                    'quality_score': result.quality_score,
                    'tokens_used': result.tokens_total,
                    'execution_time_ms': result.metadata.get('execution_time_ms', 0)
                }
            )
        )
    
    except Exception as e:
        await manager.broadcast(
            session_id,
            WebSocketMessage(
                type=MessageType.EXECUTION_FAILED,
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat(),
                payload={'error': str(e)}
            )
        )
```

---

## 📊 Exemplo Prático: Cliente JavaScript

```javascript
// Cliente WebSocket em JavaScript
class RecursionClient {
    constructor(serverUrl = 'ws://localhost:8000') {
        this.serverUrl = serverUrl;
        this.ws = null;
        this.sessionId = null;
        this.listeners = {};
    }
    
    async connect(sessionId) {
        this.sessionId = sessionId;
        
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(`${this.serverUrl}/ws/${sessionId}`);
                
                this.ws.onopen = () => {
                    console.log(`Connected to session ${sessionId}`);
                    resolve();
                };
                
                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this._handleMessage(message);
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };
                
                this.ws.onclose = () => {
                    console.log('Disconnected');
                };
            } catch (e) {
                reject(e);
            }
        });
    }
    
    execute(prompt, technique = 'self_refine', options = {}) {
        const message = {
            type: 'execute',
            session_id: this.sessionId,
            timestamp: new Date().toISOString(),
            payload: {
                prompt,
                technique,
                stream: true,
                ...options
            }
        };
        
        this.ws.send(JSON.stringify(message));
    }
    
    cancel() {
        const message = {
            type: 'cancel',
            session_id: this.sessionId,
            timestamp: new Date().toISOString(),
            payload: {}
        };
        
        this.ws.send(JSON.stringify(message));
    }
    
    on(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        this.listeners[eventType].push(callback);
    }
    
    _handleMessage(message) {
        console.log(`Event: ${message.type}`, message.payload);
        
        if (this.listeners[message.type]) {
            this.listeners[message.type].forEach(callback => {
                callback(message.payload);
            });
        }
    }
}

// Uso
const client = new RecursionClient();

client.on('iteration_update', (data) => {
    console.log(`Iteração ${data.iteration}:`);
    console.log(`  Candidatos: ${data.candidates.length}`);
    console.log(`  Tokens: ${data.tokens_used}`);
    updateProgressBar(data.progress);
});

client.on('execution_completed', (data) => {
    console.log('Resultado:', data.final_answer);
    console.log(`Score: ${data.quality_score}`);
});

client.on('execution_failed', (data) => {
    console.error('Erro:', data.error);
});

// Conectar e executar
await client.connect('sess_123');
client.execute(
    'Resolver problema X',
    'mcts',
    { max_iterations: 10 }
);
```

---

## ✅ Checklist de Implementação

- [ ] Definir MessageType enum e estrutura WebSocketMessage
- [ ] Implementar ConnectionManager com broadcast
- [ ] Criar endpoint FastAPI /ws/{session_id}
- [ ] Implementar execute_recursion com callbacks
- [ ] Adicionar keep-alive (PING/PONG)
- [ ] Implementar cancel handling
- [ ] Adicionar reconnection logic no cliente
- [ ] Implementar subscription management
- [ ] Adicionar error handling e timeouts
- [ ] Testar com múltiplas conexões simultâneas
- [ ] Implementar rate limiting por conexão
- [ ] Adicionar logging de eventos
- [ ] Documentar protocolo de handshake

---

## 🔗 Referências Cruzadas

- **11-PERFORMANCE-MONITORING.md**: Monitorar conexões ativas
- **13-API-REFERENCE.md**: Protocolo detalhado
- **14-TESTING-STRATEGY.md**: E2E com WebSockets

---

**Documento criado**: 2025
**Versão**: 1.0
