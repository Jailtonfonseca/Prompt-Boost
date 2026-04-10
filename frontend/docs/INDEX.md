# Frontend Documentation - Índice Mestre

## 📚 Visão Geral

Documentação técnica completa para o frontend do **Prompt-Boost v2.0** - plataforma de raciocínio recursivo com interface React.

**Versão**: 2.0.0  
**Data**: Abril 2026  
**Status**: ✅ Pronto para Implementação  

---

## 📖 Documentos (Em Ordem Recomendada)

### 1️⃣ **00-ARQUITETURA-FRONTEND.md**
- **Propósito**: Visão geral da arquitetura
- **Conteúdo**:
  - Princípios de design (reatividade, composição, performance)
  - Hierarquia de componentes (diagrama ASCII)
  - Fluxo de dados global (request-response e WebSocket)
  - State machine completa
  - Estrutura de pastas
  - Design tokens (cores, tipografia, espaçamento)
  - Dependências recomendadas (Zustand, axios, recharts)

- **Para Quem**: Arquitetos, Tech Leads
- **Quando Ler**: Primeiro, para entender o big picture

---

### 2️⃣ **01-COMPONENTES-PRINCIPAIS.md**
- **Propósito**: Documentação técnica de cada componente
- **Conteúdo**:
  - `RecursiveOptions` (container)
  - `TechniqueSelector` (7 técnicas)
  - `RecursiveSettings` (configurações avançadas)
  - `IterationVisualizer` (timeline de iterações)
  - `MetricsPanel` (KPIs e estatísticas)
  - Especificação de Props
  - Código completo + CSS
  - Exemplos de uso

- **Para Quem**: Frontend Developers, UI Engineers
- **Quando Ler**: Segundo, para começar a implementar componentes

---

### 3️⃣ **02-INTEGRACAO-WEBSOCKET.md**
- **Propósito**: Comunicação em tempo real
- **Conteúdo**:
  - Arquitetura WebSocket
  - Formatos de mensagem (cliente → servidor, servidor → cliente)
  - Implementação do `websocketClient.js`
  - Custom hooks:
    - `useWebSocket` - gerencia conexão
    - `useStreamingResult` - consome mensagens
  - Error handling e resilience
  - Reconnect automático
  - Padrão de retry com backoff exponencial

- **Para Quem**: Backend devs integrando, Frontend devs de streaming
- **Quando Ler**: Terceiro, para setup de comunicação

---

### 4️⃣ **03-FLUXO-DE-USUARIO.md**
- **Propósito**: UX/Wireframes e jornada do usuário
- **Conteúdo**:
  - 3 personas principais
  - Fluxo principal: melhoria iterativa (5 steps)
  - Fluxo alternativo: modo comparação
  - Fluxos de erro e recovery
  - Cancelamento de operação
  - Responsividade (desktop → mobile)
  - Acessibilidade (WCAG 2.1 AA)
  - Interações e feedback visual
  - Estados do progresso

- **Para Quem**: UX/UI Designers, Product Managers
- **Quando Ler**: Quarto, para validar conceitos com design

---

### 5️⃣ **04-ESTADO-GLOBAL-E-HOOKS.md**
- **Propósito**: State management
- **Conteúdo**:
  - Separação por domínio de estado
  - **Zustand store** (recomendado):
    - `useRecursionStore` - estado de execução
    - `useUIStore` - estado de UI
  - **Custom Hooks**:
    - `useRecursiveThinking` - hook principal
    - `usePersistence` - localStorage
    - `useAsync` - operações assíncronas
    - `useDebounce` - debounce de valores
  - Context API (alternativa simples)
  - Padrões de uso em componentes
  - Testes de hooks

- **Para Quem**: Frontend devs, State management specialists
- **Quando Ler**: Quinto, para setup de estado global

---

### 6️⃣ **05-CASOS-DE-USO-FRONTEND.md**
- **Propósito**: Exemplos práticos de cada use case
- **Conteúdo**:
  - **Caso 1**: Desenvolvedor melhorando prompt de código
  - **Caso 2**: Pesquisador resolvendo problema matemático
  - **Caso 3**: Modo comparação (4 técnicas simultâneas)
  - **Caso 4**: Verificação formal (Lean4)
  - **Caso 5**: Content creator (copywriting)
  - **Caso 6**: Salvando configurações
  - **Caso 7**: Análise de histórico
  - Templates para quick start

- **Para Quem**: Developers (referência), Product Managers
- **Quando Ler**: Sexto, para validar casos e testar

---

## 🗺️ Mapa de Implementação

### Fase 1: Fundação (Semanas 1-2)
```
00-ARQUITETURA → Setup projeto React
01-COMPONENTES → Criar componentes básicos
04-ESTADO     → Setup Zustand store
```

### Fase 2: Comunicação (Semanas 2-3)
```
02-WEBSOCKET  → Implementar WebSocket client
02-WEBSOCKET  → Hooks useWebSocket, useStreamingResult
01-COMPONENTES → StreamingOutput component
```

### Fase 3: Features (Semanas 3-4)
```
03-FLUXO      → Refinar UX
01-COMPONENTES → IterationVisualizer
01-COMPONENTES → MetricsPanel
```

### Fase 4: Validação (Semanas 4+)
```
05-CASOS      → Testar com casos reais
03-FLUXO      → Testes de acessibilidade
00-ARQUITETURA → Performance profiling
```

---

## 🔗 Relacionamentos Entre Documentos

