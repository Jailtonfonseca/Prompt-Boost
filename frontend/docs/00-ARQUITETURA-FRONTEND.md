# 00 - Arquitetura Frontend do Prompt-Boost v2.0

## 🎯 Visão Geral

O frontend do Prompt-Boost v2.0 evolui de uma aplicação simples de melhoria de prompts para uma **plataforma interativa de raciocínio recursivo** com visualização em tempo real, seleção de técnicas avançadas e comunicação WebSocket.

### Princípios de Design
- **Reatividade**: UI reflete estado em tempo real via WebSocket
- **Composição**: Componentes reutilizáveis e testáveis
- **Extensibilidade**: Fácil adicionar novas técnicas e visualizações
- **Performance**: Lazy loading, memoização, virtual scrolling
- **Acessibilidade**: WCAG 2.1 AA compliance

---

## 🏗️ Arquitetura de Componentes

### Diagrama Hierárquico

```
App.js
├── MainPage (PÁGINA PRINCIPAL - Versão 2.0)
│   ├── PromptInput
│   │   ├── textarea (original prompt)
│   │   └── charCounter
│   │
│   ├── RecursiveOptions (NOVO)
│   │   ├── TechniqueSelector
│   │   │   ├── Self-Refine
│   │   │   ├── Tree of Thoughts
│   │   │   ├── Graph of Thoughts
│   │   │   ├── LLM-MCTS
│   │   │   ├── Multi-Agent Debate
│   │   │   ├── Recursive Alignment
│   │   │   └── AutoFormalization
│   │   │
│   │   ├── RecursiveSettings
│   │   │   ├── maxIterations slider (1-10)
│   │   │   ├── maxTokens input (1000-50000)
│   │   │   ├── temperature slider (0.0-2.0)
│   │   │   ├── providerSelector (OpenAI, Anthropic, etc)
│   │   │   ├── modelSelector (dynamic based on provider)
│   │   │   └── advancedParams (collapsible)
│   │   │
│   │   └── ComparisonMode toggle (off/on)
│   │
│   ├── ActionButtons
│   │   ├── Improve (activates single technique)
│   │   ├── Compare (activates multiple techniques)
│   │   ├── Stop (cancels ongoing process)
│   │   └── Clear
│   │
│   ├── ResultsPanel (NOVO - Layout flexível)
│   │   ├── IF mode === 'single'
│   │   │   └── SingleResultView
│   │   │       ├── IterationVisualizer (NOVO)
│   │   │       │   ├── Timeline (iterações como cards)
│   │   │       │   │   ├── Iteração 1
│   │   │       │   │   │   ├── generated_candidates
│   │   │       │   │   │   ├── evaluation_scores
│   │   │       │   │   │   └── feedback
│   │   │       │   │   ├── Iteração 2
│   │   │       │   │   └── Iteração 3
│   │   │       │   │
│   │   │       ├── MetricsPanel (NOVO)
│   │   │       │   ├── iterations_count
│   │   │       │   ├── tokens_used
│   │   │       │   ├── time_elapsed
│   │   │       │   ├── quality_score (0-1)
│   │   │       │   └── rer_score (Recursion Efficiency Ratio)
│   │   │       │
│   │   │       └── ImprovedPromptDisplay
│   │   │           ├── DiffDisplay (visual diff)
│   │   │           ├── CopyButton
│   │   │           └── DownloadButton
│   │   │
│   │   ├── IF mode === 'compare'
│   │   │   └── ComparisonView (NOVO)
│   │   │       ├── TechniqueComparison (grid/tabs)
│   │   │       │   ├── Tab: Self-Refine result
│   │   │       │   ├── Tab: ToT result
│   │   │       │   ├── Tab: Debate result
│   │   │       │   └── MetricsComparison (tabela)
│   │   │       │       ├── Coluna: Technique
│   │   │       │       ├── Coluna: Quality Score
│   │   │       │       ├── Coluna: Tokens Used
│   │   │       │       ├── Coluna: Time (ms)
│   │   │       │       └── Coluna: RER
│   │   │       │
│   │   │       ├── BestSolutionHighlight
│   │   │       │   └── Score mais alto em destaque
│   │   │       │
│   │   │       └── RecommendationPanel
│   │   │           ├── Técnica recomendada p/ problema
│   │   │           └── Razão (qual métrica é melhor)
│   │   │
│   │   └── LoadingState
│   │       ├── StreamingOutput (NOVO)
│   │       │   ├── Status badge
│   │       │   │   ├── Connecting
│   │       │   │   ├── Thinking...
│   │       │   │   ├── Yielding results
│   │       │   │   ├── Complete ✓
│   │       │   │   └── Error ✗
│   │       │   │
│   │       │   ├── RealTimeMetrics (atualizado via WebSocket)
│   │       │   │   ├── tokens_so_far: X/Ymax
│   │       │   │   ├── time_elapsed: X.XXs
│   │       │   │   ├── current_iteration: X/Ymax
│   │       │   │   └── estimated_completion: X%
│   │       │   │
│   │       │   └── ProgressBar (animado)
│   │       │
│   │       └── ErrorDisplay
│   │           ├── error message
│   │           ├── error code
│   │           ├── suggestion (how to fix)
│   │           └── retry button
│   │
│   └── ActionBar (Bottom)
│       ├── ShareButton
│       ├── PublishButton
│       └── HistoryButton (access recent)
│
├── SharedPromptPage
│   └── (mantém estrutura existente)
│
├── GalleryPage
│   └── (mantém estrutura existente)
│
└── SettingsPage (ESTENDIDO)
    ├── API Settings (existente)
    ├── Default Technique Selection (NOVO)
    ├── Recursion Preferences (NOVO)
    │   ├── Default max iterations
    │   ├── Default max tokens
    │   ├── Auto-enable comparison mode
    │   └── Preferred visualization style
    └── Advanced Options (NOVO)
        ├── WebSocket URL configuration
        ├── Timeout settings
        └── Cache preferences
```

