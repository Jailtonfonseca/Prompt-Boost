# 03 - Fluxo de Usuário & UX/Wireframes

## 🎯 Visão Geral

Este documento descreve a jornada do usuário ao usar o Prompt-Boost v2.0, com ênfase em fluxos de interação, wireframes ASCII e padrões de UX.

---

## 👤 Personas

### Persona 1: Desenvolvedor
- **Objetivo**: Melhorar prompts para gerar código de qualidade
- **Técnicas preferidas**: Self-Refine, ToT
- **Modo**: Single technique com streaming

### Persona 2: Pesquisador
- **Objetivo**: Resolver problemas matemáticos/lógicos complexos
- **Técnicas preferidas**: ToT, Debate, AutoFormalization
- **Modo**: Comparison mode para entender trade-offs

### Persona 3: Content Creator
- **Objetivo**: Otimizar prompts de copywriting/marketing
- **Técnicas preferidas**: Self-Refine, Debate
- **Modo**: Quick iterations com feedback visual

---

## 🗺️ Fluxo Principal: Melhoria Iterativa

```
┌─────────────────────────────────────────────────────────────────┐
│ INÍCIO                                                          │
│ Usuário abre http://localhost:3000                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Input do Prompt Original                               │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Paste your prompt here...                                   │ │
│ │ ═════════════════════════════════════════════════════════════ │
│ │ Escreva um código que parseia JSON                           │ │
│ │                                                             │ │
│ │ [char count: 42]                                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ CTA: "🚀 Melhorar Prompt" [enabled] "📋 Colar Exemplo"        │
└────────────────────┬────────────────────────────────────────────┘
                     │ Usuário clica "Melhorar Prompt"
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Selecionar Técnica (Opcional - pode ter default)       │
│                                                                 │
│ ┌─ Técnica de Raciocínio ─────────────────────────────────────┐ │
│ │                                                             │ │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│ │ │ 🔄       │  │ 🌳       │  │ 🕸️       │  │ 🎲       │    │ │
│ │ │Self-    │  │Tree of   │  │Graph of  │  │LLM-MCTS  │    │ │
│ │ │Refine   │  │Thoughts  │  │Thoughts  │  │          │    │ │
│ │ │SELECTED │  │          │  │          │  │          │    │ │
│ │ └──────────┘  └──────────┘  └──────────┘  └──────────┘    │ │
│ │                                                             │ │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐                  │ │
│ │ │ 🗣️       │  │ ✓        │  │ 📐       │                  │ │
│ │ │Debate    │  │Alignment │  │AutoForm  │                  │ │
│ │ │          │  │          │  │          │                  │ │
│ │ └──────────┘  └──────────┘  └──────────┘                  │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ ⚙️ Configurações ▶ ──────────────────────────────────────┐ │
│ │ [Expandido]                                               │ │
│ │ Provider: OpenAI ▼        Model: gpt-4o ▼               │ │
│ │ Temperature: 0.7 |━━━●━━━━━━|                             │ │
│ │ Max Iterations: 3 |━━━●━━━━━━|                            │ │
│ │ Max Tokens: 10000 [input: 10000]                          │ │
│ │                                                            │ │
│ │ ☐ Use Reasoning Effort (o1-preview)                      │ │
│ │ Seed: [empty]                                            │ │
│ │                                                            │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ☐ Modo Comparação (testar múltiplas técnicas)                 │
│                                                                 │
│ CTA: "🚀 Melhorar Prompt" [enabled]                            │
└────────────────────┬────────────────────────────────────────────┘
                     │ Usuário clica "Melhorar Prompt"
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Processamento em Streaming                             │
│                                                                 │
│ ┌─ Status em Tempo Real ──────────────────────────────────────┐ │
│ │ 🔌 Conectado | 🧠 Pensando...                              │ │
│ │                                                             │ │
│ │ ┌─ Métricas em Tempo Real ──────────────────────────────┐  │ │
│ │ │ Iteração: 1/3                                         │  │ │
│ │ │ Tokens: 320/10000                                     │  │ │
│ │ │ Tempo: 3.5s                                           │  │ │
│ │ │ Progresso: [██░░░░░░░░░░░░░░░░░] 20%                │  │ │
│ │ └────────────────────────────────────────────────────────┘  │ │
│ │                                                             │ │
│ │ ┌─ Iteração #1 ──────────────────────────────────────────┐  │ │
│ │ │ Score: 65% | 280 tokens                              │  │ │
│ │ │ ▶ [clique para expandir]                             │  │ │
│ │ └────────────────────────────────────────────────────────┘  │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ CTA: "⏹️ Cancelar" [enabled]                                   │
│                                                                 │
│ [Usuario pode monitorar progresso sem bloqueio]                │
└────────────────────┬────────────────────────────────────────────┘
                     │ Backend completa iteração 1
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3b: Iterações Continuam em Tempo Real                     │
│                                                                 │
│ ┌─ Status ───────────────────────────────────────────────────┐ │
│ │ 🧠 Pensando... | Iteração: 2/3                            │ │
│ │                                                             │ │
│ │ Progresso: [████████░░░░░░░░░░░░░░░░] 50%                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ Iterações Completadas ─────────────────────────────────────┐ │
│ │                                                             │ │
│ │ ┌─ Iteração #1 ──────────────────────────────────────────┐ │ │
│ │ │ Score: 65% | 280 tokens | ▶                           │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ │ ┌─ Iteração #2 ──────────────────────────────────────────┐ │ │
│ │ │ Score: 78% | 320 tokens | ▼ [expandido]               │ │ │
│ │ │                                                         │ │ │
│ │ │ Gerado (3 candidatos):                                │ │ │
│ │ │  - Candidato 1: Score 72%                             │ │ │
│ │ │    Um parser é...                                     │ │ │
│ │ │                                                         │ │ │
│ │ │  - Candidato 2: Score 78% ← SELECIONADO             │ │ │
│ │ │    Um parser JSON é...                                │ │ │
│ │ │                                                         │ │ │
│ │ │  - Candidato 3: Score 65%                             │ │ │
│ │ │    Escreva um parser...                               │ │ │
│ │ │                                                         │ │ │
│ │ │ ⚠️ Crítica do Modelo:                                  │ │ │
│ │ │ "Bem melhor! Mas falta validação de erros"            │ │ │
│ │ │                                                         │ │ │
│ │ │ ✓ Melhor Selecionado:                                 │ │ │
│ │ │ "Um parser JSON é um programa que..."                 │ │ │
│ │ │                                                         │ │ │
│ │ └────────────────────────────────────────────────────────┘ │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────────┘
                     │ Backend completa final
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Resultado Final & Métricas                             │
│                                                                 │
│ ┌─ Status ───────────────────────────────────────────────────┐ │
│ │ ✅ Concluído | Iteração: 3/3 | 100%                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ Métricas da Execução ──────────────────────────────────────┐ │
│ │                                                             │ │
│ │ 🔄 Iterações: 3      📊 Tokens: 4,200      ⏱️ Tempo: 15s  │ │
│ │ ⭐ Qualidade: 92%    📈 RER Score: 1.84    🧠 Técnica: ... │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ Consumo por Iteração ──────────────────────────────────────┐ │
│ │ Iter.  | Tokens | Score | Tempo (ms)                       │ │
│ │ ────────────────────────────────────────────────────────── │ │
│ │ #1     | 280    | 65%   | 4200                             │ │
│ │ #2     | 320    | 78%   | 5100                             │ │
│ │ #3     | 520    | 92%   | 5700                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ Prompt Melhorado ──────────────────────────────────────────┐ │
│ │                                                             │ │
│ │ Escreva em Python um parser JSON otimizado que valida      │ │
│ │ entrada corretamente e trata erros de sintaxe com         │ │
│ │ mensagens amigáveis. Inclua exemplos de entrada/saída.    │ │
│ │                                                             │ │
│ │ [📋 Copiar] [⬇️ Download] [🔄 Melhorar Novamente]          │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─ Ações ─────────────────────────────────────────────────────┐ │
│ │ [🔗 Compartilhar] [📚 Publicar na Galeria] [❤️ Favoritar] │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │ Usuário pode:
                     ├─→ Copiar resultado
                     ├─→ Refinar novamente com novas config
                     ├─→ Compartilhar com link
                     └─→ Publicar na galeria pública
```

