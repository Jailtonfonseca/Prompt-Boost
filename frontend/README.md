# Prompt-Boost Frontend v2.0

React frontend para a plataforma de raciocínio recursivo **Prompt-Boost**.

> Transforme seus prompts com 7 técnicas avançadas de raciocínio LLM em tempo real.

## 📚 Documentação

### 📖 [Documentação Técnica Completa](./docs/INDEX.md)

Leia a documentação em ordem:

1. **[00-ARQUITETURA-FRONTEND.md](./docs/00-ARQUITETURA-FRONTEND.md)** - Visão geral da arquitetura
2. **[01-COMPONENTES-PRINCIPAIS.md](./docs/01-COMPONENTES-PRINCIPAIS.md)** - Specs de componentes React
3. **[02-INTEGRACAO-WEBSOCKET.md](./docs/02-INTEGRACAO-WEBSOCKET.md)** - WebSocket em tempo real
4. **[03-FLUXO-DE-USUARIO.md](./docs/03-FLUXO-DE-USUARIO.md)** - UX/Wireframes
5. **[04-ESTADO-GLOBAL-E-HOOKS.md](./docs/04-ESTADO-GLOBAL-E-HOOKS.md)** - State management
6. **[05-CASOS-DE-USO-FRONTEND.md](./docs/05-CASOS-DE-USO-FRONTEND.md)** - Exemplos práticos

## 🚀 Quick Start

### Instalação

```bash
npm install
```

### Dependências Principais

```json
{
  "react": "^19.1.1",
  "zustand": "^4.4.0",
  "axios": "^1.6.0",
  "ws": "^8.13.0",
  "react-markdown": "^9.0.0",
  "recharts": "^2.10.0"
}
```

### Desenvolvimento

```bash
npm start
```

Abre [http://localhost:3000](http://localhost:3000)

### Build para Produção

```bash
npm run build
```

### Testes

```bash
npm test
```

## 🏗️ Arquitetura

```
src/
├── components/          # Componentes React
│   ├── MainPage.js
│   ├── RecursiveOptions/
│   ├── Results/
│   └── Common/
│
├── hooks/              # Custom hooks
│   ├── useRecursiveThinking.js
│   ├── useWebSocket.js
│   ├── useStreamingResult.js
│   └── useAsync.js
│
├── store/              # Estado (Zustand)
│   ├── recursionStore.js
│   └── uiStore.js
│
├── api/                # Clientes HTTP/WebSocket
│   ├── api.js
│   ├── websocketClient.js
│   └── recursiveApi.js
│
├── styles/             # Estilos globais
│   └── variables.css
│
└── utils/              # Utilidades
    ├── constants.js
    ├── formatters.js
    └── validators.js
```

## 🧠 Técnicas Suportadas

1. **Self-Refine** 🔄 - Melhoria iterativa via crítica
2. **Tree of Thoughts** 🌳 - Exploração em árvore
3. **Graph of Thoughts** 🕸️ - Exploração em grafo
4. **LLM-MCTS** 🎲 - Monte Carlo Tree Search
5. **Multi-Agent Debate** 🗣️ - Múltiplos agentes
6. **Recursive Alignment** ✓ - Verificação formal
7. **AutoFormalization** 📐 - Prova formal (Lean4)

## 🔌 Integração com Backend

### URL Base
```javascript
// Configurar em .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Endpoints Esperados
```
POST /api/improve-prompt-recursive
WS  /ws/recursive
```

Veja [02-INTEGRACAO-WEBSOCKET.md](./docs/02-INTEGRACAO-WEBSOCKET.md) para formatos de mensagem.

## 🎨 Design System

### Cores
```css
--color-primary: #0066cc;
--color-success: #28a745;
--color-warning: #ffc107;
--color-error: #dc3545;
```

Veja [00-ARQUITETURA-FRONTEND.md](./docs/00-ARQUITETURA-FRONTEND.md#-design-system) para tokens completos.

## ♿ Acessibilidade

- WCAG 2.1 AA compliance
- Keyboard navigation completa
- Screen reader support
- High contrast mode

Veja [03-FLUXO-DE-USUARIO.md](./docs/03-FLUXO-DE-USUARIO.md#-acessibilidade) para detalhes.

## 📊 State Management

### Zustand Stores

```javascript
import { useRecursionStore, useUIStore } from './store';

const store = useRecursionStore();
const ui = useUIStore();
```

Veja [04-ESTADO-GLOBAL-E-HOOKS.md](./docs/04-ESTADO-GLOBAL-E-HOOKS.md) para exemplos completos.

## 🪝 Custom Hooks

```javascript
import { useRecursiveThinking } from './hooks';
import { useWebSocket } from './hooks';
import { useStreamingResult } from './hooks';

const { improve, cancel, result, status } = useRecursiveThinking();
```

## 🧪 Testing

```bash
npm test -- --coverage
```

Estrutura de testes:
```
src/__tests__/
├── hooks/
├── components/
└── utils/
```

## 📈 Performance

- Code splitting com React.lazy()
- Memoização com React.memo()
- Lazy loading de componentes pesados
- Virtual scrolling para listas grandes

Veja [00-ARQUITETURA-FRONTEND.md](./docs/00-ARQUITETURA-FRONTEND.md#-arquitetura-de-componentes) para detalhes.

## 🐛 Troubleshooting

### WebSocket não conecta
1. Verifique `REACT_APP_WS_URL` no .env
2. Confirme backend está rodando em `ws://localhost:8000`
3. Verifique logs do navegador (DevTools)

### Estado não persiste
- Verifique localStorage está habilitado
- Limpe cache: `localStorage.clear()`

### Componentes lentos
- Abra DevTools → Performance
- Verifique re-renders desnecessários
- Use React Profiler

## 📱 Responsividade

Testado em:
- Desktop (1920px+)
- Tablet (768px - 1199px)
- Mobile (<768px)

Veja [03-FLUXO-DE-USUARIO.md](./docs/03-FLUXO-DE-USUARIO.md#-responsividade-desktop--mobile) para detalhes.

## 🔗 Links Úteis

- [Documentação Técnica](./docs/INDEX.md)
- [Backend Documentation](../docs/09-IMPLEMENTACAO-PRATICA.md)
- [React Documentation](https://react.dev)
- [Zustand Docs](https://github.com/pmndrs/zustand)

## 📝 Changelog

### v2.0.0
- ✅ Documentação completa (6 arquivos)
- ✅ Componentes React com specs
- ✅ WebSocket integration
- ✅ Zustand state management
- ✅ Custom hooks
- ✅ 7 casos de uso práticos

## 📄 Licença

MIT

## 👥 Contribuições

Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para diretrizes.

---

**Última Atualização**: Abril 2026  
**Status**: ✅ Pronto para Implementação