---

## 🔄 Fluxo de Dados Global

### Request-Response Cycle (Single Technique)

```
1. USER INTERACTION
   └─ Clica "Improve"
   
2. STATE UPDATE
   └─ MainPage: {
       originalPrompt: "...",
       technique: "self_refine",
       isLoading: true,
       config: {...}
      }
      
3. API CALL
   └─ POST /api/improve-prompt-recursive {
       prompt,
       technique,
       config
      }
      
4. BACKEND PROCESSING
   └─ RecursionRouter seleciona engine
      └─ self_refine_engine.run()
      
5. RESPONSE (com todas iterações)
   └─ RecursionResult {
       final_answer: "...",
       iterations_count: 3,
       tokens_total: 4200,
       all_iterations: [
         {iteration_number: 1, ...},
         {iteration_number: 2, ...},
         {iteration_number: 3, ...}
       ],
       metadata: {...}
      }
      
6. UI UPDATE
   └─ MainPage renderiza:
       ├── IterationVisualizer (mostra timeline)
       ├── MetricsPanel (scores e tokens)
       └── ImprovedPromptDisplay (resultado final)
```

### WebSocket Cycle (Real-Time Streaming)

```
1. USER INTERACTION
   └─ Clica "Improve" (modo streaming ativado)
   
2. WEBSOCKET CONNECT
   └─ ws.connect('ws://localhost:8000/ws/recursive')
   
3. SEND REQUEST
   └─ ws.send({
       action: "start_reasoning",
       prompt: "...",
       technique: "tot",
       config: {...}
      })
      
4. STREAMING RESPONSES (múltiplas mensagens)
   └─ Message 1: {status: "thinking", current_iteration: 1}
   └─ Message 2: {status: "yielding", iteration_data: {...}}
   └─ Message 3: {status: "thinking", current_iteration: 2}
   └─ Message 4: {status: "yielding", iteration_data: {...}}
   └─ Message 5: {status: "complete", final_result: {...}}
   
5. UI UPDATES (cada mensagem)
   └─ StreamingOutput atualiza status badge
   └─ RealTimeMetrics atualiza counters
   └─ IterationVisualizer adiciona novo card
   └─ ProgressBar anima para completion %
   
6. FINALIZATION
   └─ WebSocket fecha
   └─ ResultsPanel mostra versão final
```

