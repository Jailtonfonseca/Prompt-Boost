# 02 - Integração WebSocket & Real-Time Communication

## 🔌 Visão Geral

WebSocket permite comunicação bidirecional em tempo real entre cliente (React frontend) e servidor (Python backend). Para o Prompt-Boost v2.0, isso é crítico para:

1. **Streaming de iterações** em tempo real
2. **Atualização de métricas** conforme processamento ocorre
3. **Cancelamento** de processos em andamento
4. **Reconexão automática** após desconexão

---

## 📡 Arquitetura WebSocket

### Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend (React)                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MainPage.js                                                    │
│      ├─ useWebSocket()                                          │
│      ├─ useStreamingResult()                                    │
│      └─ handleImprovePrompt()                                   │
│          │                                                      │
│          │ ws.send({action: "start_reasoning", ...})            │
│          ▼                                                      │
│  websocketClient.js                                             │
│      ├─ connect(wsUrl)                                          │
│      ├─ send(message)                                           │
│      ├─ on("message", handler)                                  │
│      ├─ close()                                                 │
│      └─ reconnect() [automático]                                │
│                                                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │ WebSocket │            │ Fallback (Polling)
        │ Protocol  │            │
        ▼           ▼            ▼
    ┌─────────────────────────────────┐
    │ Backend (FastAPI)               │
    ├─────────────────────────────────┤
    │ main.py                         │
    │  └─ @app.websocket("/ws/...")   │
    │     ├─ receive(): get message   │
    │     ├─ process: run engine      │
    │     └─ send(): yield updates    │
    │                                 │
    │ RecursionRouter                 │
    │  └─ dispatch to engine          │
    │                                 │
    └─────────────────────────────────┘
