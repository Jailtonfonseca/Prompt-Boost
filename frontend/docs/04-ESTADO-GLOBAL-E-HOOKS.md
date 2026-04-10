# 04 - Estado Global & Custom Hooks

## 🧠 Visão Geral

Este documento descreve como gerenciar estado complexo no Prompt-Boost v2.0 usando:
- Context API + Hooks (simples)
- Zustand (recomendado) - state management leve
- Custom Hooks reutilizáveis

---

## 🏗️ Estratégia de Estado

### Separação por Domínio

```
Global State (Zustand)
├── UI State
│   ├── sidebarOpen
│   ├── theme
│   └── notifications
│
├── Recursion State
│   ├── currentExecution
│   ├── executionHistory
│   └── savedConfigs
│
└── User Preferences
    ├── defaultTechnique
    ├── defaultConfig
    └── savedPrompts

Local Component State (useState)
├── Form inputs
├── Temporary UI flags
└── Animation states
```

---

## 📦 Zustand Store (Recomendado)

### Arquivo: `frontend/src/store/recursionStore.js`

```javascript
import create from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist } from 'zustand/middleware';

/**
 * Estado de Execução Recursiva
 */
export const useRecursionStore = create(
  persist(
    immer((set, get) => ({
      // === CURRENT EXECUTION ===
      currentExecution: {
        id: null,
        status: 'idle', // idle, connecting, thinking, yielding, complete, error
        originalPrompt: '',
        technique: 'self_refine',
        config: {
          provider: 'openai',
          model: 'gpt-4o',
          temperature: 0.7,
          max_iterations: 3,
          max_tokens_total: 10000,
          extra_params: {}
        },
        result: null,
        iterations: [],
        metrics: {},
        error: null,
        createdAt: null,
        completedAt: null
      },

      // === EXECUTION HISTORY ===
      executionHistory: [],
      maxHistoryItems: 50,

      // === USER PREFERENCES ===
      preferences: {
        defaultTechnique: 'self_refine',
        defaultProvider: 'openai',
        defaultModel: 'gpt-4o',
        defaultIterations: 3,
        defaultTokens: 10000,
        comparisonMode: false,
        enableNotifications: true,
        theme: 'light' // light | dark
      },

      // === SAVED CONFIGURATIONS ===
      savedConfigs: [],

      // === SAVED PROMPTS ===
      savedPrompts: [],

      // === ACTIONS ===

      // Iniciar nova execução
      startExecution: (prompt, technique, config) =>
        set((state) => {
          state.currentExecution = {
            id: `exec_${Date.now()}_${Math.random()}`,
            status: 'connecting',
            originalPrompt: prompt,
            technique: technique,
            config: config,
            result: null,
            iterations: [],
            metrics: {},
            error: null,
            createdAt: new Date().toISOString(),
            completedAt: null
          };
        }),

      // Atualizar status
      updateStatus: (status) =>
        set((state) => {
          state.currentExecution.status = status;
        }),

      // Adicionar iteração
      addIteration: (iterationData) =>
        set((state) => {
          state.currentExecution.iterations.push(iterationData);
          state.currentExecution.status = 'yielding';
        }),

      // Atualizar métricas em tempo real
      updateMetrics: (metrics) =>
        set((state) => {
          state.currentExecution.metrics = {
            ...state.currentExecution.metrics,
            ...metrics
          };
        }),

      // Completar execução com sucesso
      completeExecution: (result) =>
        set((state) => {
          state.currentExecution.status = 'complete';
          state.currentExecution.result = result;
          state.currentExecution.completedAt = new Date().toISOString();

          // Adicionar ao histórico
          state.executionHistory.unshift({
            ...state.currentExecution,
            // Snapshot do estado completo
          });

          // Limitar histórico
          if (state.executionHistory.length > state.maxHistoryItems) {
            state.executionHistory.pop();
          }
        }),

      // Registrar erro
      setError: (error) =>
        set((state) => {
          state.currentExecution.status = 'error';
          state.currentExecution.error = error;
        }),

      // Cancelar execução
      cancelExecution: () =>
        set((state) => {
          state.currentExecution.status = 'idle';
          state.currentExecution = {
            ...state.currentExecution,
            iterations: state.currentExecution.iterations,
            metrics: state.currentExecution.metrics,
            result: state.currentExecution.result,
            // Mantém dados parciais
          };
        }),

      // Resetar execução atual
      resetCurrentExecution: () =>
        set((state) => {
          state.currentExecution = {
            id: null,
            status: 'idle',
            originalPrompt: '',
            technique: 'self_refine',
            config: state.preferences.defaultConfig || {},
            result: null,
            iterations: [],
            metrics: {},
            error: null,
            createdAt: null,
            completedAt: null
          };
        }),

      // Salvar configuração
      saveConfig: (name, config) =>
        set((state) => {
          const saved = {
            id: `config_${Date.now()}`,
            name,
            config,
            createdAt: new Date().toISOString()
          };
          state.savedConfigs.unshift(saved);
        }),

      // Deletar configuração salva
      deleteConfig: (configId) =>
        set((state) => {
          state.savedConfigs = state.savedConfigs.filter(
            (c) => c.id !== configId
          );
        }),

      // Carregar configuração salva
      loadConfig: (configId) =>
        set((state) => {
          const config = state.savedConfigs.find((c) => c.id === configId);
          if (config) {
            state.currentExecution.config = config.config;
          }
        }),

      // Salvar prompt
      savePrompt: (name, prompt) =>
        set((state) => {
          const saved = {
            id: `prompt_${Date.now()}`,
            name,
            prompt,
            createdAt: new Date().toISOString(),
            usageCount: 0
          };
          state.savedPrompts.unshift(saved);
        }),

      // Atualizar preferências
      updatePreferences: (prefs) =>
        set((state) => {
          state.preferences = {
            ...state.preferences,
            ...prefs
          };
        }),

      // Obter histórico filtrado
      getHistoryByTechnique: (technique) => {
        const state = get();
        return state.executionHistory.filter(
          (exec) => exec.technique === technique
        );
      },

      // Obter melhor resultado do histórico
      getBestResultByMetric: (metric = 'quality_score') => {
        const state = get();
        if (state.executionHistory.length === 0) return null;

        return state.executionHistory.reduce((best, current) => {
          const currentValue = current.result?.[metric] || 0;
          const bestValue = best.result?.[metric] || 0;
          return currentValue > bestValue ? current : best;
        });
      },

      // Limpar histórico
      clearHistory: () =>
        set((state) => {
          state.executionHistory = [];
        })
    })),
    {
      name: 'prompt-boost-store',
      partialize: (state) => ({
        executionHistory: state.executionHistory.slice(0, 10),
        savedConfigs: state.savedConfigs,
        savedPrompts: state.savedPrompts,
        preferences: state.preferences
      })
    }
  )
);
```