---

## 🔀 Fluxo Alternativo: Modo Comparação

```
User selects "Modo Comparação" ☑️

↓

"🚀 Melhorar Prompt" triggers MULTIPLE techniques in parallel:
  ├─ Self-Refine
  ├─ Tree of Thoughts
  ├─ Debate
  └─ AutoFormalization (opcional)

↓

Results displayed in TABS/GRID view

┌─ Comparação de Técnicas ────────────────────────────────────┐
│                                                             │
│ [Self-Refine] [ToT] [Debate] [Alignment]                  │
│                                                             │
│ ┌─ Self-Refine (Selected) ───────────────────────────────┐ │
│ │ Iterações: 3 | Tokens: 4,200 | Tempo: 15s             │ │
│ │ Qualidade: 92% | RER: 1.84                            │ │
│ │                                                        │ │
│ │ "Escreva em Python um parser JSON otimizado..."       │ │
│ │                                                        │ │
│ │ [Ver Detalhes] [Copiar]                              │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Tabela Comparativa ────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Técnica    | Qualidade | Tokens | Tempo  | RER         │ │
│ │ ───────────────────────────────────────────────────── │ │
│ │ Self-Refine| 92%  ⭐   | 4,200  | 15s   | 1.84       │ │
│ │ ToT        | 88%       | 6,100  | 22s   | 1.44       │ │
│ │ Debate     | 95%  ⭐⭐ | 7,800  | 28s   | 1.22       │ │
│ │ Alignment  | 90%       | 5,200  | 18s   | 1.73       │ │
│ │                                                         │ │
│ │ Recomendado: Debate (maior qualidade)                 │ │
│ │             Self-Refine (melhor eficiência RER)       │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Fluxo de Erro & Recovery

```
Error Scenario 1: Timeout
┌─────────────────────────────────────────────────────────┐
│ ❌ Erro: Timeout Excedido                              │
│                                                         │
│ A execução levou mais de 120 segundos e foi cancelada. │
│                                                         │
│ 💡 Sugestões:                                           │
│    • Reduza max_iterations (ex: 2 em vez de 5)        │
│    • Aumente max_time_ms nas configurações            │
│    • Tente uma técnica mais rápida (Self-Refine)      │
│                                                         │
│ [🔄 Tentar Novamente] [⚙️ Ajustar Configurações]       │
└─────────────────────────────────────────────────────────┘