```
┌─ 00-ARQUITETURA ─────────────────────────────┐
│ (Big Picture)                               │
├─ Design System                             │
├─ Component Hierarchy                       │
└─ Data Flow                                 │
    │
    ├─→ 01-COMPONENTES ──────────────────────┐
    │   (Component Specs)                    │
    │   ├─ RecursiveOptions                  │
    │   ├─ IterationVisualizer               │
    │   └─ MetricsPanel                      │
    │       │
    │       └─→ 02-WEBSOCKET ───────────────┐
    │           (Real-time Communication)   │
    │           ├─ websocketClient.js        │
    │           ├─ useWebSocket              │
    │           └─ useStreamingResult        │
    │
    ├─→ 04-ESTADO ─────────────────────────┐
    │   (State Management)                  │
    │   ├─ useRecursionStore (Zustand)      │
    │   ├─ useUIStore                       │
    │   └─ Custom Hooks                     │
    │       │
    │       └─→ 03-FLUXO ───────────────────┐
    │           (UX/Wireframes)             │
    │           ├─ Personas                 │
    │           ├─ Wireframes               │
    │           └─ State Transitions        │
    │
    └─→ 05-CASOS ──────────────────────────┐
        (Practical Examples)               │
        ├─ Developer Workflow              │
        ├─ Researcher Math                 │
        └─ Comparison Mode                 │
```

---

## 📋 Checklist de Leitura

- [ ] **00-ARQUITETURA**: Entender big picture
  - [ ] Component hierarchy
  - [ ] State machine
  - [ ] Design system

- [ ] **01-COMPONENTES**: Specs de cada componente
  - [ ] RecursiveOptions
  - [ ] IterationVisualizer
  - [ ] MetricsPanel
  - [ ] CSS completo

- [ ] **02-WEBSOCKET**: Comunicação em tempo real
  - [ ] Formatos de mensagem
  - [ ] websocketClient.js
  - [ ] useWebSocket hook
  - [ ] useStreamingResult hook

- [ ] **03-FLUXO**: UX validation
  - [ ] Personas checagem
  - [ ] Wireframes review
  - [ ] Acessibilidade

- [ ] **04-ESTADO**: State management
  - [ ] Zustand store
  - [ ] Custom hooks
  - [ ] Padrões de uso

- [ ] **05-CASOS**: Prático
  - [ ] 7 casos de uso
  - [ ] Quick start template

---

## 🚀 Quick Start para Implementadores

### 1. Setup Inicial
```bash
npm install zustand immer axios ws date-fns react-markdown recharts
```

### 2. Criar Estrutura
```bash
mkdir -p src/{components,hooks,stores,styles,utils}
```

### 3. Implementar em Ordem
1. **Stores** (04-ESTADO)
   - `store/recursionStore.js`
   - `store/uiStore.js`

2. **Hooks** (04-ESTADO + 02-WEBSOCKET)
   - `hooks/useWebSocket.js`
   - `hooks/useStreamingResult.js`
   - `hooks/useRecursiveThinking.js`
   - `api/websocketClient.js`

3. **Componentes** (01-COMPONENTES)
   - `components/RecursiveOptions/`
   - `components/Results/IterationVisualizer.js`
   - `components/Results/MetricsPanel.js`

4. **Integração** (03-FLUXO)
   - Update `MainPage.js`
   - Add `StreamingOutput.js`

### 4. Validar
- Testar com 05-CASOS
- Verificar acessibilidade (03-FLUXO)
- Performance profiling (00-ARQUITETURA)

---

## 🎓 Recursos Externos

### React & Hooks
- [React Hooks Documentation](https://react.dev/reference/react)
- [Custom Hooks Guide](https://react.dev/learn/reusing-logic-with-custom-hooks)

### State Management
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Immer (Immutability Helper)](https://immerjs.github.io/immer/)

### WebSocket
- [WebSocket API MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [ws npm package](https://www.npmjs.com/package/ws)

### Accessibility
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

### Styling
- [CSS Variables Best Practices](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [CSS Grid & Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)

---

## 📞 Suporte & Contribuições

### Reportar Issues
- Erros na documentação: [GitHub Issues](https://github.com/Jailtonfonseca/Prompt-Boost/issues)
- Sugestões: Pull Request com melhorias

### Contribuir
1. Fork o repositório
2. Crie branch (`git checkout -b docs/melhorias`)
3. Commit mudanças (`git commit -m 'Melhoria em 01-COMPONENTES'`)
4. Push (`git push origin docs/melhorias`)
5. Open Pull Request

---

## 📊 Estatísticas da Documentação

| Documento | Linhas | Seções | Exemplos | CSS |
|-----------|--------|--------|----------|-----|
| 00-ARQUITETURA | ~450 | 8 | 5 | - |
| 01-COMPONENTES | ~680 | 5 | 15+ | ~300 |
| 02-WEBSOCKET | ~520 | 6 | 8 | - |
| 03-FLUXO | ~550 | 7 | 20+ wireframes | ~100 |
| 04-ESTADO | ~680 | 6 | 12 | - |
| 05-CASOS | ~620 | 7 | 7 casos | - |
| **TOTAL** | **~3,500** | **39** | **~70** | **~400** |

---

## 🔄 Versioning

| Versão | Data | Mudanças |
|--------|------|----------|
| 2.0.0 | Abr 2026 | Documentação completa para v2.0 |
| 1.0.0 | Mar 2026 | Documentação inicial |

---

## 📝 Changelog

### v2.0.0 (Abril 2026)
- ✅ Documentação de 6 documentos (~3,500 linhas)
- ✅ Componentes React completos com código
- ✅ WebSocket integration guide
- ✅ Custom hooks e state management
- ✅ UX/Accessibility guidelines
- ✅ 7 casos de uso práticos
- ✅ Exemplos em código

---

**Última Atualização**: Abril 2026  
**Mantido por**: Prompt-Boost Team  
**Licença**: MIT
