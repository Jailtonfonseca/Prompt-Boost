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
│   ├── api.js          # API v1 compatibility layer
│   ├── websocketClient.js
│   └── recursiveApi.js
│
├── styles/             # Estilos globais
│   └── variables.css
│
├── utils/              # Utilidades
│   ├── constants.js
│   ├── formatters.js
│   └── validators.js
│
└── utils/
    └── reportWebVitals.js  # Performance metrics (create-react-app)
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
// Configurar em .env ou via docker-compose
REACT_APP_API_URL=http://localhost:8000/api
```

### Endpoints API v1 (Compatibility Layer)
O backend expõe endpoints de compatibilidade para o frontend v1.x:

```
GET  /api/providers           # Lista provedores disponíveis
GET  /api/config              # Retorna configuração atual
POST /api/config              # Salva configuração
POST /api/config/test-provider # Testa conexão com provedor
POST /api/improve-prompt      # Melhora um prompt
POST /api/prompts            # Salva um par de prompts
GET  /api/prompts/{id}        # Recupera prompt pelo ID
GET  /api/gallery            # Lista prompts públicos
```

### Endpoints API v2 (Recursion)
```
POST /api/recursion/execute   # Executa técnica de recursão
GET  /api/recursion/techniques # Lista técnicas disponíveis
GET  /api/recursion/sessions  # Lista sessões ativas
WS   /ws/recursion            # WebSocket para streaming
```

### Docker - URL do Backend
Quando rodando via Docker Compose, o nginx faz proxy do frontend para o backend:

```bash
# Frontend: http://localhost:3000
# API: http://localhost:3000/api/* (proxied para backend:8000)
# Backend: http://localhost:8000 (direto)
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
1. Verifique `REACT_APP_API_URL` no .env
2. Confirme backend está rodando em `http://localhost:8000`
3. Verifique logs do navegador (DevTools)

### API 502 Bad Gateway
1. Verifique se o backend está rodando: `docker compose ps`
2. Logs do backend: `docker compose logs backend`
3. Teste direto: `curl http://localhost:8000/api/providers`

### API 404 Not Found
- O backend usa compatibility layer v1
- Certifique-se que está usando endpoints `/api/*`

### Estado não persiste
- Verifique localStorage está habilitado
- Limpe cache: `localStorage.clear()`

### Componentes lentos
- Abra DevTools → Performance
- Verifique re-renders desnecessários
- Use React Profiler

### Erro "Module not found: reportWebVitals"
- Execute: `npm install web-vitals`
- Ou crie o arquivo `src/reportWebVitals.js`:

```javascript
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
```

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

### v2.0.1 (2026-04-12)
- ✅ Compatibilidade com backend v2.0.1 (SQLite + API v1)
- ✅ Adicionado reportWebVitals.js à estrutura
- ✅ Troubleshooting atualizado com erros comuns do Docker

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
**Status**: ✅ Pronto para Produção - Docker Compose