Error Scenario 2: Conexão WebSocket Perdida
┌─────────────────────────────────────────────────────────┐
│ ⚠️ Aviso: Conexão Perdida                              │
│                                                         │
│ A conexão com o servidor foi interrompida.             │
│ Tentando reconectar... (1/3)                           │
│                                                         │
│ Se o problema persistir:                              │
│ • Verifique sua conexão de internet                   │
│ • Recarregue a página                                 │
│ • Limpe o cache do navegador                          │
│                                                         │
│ [🔄 Reconectar Manualmente] [🔄 Recarregar Página]     │
└─────────────────────────────────────────────────────────┘

Error Scenario 3: Invalid API Key
┌─────────────────────────────────────────────────────────┐
│ ❌ Erro: API Key Inválida                              │
│                                                         │
│ A chave do OpenAI não está configurada ou é inválida. │
│                                                         │
│ [⚙️ Configurar API Key] [📖 Ver Documentação]          │
└─────────────────────────────────────────────────────────┘
```

---

## 🧬 Cancelamento de Operação

```
While streaming (User clicks "⏹️ Cancelar"):

1. Send WebSocket message: {action: "cancel", execution_id: "..."}

2. Backend stops processing immediately

3. Frontend shows:
   ┌─────────────────────────────────────────────────────┐
   │ ⏹️ Cancelado pelo usuário                            │
   │                                                     │
   │ Processamento foi interrompido em:                 │
   │ Iteração: 2/3 | Tokens utilizados: 2,100/10,000   │
   │                                                     │
   │ Resultados parciais (2 iterações):                │
   │ ┌─ Iteração #1 ───┐                               │
   │ │ Score: 65%      │                               │
   │ └─────────────────┘                               │
   │ ┌─ Iteração #2 ───┐                               │
   │ │ Score: 78%      │                               │
   │ └─────────────────┘                               │
   │                                                     │
   │ [💾 Salvar Resultado Parcial] [🚀 Tentar Novamente]│
   └─────────────────────────────────────────────────────┘

4. User can:
   - Save partial result
   - Retry with different config
   - Close and start fresh