### Arquivo: `frontend/src/store/uiStore.js`

```javascript
import create from 'zustand';

/**
 * Estado de UI
 */
export const useUIStore = create((set) => ({
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  modals: {
    settings: false,
    history: false,
    shareResult: false
  },

  // Actions
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setTheme: (theme) => set({ theme }),

  addNotification: (notification) =>
    set((state) => {
      const id = `notif_${Date.now()}`;
      const notif = {
        id,
        type: 'info', // info, success, warning, error
        message: notification.message || notification,
        duration: notification.duration || 3500,
        dismissible: notification.dismissible !== false
      };

      // Auto-dismiss
      if (notif.duration > 0) {
        setTimeout(() => {
          set((s) => ({
            notifications: s.notifications.filter((n) => n.id !== id)
          }));
        }, notif.duration);
      }

      return {
        notifications: [...state.notifications, notif]
      };
    }),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id)
    })),

  openModal: (modalName) =>
    set((state) => ({
      modals: { ...state.modals, [modalName]: true }
    })),

  closeModal: (modalName) =>
    set((state) => ({
      modals: { ...state.modals, [modalName]: false }
    }))
}));
```

---

## 🪝 Custom Hooks

### 1. `useRecursiveThinking` - Orquestra todo o fluxo

**Arquivo**: `frontend/src/hooks/useRecursiveThinking.js`