```

---

## 📨 Formatos de Mensagem

### Cliente → Servidor

#### Start Request
```json
{
  "action": "start_reasoning",
  "prompt": "Escreva um código que parsea JSON",
  "technique": "self_refine",
  "config": {
    "provider": "openai",
    "model": "gpt-4o",
    "temperature": 0.7,
    "max_iterations": 3,
    "max_tokens_total": 10000,
    "extra_params": {}
  }
}
```

#### Cancel Request
```json
{
  "action": "cancel",
  "execution_id": "uuid-string"
}
```

#### Ping (Keep-Alive)
```json
{
  "action": "ping"
}
```

---

### Servidor → Cliente

#### Status Update
```json
{
  "type": "status",
  "status": "thinking",
  "execution_id": "uuid-string",
  "current_iteration": 1,
  "max_iterations": 3,
  "timestamp": "2026-04-10T12:30:45.123Z"
}
```

#### Iteration Yield (Dados de Uma Iteração)
```json
{
  "type": "iteration",
  "execution_id": "uuid-string",
  "iteration_number": 1,
  "timestamp": "2026-04-10T12:30:47.456Z",
  "generated_candidates": [
    "Um parser é um programa...",
    "Um parser JSON é...",
    "Escreva em Python um parser..."
  ],
  "evaluation_scores": [0.65, 0.72, 0.88],
  "selected_best": "Escreva em Python um parser...",
  "feedback_from_critic": "Bem melhor! Mas falta especificar validação de erros.",
  "tokens_this_iteration": 1200,
  "extra_data": {
    "time_ms": 2340,
    "model_used": "gpt-4o"
  }
}
```

#### Metrics Update (Contadores em Tempo Real)
```json
{
  "type": "metrics",
  "execution_id": "uuid-string",
  "tokens_so_far": 3200,
  "tokens_max": 10000,
  "time_elapsed_ms": 7000,
  "time_max_ms": 120000,
  "current_iteration": 2,
  "max_iterations": 3
}
```

#### Complete (Final Result)
```json
{
  "type": "complete",
  "execution_id": "uuid-string",
  "final_answer": "Escreva em Python um parser JSON otimizado que valida entrada...",
  "iterations_count": 3,
  "tokens_total": 4200,
  "time_total_ms": 15000,
  "quality_score": 0.92,
  "all_iterations": [
    {iteration_number: 1, ...},
    {iteration_number: 2, ...},
    {iteration_number: 3, ...}
  ],
  "metadata": {
    "technique_used": "self_refine",
    "model_used": "gpt-4o",
    "timestamp_completed": "2026-04-10T12:30:55.789Z"
  }
}
```

#### Error
```json
{
  "type": "error",
  "execution_id": "uuid-string",
  "error_code": "TIMEOUT | INVALID_PARAMS | LLM_ERROR | CANCELLED",
  "error_message": "Descrição do erro para o usuário",
  "details": {
    "code": "ERR_TIMEOUT_EXCEEDED",
    "suggestion": "Aumente max_time_ms ou reduza max_iterations"
  }
}
```

#### Heartbeat
```json
{
  "type": "heartbeat"
}
```

---

## 🎯 WebSocket Client Implementation

### Arquivo: `frontend/src/api/websocketClient.js`

```javascript
class WebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 3;
    this.reconnectDelay = options.reconnectDelay || 1000;
    this.heartbeatInterval = null;
    this.messageHandlers = {};
    this.isIntentionallyClosed = false;
  }

  /**
   * Conecta ao servidor WebSocket
   */
  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket] Conectado');
          this.reconnectAttempts = 0;
          this.isIntentionallyClosed = false;
          this._startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this._handleMessage(message);
          } catch (e) {
            console.error('[WebSocket] Erro parseando mensagem:', e);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Erro:', error);
          this._emit('error', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Desconectado');
          this._stopHeartbeat();
          
          if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
            this._attemptReconnect();
          } else {
            this._emit('close', { code: 'closed', intentional: this.isIntentionallyClosed });
          }
        };
      } catch (e) {
        reject(e);
      }
    });
  }

  /**
   * Envia mensagem ao servidor
   */
  send(message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket não está conectado');
    }
    this.ws.send(JSON.stringify(message));
  }

  /**
   * Registra handler para tipo de mensagem
   */
  on(messageType, handler) {
    if (!this.messageHandlers[messageType]) {
      this.messageHandlers[messageType] = [];
    }
    this.messageHandlers[messageType].push(handler);

    // Retorna função para unsubscribe
    return () => {
      this.messageHandlers[messageType] = this.messageHandlers[messageType].filter(h => h !== handler);
    };
  }

  /**
   * Fecha conexão deliberadamente
   */
  close() {
    this.isIntentionallyClosed = true;
    this._stopHeartbeat();
    if (this.ws) {
      this.ws.close();
    }
  }

  // === Métodos Privados ===

  _handleMessage(message) {
    const { type } = message;
    
    // Ignora heartbeat (sem handlers registrados por padrão)
    if (type === 'heartbeat') {
      return;
    }

    // Emite para handlers registrados
    if (this.messageHandlers[type]) {
      this.messageHandlers[type].forEach(handler => {
        try {
          handler(message);
        } catch (e) {
          console.error(`[WebSocket] Erro em handler para ${type}:`, e);
        }
      });
    }

    // Emite para handler genérico 'message'
    if (this.messageHandlers['message']) {
      this.messageHandlers['message'].forEach(handler => handler(message));
    }
  }

  _emit(eventType, data) {
    if (this.messageHandlers[eventType]) {
      this.messageHandlers[eventType].forEach(handler => handler(data));
    }
  }

  _startHeartbeat() {
    this._stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.send({ action: 'ping' });
        } catch (e) {
          console.warn('[WebSocket] Falha enviando heartbeat:', e);
        }
      }
    }, 30000); // A cada 30 segundos
  }

  _stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  _attemptReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`[WebSocket] Reconectando em ${delay}ms (tentativa ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(e => {
        console.error('[WebSocket] Falha na reconexão:', e);
      });
    }, delay);
  }
}

export default WebSocketClient;
```

---

## 🎣 Custom Hook: `useWebSocket`

### Arquivo: `frontend/src/hooks/useWebSocket.js`

```javascript
import { useEffect, useRef, useState, useCallback } from 'react';
import WebSocketClient from '../api/websocketClient';

/**
 * Hook que gerencia conexão WebSocket
 * 
 * @param {string} url - URL do servidor WebSocket
 * @param {object} options - Opções de configuração
 * @returns {object} - {connect, send, close, isConnected, error}
 */
export function useWebSocket(url, options = {}) {
  const clientRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  const connect = useCallback(async () => {
    try {
      if (!clientRef.current) {
        clientRef.current = new WebSocketClient(url, options);
      }
      await clientRef.current.connect();
      setIsConnected(true);
      setError(null);
    } catch (e) {
      setError(e);
      setIsConnected(false);
    }
  }, [url, options]);

  const send = useCallback((message) => {
    if (!clientRef.current || !isConnected) {
      throw new Error('WebSocket não está conectado');
    }
    clientRef.current.send(message);
  }, [isConnected]);

  const on = useCallback((messageType, handler) => {
    if (!clientRef.current) return () => {};
    return clientRef.current.on(messageType, handler);
  }, []);

  const close = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.close();
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    return () => {
      // Cleanup ao desmontar
      close();
    };
  }, [close]);

  return {
    connect,
    send,
    on,
    close,
    isConnected,
    error,
    client: clientRef.current
  };
}
```