---

## 🌳 Diagrama de Estado (State Machine)

```
Initial State
└─ idle: {
     originalPrompt: "",
     improvedPrompt: "",
     isLoading: false,
     technique: null,
     results: null,
     wsConnection: null
   }

Transition: User clicks "Improve"
└─ loading: {
     originalPrompt: "...",
     isLoading: true,
     wsConnection: WebSocket instance,
     streamingProgress: {
       current_iteration: 0,
       tokens_used: 0,
       status: "connecting"
     }
   }

Transition: WebSocket connects
└─ streaming: {
     status: "thinking",
     current_iteration: 1,
     realTimeMetrics: {
       tokens_used: 0-max,
       time_elapsed: 0-timeout,
       iterations_so_far: 1/max
     },
     iterations_display: []
   }

Transition: Backend yields iteration data
└─ streaming: {
     status: "yielding",
     iterations_display: [
       {
         iteration_number: 1,
         generated: [...],
         scores: [...],
         feedback: "...",
         best: "..."
       }
     ]
   }

Transition: Final message received
└─ success: {
     improvedPrompt: "final answer",
     results: RecursionResult,
     metrics: {
       iterations_count: 3,
       tokens_total: 4200,
       time_total_ms: 15000,
       quality_score: 0.92,
       rer_score: 1.84
     }
   }

Transition: Error occurs
└─ error: {
     error_message: "...",
     error_code: "...",
     can_retry: true
   }

Transition: User clicks "Clear"
└─ idle (volta ao estado inicial)
```

---

## 🗂️ Estrutura de Pastas (Frontend)

```
frontend/
├── src/
│   ├── components/
│   │   ├── MainPage.js
│   │   ├── RecursiveOptions/
│   │   │   ├── RecursiveOptions.js (container)
│   │   │   ├── TechniqueSelector.js
│   │   │   ├── RecursiveSettings.js
│   │   │   └── ComparisonModeToggle.js
│   │   │
│   │   ├── Results/
│   │   │   ├── ResultsPanel.js (container)
│   │   │   ├── SingleResultView.js
│   │   │   ├── ComparisonView.js
│   │   │   ├── IterationVisualizer.js (NOVO)
│   │   │   ├── MetricsPanel.js (NOVO)
│   │   │   ├── StreamingOutput.js (NOVO)
│   │   │   ├── TechniqueComparison.js (NOVO)
│   │   │   └── MetricsComparison.js (NOVO)
│   │   │
│   │   ├── Common/
│   │   │   ├── DiffDisplay.js (existente)
│   │   │   ├── LoadingSpinner.js
│   │   │   ├── ErrorBoundary.js
│   │   │   └── ProgressBar.js
│   │   │
│   │   ├── SharedPromptPage.js (existente)
│   │   ├── GalleryPage.js (existente)
│   │   └── SettingsPage.js (existente + extensões)
│   │
│   ├── hooks/
│   │   ├── useRecursiveThinking.js (NOVO)
│   │   ├── useWebSocket.js (NOVO)
│   │   ├── useStreamingResult.js (NOVO)
│   │   ├── usePersistence.js (NOVO)
│   │   └── useLocalStorage.js (existente)
│   │
│   ├── context/
│   │   ├── RecursionContext.js (NOVO)
│   │   └── RecursionProvider.js (NOVO)
│   │
│   ├── api/
│   │   ├── api.js (existente, estender)
│   │   ├── recursiveApi.js (NOVO)
│   │   └── websocketClient.js (NOVO)
│   │
│   ├── styles/
│   │   ├── App.css (existente, estender)
│   │   ├── RecursiveOptions.css (NOVO)
│   │   ├── IterationVisualizer.css (NOVO)
│   │   ├── MetricsPanel.css (NOVO)
│   │   ├── StreamingOutput.css (NOVO)
│   │   └── variables.css (NOVO - design tokens)
│   │
│   ├── utils/
│   │   ├── formatters.js (NOVO)
│   │   ├── validators.js (NOVO)
│   │   ├── constants.js (NOVO)
│   │   └── storage.js (NOVO)
│   │
│   ├── App.js (existente, manter roteamento)
│   └── index.js
│
├── docs/
│   ├── INDEX.md
│   ├── 00-ARQUITETURA-FRONTEND.md (ESTE ARQUIVO)
│   ├── 01-COMPONENTES-PRINCIPAIS.md
│   ├── 02-INTEGRACAO-WEBSOCKET.md
│   ├── 03-FLUXO-DE-USUARIO.md
│   ├── 04-ESTADO-GLOBAL-E-HOOKS.md
│   └── 05-CASOS-DE-USO-FRONTEND.md
│
├── public/
├── package.json (estender com novas dependências)
├── Dockerfile
└── README.md (atualizar com referências aos docs)
```