```javascript
import { useCallback, useRef } from 'react';
import { useWebSocket } from './useWebSocket';
import { useStreamingResult } from './useStreamingResult';
import { useRecursionStore } from '../store/recursionStore';
import { useUIStore } from '../store/uiStore';

/**
 * Hook principal que coordena WebSocket, streaming e estado
 */
export function useRecursiveThinking() {
  const abortControllerRef = useRef(null);

  // Stores
  const recursionState = useRecursionStore();
  const ui = useUIStore();

  // WebSocket & Streaming
  const ws = useWebSocket(process.env.REACT_APP_WS_URL, {
    maxReconnectAttempts: 3,
    reconnectDelay: 1000
  });

  const streaming = useStreamingResult(ws);

  const improve = useCallback(
    async (originalPrompt, technique, config) => {
      try {
        // Reset estado
        recursionState.resetCurrentExecution();
        recursionState.startExecution(originalPrompt, technique, config);

        // Conectar WebSocket se necessário
        if (!ws.isConnected) {
          await ws.connect();
        }

        // Criar abort controller para poder cancelar
        abortControllerRef.current = new AbortController();

        // Enviar request
        ws.send({
          action: 'start_reasoning',
          prompt: originalPrompt,
          technique: technique,
          config: config
        });

        // Aguardar conclusão
        await new Promise((resolve, reject) => {
          const timeoutId = setTimeout(
            () => reject(new Error('Timeout')),
            config.max_time_ms || 120000
          );

          const checkCompletion = () => {
            if (streaming.status === 'complete' || streaming.status === 'error') {
              clearTimeout(timeoutId);
              resolve();
            } else {
              setTimeout(checkCompletion, 100);
            }
          };

          checkCompletion();
        });

        // Atualizar estado com resultado
        if (streaming.result) {
          recursionState.completeExecution(streaming.result);
          ui.addNotification({
            type: 'success',
            message: 'Prompt melhorado com sucesso!'
          });
        }

        if (streaming.error) {
          throw streaming.error;
        }

        return streaming.result;
      } catch (error) {
        recursionState.setError(error);
        ui.addNotification({
          type: 'error',
          message: `Erro: ${error.message}`,
          duration: 5000
        });
        throw error;
      }
    },
    [ws, streaming, recursionState, ui]
  );

  const cancel = useCallback(() => {
    if (streaming.executionId) {
      ws.send({
        action: 'cancel',
        execution_id: streaming.executionId
      });
    }
    recursionState.cancelExecution();
    streaming.reset();
  }, [ws, streaming, recursionState]);

  return {
    improve,
    cancel,
    status: streaming.status,
    result: streaming.result,
    iterations: streaming.iterations,
    metrics: streaming.metrics,
    error: streaming.error,
    executionId: streaming.executionId,
    isProcessing: streaming.status !== 'idle' && streaming.status !== 'complete'
  };
}
```

### 2. `usePersistence` - Salva dados no localStorage

**Arquivo**: `frontend/src/hooks/usePersistence.js`

```javascript
import { useEffect } from 'react';

/**
 * Hook para persistir estado no localStorage
 */
export function usePersistence(key, value, options = {}) {
  const {
    debounceMs = 500,
    serializer = JSON.stringify,
    deserializer = JSON.parse
  } = options;

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      try {
        const serialized = serializer(value);
        localStorage.setItem(key, serialized);
      } catch (error) {
        console.error(`Erro salvando ${key} no localStorage:`, error);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [key, value, debounceMs, serializer]);
}

/**
 * Hook para recuperar dados do localStorage
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = React.useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Erro salvando localStorage:`, error);
    }
  };

  return [storedValue, setValue];
}
```

### 3. `useAsync` - Gerencia promises

**Arquivo**: `frontend/src/hooks/useAsync.js`

```javascript
import { useState, useEffect, useCallback } from 'react';

/**
 * Hook para manejar operações assíncronas
 */
export function useAsync(asyncFunction, immediate = true) {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setStatus('pending');
    setData(null);
    setError(null);

    try {
      const response = await asyncFunction(...args);
      setData(response);
      setStatus('success');
      return response;
    } catch (error) {
      setError(error);
      setStatus('error');
      throw error;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, data, error };
}
```

### 4. `useDebounce` - Debounce de valores

**Arquivo**: `frontend/src/hooks/useDebounce.js`

```javascript
import { useState, useEffect } from 'react';

/**
 * Hook que debouncea um valor
 */
export function useDebounce(value, delayMs = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delayMs);

    return () => clearTimeout(handler);
  }, [value, delayMs]);

  return debouncedValue;
}
```

---

## 🎯 Context API (Alternativa Simples)

Se preferir não usar Zustand, Context API também funciona:

### Arquivo: `frontend/src/context/RecursionContext.js`

```javascript
import { createContext, useReducer, useCallback } from 'react';

export const RecursionContext = createContext();