---

## 📊 Custom Hook: `useStreamingResult`

### Arquivo: `frontend/src/hooks/useStreamingResult.js`

```javascript
import { useCallback, useState, useRef, useEffect } from 'react';

/**
 * Hook que consome mensagens WebSocket e constrói estado de resultado
 * 
 * @param {object} ws - Resultado do useWebSocket()
 * @returns {object} - {result, status, metrics, addIteration, reset, isComplete}
 */
export function useStreamingResult(ws) {
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, connecting, thinking, yielding, complete, error
  const [metrics, setMetrics] = useState({});
  const [iterations, setIterations] = useState([]);
  const [error, setError] = useState(null);
  const [executionId, setExecutionId] = useState(null);

  const unsubscribersRef = useRef([]);

  const reset = useCallback(() => {
    setResult(null);
    setStatus('idle');
    setMetrics({});
    setIterations([]);
    setError(null);
    setExecutionId(null);
  }, []);

  const handleStatusUpdate = useCallback((message) => {
    setExecutionId(message.execution_id);
    setStatus(message.status);
    setMetrics(m => ({
      ...m,
      current_iteration: message.current_iteration,
      max_iterations: message.max_iterations
    }));
  }, []);

  const handleIterationYield = useCallback((message) => {
    setExecutionId(message.execution_id);
    setStatus('yielding');
    setIterations(prev => [...prev, {
      iteration_number: message.iteration_number,
      timestamp: message.timestamp,
      generated_candidates: message.generated_candidates,
      evaluation_scores: message.evaluation_scores,
      selected_best: message.selected_best,
      feedback_from_critic: message.feedback_from_critic,
      tokens_this_iteration: message.tokens_this_iteration,
      extra_data: message.extra_data
    }]);
  }, []);

  const handleMetricsUpdate = useCallback((message) => {
    setMetrics(m => ({
      ...m,
      tokens_so_far: message.tokens_so_far,
      tokens_max: message.tokens_max,
      time_elapsed_ms: message.time_elapsed_ms,
      time_max_ms: message.time_max_ms,
      current_iteration: message.current_iteration,
      max_iterations: message.max_iterations,
      progress_percent: Math.round((message.current_iteration / message.max_iterations) * 100)
    }));
  }, []);

  const handleComplete = useCallback((message) => {
    setExecutionId(message.execution_id);
    setStatus('complete');
    setResult({
      final_answer: message.final_answer,
      iterations_count: message.iterations_count,
      tokens_total: message.tokens_total,
      time_total_ms: message.time_total_ms,
      quality_score: message.quality_score,
      all_iterations: message.all_iterations,
      metadata: message.metadata
    });
  }, []);

  const handleError = useCallback((message) => {
    setExecutionId(message.execution_id);
    setStatus('error');
    setError({
      code: message.error_code,
      message: message.error_message,
      details: message.details
    });
  }, []);

  // Setup listeners
  useEffect(() => {
    if (!ws.client) return;

    const unsubscribers = [
      ws.on('status', handleStatusUpdate),
      ws.on('iteration', handleIterationYield),
      ws.on('metrics', handleMetricsUpdate),
      ws.on('complete', handleComplete),
      ws.on('error', handleError)
    ];

    unsubscribersRef.current = unsubscribers;

    return () => {
      unsubscribers.forEach(unsub => unsub?.());
    };
  }, [ws, handleStatusUpdate, handleIterationYield, handleMetricsUpdate, handleComplete, handleError]);

  return {
    result,
    status,
    metrics,
    iterations,
    error,
    executionId,
    reset,
    isComplete: status === 'complete' || status === 'error'
  };
}
```

---

## 💻 Exemplo de Uso em Componente

### Arquivo: `frontend/src/components/MainPage.js` (snippet)