---

## 📦 Dependências Adicionais Recomendadas

```json
{
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1",
    "react-router-dom": "^7.8.0",
    "react-scripts": "5.0.1",
    "diff-match-patch": "^1.0.5",
    
    "zustand": "^4.4.0",
    "immer": "^10.0.0",
    "ws": "^8.13.0",
    "axios": "^1.6.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0",
    "react-markdown": "^9.0.0",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "@testing-library/react": "^16.3.0",
    "@testing-library/jest-dom": "^6.6.4",
    "@testing-library/user-event": "^13.5.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

### Justificativa de Dependências
- **zustand**: State management leve e reativo (alternativa a Redux)
- **immer**: Immutability helpers para estado complexo
- **ws**: WebSocket client com reconnect automático
- **axios**: HTTP client com interceptors
- **date-fns**: Formatação de datas/tempos
- **clsx**: Conditional CSS classes
- **react-markdown**: Renderizar feedback em markdown
- **recharts**: Gráficos para comparação de técnicas

---

## 🔌 Padrão de Integração Com Backend

### API Endpoints Esperados

```
POST /api/improve-prompt-recursive
  Request: {prompt, technique, config}
  Response: RecursionResult

WS /ws/recursive
  Connection: ws://localhost:8000/ws/recursive
  Messages: StreamingUpdates (veja 02-INTEGRACAO-WEBSOCKET.md)
```

### Configuração do Cliente

```javascript
// frontend/src/config.js
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000',
  TIMEOUT_MS: 180000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY_MS: 1000
};
```

---

## 🎨 Design System

### Cores (Design Tokens)
```css
--color-primary: #0066cc;
--color-success: #28a745;
--color-warning: #ffc107;
--color-error: #dc3545;
--color-text-primary: #1a1a1a;
--color-text-secondary: #666666;
--color-bg-primary: #ffffff;
--color-bg-secondary: #f5f5f5;
--color-border: #e0e0e0;
--color-iteration-bg: #f0f8ff;
--color-metric-good: #d4edda;
--color-metric-warning: #fff3cd;
```

### Tipografia
```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.125rem;
--font-size-xl: 1.25rem;
--font-weight-regular: 400;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Espaçamento
```css
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;
```

---

## ✅ Próximos Passos

1. **Revisão**: Confirmar arquitetura com equipe
2. **Implementação**: Seguir ordem de componentes (veja 01-COMPONENTES-PRINCIPAIS.md)
3. **Testes**: Unit tests para cada componente
4. **Integração**: Conectar com backend (veja 02-INTEGRACAO-WEBSOCKET.md)
5. **Performance**: Profiling e otimização

---

**Referências Cruzadas**:
- Backend: `/docs/09-IMPLEMENTACAO-PRATICA.md`
- UX/Wireframes: `/frontend/docs/03-FLUXO-DE-USUARIO.md`
- Componentes Detalhados: `/frontend/docs/01-COMPONENTES-PRINCIPAIS.md`
- WebSocket: `/frontend/docs/02-INTEGRACAO-WEBSOCKET.md`