const initialState = {
  currentExecution: {
    status: 'idle',
    iterations: [],
    result: null,
    error: null
  },
  executionHistory: [],
  preferences: {}
};

function recursionReducer(state, action) {
  switch (action.type) {
    case 'START_EXECUTION':
      return {
        ...state,
        currentExecution: {
          status: 'connecting',
          originalPrompt: action.payload.prompt,
          technique: action.payload.technique,
          config: action.payload.config,
          iterations: [],
          result: null,
          error: null
        }
      };

    case 'ADD_ITERATION':
      return {
        ...state,
        currentExecution: {
          ...state.currentExecution,
          iterations: [...state.currentExecution.iterations, action.payload]
        }
      };

    case 'COMPLETE_EXECUTION':
      return {
        ...state,
        currentExecution: {
          ...state.currentExecution,
          status: 'complete',
          result: action.payload
        },
        executionHistory: [
          state.currentExecution,
          ...state.executionHistory
        ].slice(0, 50)
      };

    case 'ERROR':
      return {
        ...state,
        currentExecution: {
          ...state.currentExecution,
          status: 'error',
          error: action.payload
        }
      };

    default:
      return state;
  }
}

export function RecursionProvider({ children }) {
  const [state, dispatch] = useReducer(recursionReducer, initialState);

  const startExecution = useCallback((prompt, technique, config) => {
    dispatch({
      type: 'START_EXECUTION',
      payload: { prompt, technique, config }
    });
  }, []);

  const addIteration = useCallback((iteration) => {
    dispatch({
      type: 'ADD_ITERATION',
      payload: iteration
    });
  }, []);

  const completeExecution = useCallback((result) => {
    dispatch({
      type: 'COMPLETE_EXECUTION',
      payload: result
    });
  }, []);

  const setError = useCallback((error) => {
    dispatch({
      type: 'ERROR',
      payload: error
    });
  }, []);

  return (
    <RecursionContext.Provider
      value={{
        state,
        startExecution,
        addIteration,
        completeExecution,
        setError
      }}
    >
      {children}
    </RecursionContext.Provider>
  );
}

export function useRecursion() {
  const context = React.useContext(RecursionContext);
  if (!context) {
    throw new Error('useRecursion deve ser usado dentro de RecursionProvider');
  }
  return context;
}
```

---

## 📊 Padrão de Uso em Componentes

### Exemplo com Zustand

```javascript
import { useRecursionStore } from '../store/recursionStore';
import { useRecursiveThinking } from '../hooks/useRecursiveThinking';

export function MainPage() {
  const store = useRecursionStore();
  const { improve, cancel, status, result } = useRecursiveThinking();

  const handleImprove = async () => {
    try {
      await improve(
        originalPrompt,
        'self_refine',
        store.currentExecution.config
      );
    } catch (error) {
      console.error('Erro:', error);
    }
  };

  return (
    <div>
      <button onClick={handleImprove} disabled={status !== 'idle'}>
        Melhorar
      </button>
      
      {status !== 'idle' && (
        <button onClick={cancel}>Cancelar</button>
      )}

      {result && (
        <div>
          <p>{result.final_answer}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🧪 Testando Hooks

### Exemplo com React Testing Library

```javascript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useRecursiveThinking } from './useRecursiveThinking';

test('useRecursiveThinking completa com sucesso', async () => {
  const { result } = renderHook(() => useRecursiveThinking());

  await act(async () => {
    await result.current.improve(
      'Test prompt',
      'self_refine',
      { max_iterations: 1 }
    );
  });

  await waitFor(() => {
    expect(result.current.status).toBe('complete');
    expect(result.current.result).toBeDefined();
  });
});
```

---

## 📋 Checklist de Implementação

- [ ] Zustand store criado e testado
- [ ] Custom hooks implementados
- [ ] Integração com WebSocket testada
- [ ] Persistência no localStorage funcionando
- [ ] Error handling robusto
- [ ] TypeScript types (opcional mas recomendado)
- [ ] Testes unitários para hooks
- [ ] Performance profiling (Redux DevTools)
- [ ] Documentação de padrões

---

**Referências Cruzadas**:
- WebSocket: `/frontend/docs/02-INTEGRACAO-WEBSOCKET.md`
- Componentes: `/frontend/docs/01-COMPONENTES-PRINCIPAIS.md`
- Arquitetura: `/frontend/docs/00-ARQUITETURA-FRONTEND.md`