```javascript
import { useWebSocket } from '../hooks/useWebSocket';
import { useStreamingResult } from '../hooks/useStreamingResult';
import { API_CONFIG } from '../config';

export default function MainPage() {
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [selectedTechnique, setSelectedTechnique] = useState('self_refine');
  const [recursionConfig, setRecursionConfig] = useState({
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    max_iterations: 3,
    max_tokens_total: 10000
  });

  // WebSocket Hook
  const ws = useWebSocket(API_CONFIG.WS_URL, {
    maxReconnectAttempts: 3,
    reconnectDelay: 1000
  });

  // Streaming Result Hook
  const streamingResult = useStreamingResult(ws);

  const handleImprovePrompt = async () => {
    if (!originalPrompt.trim()) {
      setError('Digite um prompt');
      return;
    }

    try {
      // Conecta WebSocket
      if (!ws.isConnected) {
        await ws.connect();
      }

      // Reset estado anterior
      streamingResult.reset();

      // Envia request
      ws.send({
        action: 'start_reasoning',
        prompt: originalPrompt,
        technique: selectedTechnique,
        config: recursionConfig
      });
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancel = () => {
    if (streamingResult.executionId) {
      ws.send({
        action: 'cancel',
        execution_id: streamingResult.executionId
      });
    }
    streamingResult.reset();
  };

  return (
    <div className="main-page">
      <h1>Prompt-Boost v2.0</h1>

      {/* Input */}
      <textarea 
        value={originalPrompt}
        onChange={(e) => setOriginalPrompt(e.target.value)}
        disabled={streamingResult.status !== 'idle'}
        placeholder="Cole seu prompt aqui..."
      />

      {/* Técnica + Configurações */}
      <RecursiveOptions
        onTechniqueChange={setSelectedTechnique}
        onConfigChange={setRecursionConfig}
        isLoading={streamingResult.status !== 'idle'}
        currentTechnique={selectedTechnique}
        currentConfig={recursionConfig}
      />

      {/* Botões */}
      <button 
        onClick={handleImprovePrompt}
        disabled={streamingResult.status !== 'idle'}
      >
        🚀 Melhorar Prompt
      </button>

      {streamingResult.status !== 'idle' && (
        <button onClick={handleCancel} className="cancel-btn">
          ⏹️ Cancelar
        </button>
      )}

      {/* Resultado em Streaming */}
      {streamingResult.status !== 'idle' && (
        <>
          <StreamingOutput
            status={streamingResult.status}
            metrics={streamingResult.metrics}
            error={streamingResult.error}
          />

          <IterationVisualizer
            iterations={streamingResult.iterations}
            isLoading={streamingResult.status !== 'complete' && streamingResult.status !== 'error'}
          />
        </>
      )}

      {/* Resultado Final */}
      {streamingResult.result && (
        <>
          <MetricsPanel
            result={streamingResult.result}
            technique={selectedTechnique}
          />

          <div className="improved-prompt">
            <h3>Prompt Melhorado</h3>
            <p>{streamingResult.result.final_answer}</p>
          </div>
        </>
      )}

      {/* Erro */}
      {streamingResult.error && (
        <ErrorDisplay
          error={streamingResult.error}
          onRetry={handleImprovePrompt}
        />
      )}
    </div>
  );
}
```

---

## 🛡️ Error Handling & Resilience

### Padrão de Retry

```javascript
async function executeWithRetry(operation, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      
      const delay = 1000 * Math.pow(2, attempt - 1); // Exponential backoff
      console.warn(`Tentativa ${attempt} falhou, retentando em ${delay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// Uso
await executeWithRetry(
  () => ws.connect(),
  3
);
```

### Timeouts

```javascript
function withTimeout(promise, timeoutMs) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), timeoutMs)
    )
  ]);
}

// Uso
await withTimeout(
  ws.send({action: 'start_reasoning', ...}),
  30000 // 30 segundos
);
```

---

## 📋 Checklist de Implementação

- [ ] `websocketClient.js`: Cliente WebSocket com reconnect
- [ ] `useWebSocket.js`: Hook para gerenciar conexão
- [ ] `useStreamingResult.js`: Hook para consumir mensagens
- [ ] `StreamingOutput.js`: Componente que exibe status
- [ ] Testes unitários para websocket client
- [ ] Testes de integração com backend
- [ ] Documentação de troubleshooting
- [ ] Performance profiling
- [ ] Suporte a SSL/WSS em produção

---

**Referências Cruzadas**:
- Backend: `/docs/09-IMPLEMENTACAO-PRATICA.md`
- Componentes: `/frontend/docs/01-COMPONENTES-PRINCIPAIS.md`
- Hooks: `/frontend/docs/04-ESTADO-GLOBAL-E-HOOKS.md`