```

---

## 📱 Responsividade (Desktop → Mobile)

### Desktop (≥1200px)
```
┌─ Full Layout (3-column) ─────────────────────┐
│ Input (left) | Options (center) | Results (right)
└──────────────────────────────────────────────┘
```

### Tablet (768px - 1199px)
```
┌─ Stacked (2-column) ──────────────────┐
│ Input (top)                           │
├───────────────────────────────────────┤
│ Options (left) | Results (right)      │
└───────────────────────────────────────┘
```

### Mobile (<768px)
```
┌─ Full-width stacked ──────────────────────┐
│ Input                                    │
├──────────────────────────────────────────┤
│ Options (collapsed by default)           │
├──────────────────────────────────────────┤
│ Results (scrollable)                     │
└──────────────────────────────────────────┘
```

---

## ♿ Acessibilidade

### WCAG 2.1 AA Compliance

- **Contraste**: Razão mínima 4.5:1 para texto
- **Focus**: Todos elementos interativos com `:focus-visible`
- **ARIA Labels**: `aria-label` em botões sem texto
- **Keyboard Navigation**: Tab order lógico
- **Screen Readers**: Anúncio de status com `role="status"`

### Exemplos

```javascript
// ARIA Live Region para status
<div role="status" aria-live="polite" aria-atomic="true">
  {streamingResult.status === 'thinking' && 'Processando iteração 1 de 3...'}
</div>

// Botão com label acessível
<button aria-label="Cancelar processamento recursivo">
  ⏹️
</button>

// Formulário com labels
<label htmlFor="technique-select">Técnica de Raciocínio</label>
<select id="technique-select">...</select>
```

---

## 🎮 Interações & Feedback Visual

### Botão Melhorar Prompt

```
Estado Padrão:
┌─ 🚀 Melhorar Prompt ─┐
└──────────────────────┘
Cursor: pointer, Background: #0066cc, Text: white

Hover:
┌─ 🚀 Melhorar Prompt ─┐ ← Background mais escuro
└──────────────────────┘    Shadow elevado

Active (Press):
┌─ 🚀 Melhorar Prompt ─┐ ← Transform scale(0.98)
└──────────────────────┘

Disabled (During Processing):
┌─ 🚀 Melhorar Prompt ─┐ ← Opacity 0.5
└──────────────────────┘    Cursor: not-allowed
```

### Slider de Temperatura

```
Visual Feedback:
Temperature: 0.7 ────────────────────────
             |
             0.0 (Determinístico) ← │ ← 2.0 (Criativo)
                        Tooltip mostra valor atual
                        
On change:
  - Thumb muda cor (interpolação gradient)
  - Label atualiza em tempo real
  - Sugestão de uso aparece abaixo
```

---

## 📊 Estados do Progresso

```css
/* CSS para ProgressBar */
@keyframes progress-animate {
  0% { background-position: -1000px 0; }
  100% { background-position: 0 0; }
}

.progress-bar {
  background: linear-gradient(
    90deg,
    #0066cc 0%,
    #0099ff 50%,
    #0066cc 100%
  );
  background-size: 200% 100%;
  animation: progress-animate 1.5s ease-in-out infinite;
  height: 4px;
  border-radius: 2px;
}

/* Diferentes cores por status */
.progress-bar.thinking { background: linear-gradient(90deg, #0066cc, #0099ff); }
.progress-bar.yielding { background: linear-gradient(90deg, #28a745, #5ac05e); }
.progress-bar.error { background: linear-gradient(90deg, #dc3545, #ff6b7a); }
```

---

## 📋 Checklist de Implementação UX

- [ ] Wireframes criados em Figma/Adobe XD
- [ ] Prototipo interativo testado
- [ ] Testes de usabilidade com 5+ usuários
- [ ] WCAG 2.1 AA compliance verificado
- [ ] Responsividade testada em 3+ breakpoints
- [ ] Dark mode considerado (opcional)
- [ ] Loading states refinados
- [ ] Error messages testadas
- [ ] Onboarding/tutorial criado
- [ ] Documentação de UX patterns

---

**Referências Cruzadas**:
- Componentes: `/frontend/docs/01-COMPONENTES-PRINCIPAIS.md`
- WebSocket: `/frontend/docs/02-INTEGRACAO-WEBSOCKET.md`
- Design System: `/frontend/docs/00-ARQUITETURA-FRONTEND.md#-design-system`
