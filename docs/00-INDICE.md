# 📚 Índice de Técnicas de Raciocínio Recursivo - Prompt-Boost 2026

## 🎯 Visão Geral

Este conjunto de documentação descreve a implementação de **7 técnicas de pensamento recursivo** no Prompt-Boost, transformando-o em uma plataforma de raciocínio profundo (reasoning platform). Cada técnica é documentada com:

- ✅ Teoria e mecanismo operacional
- ✅ Pseudocódigo e arquitetura
- ✅ Guia de implementação no FastAPI + React
- ✅ Métricas de avaliação e benchmarks
- ✅ Casos de uso reais

---

## 📖 Índice de Documentos

### **Fundações**

| Doc | Título | Foco | Tempo de Leitura |
|-----|--------|------|------------------|
| **01** | [Fundamentos de Raciocínio Recursivo](./01-FUNDAMENTOS-RECURSIVOS.md) | Loop recursivo genérico, arquitetura geral, ciclo de vida | 20 min |
| **02** | [Comparação de Técnicas](./02-COMPARACAO-TECNICAS.md) | Matriz de decisão, quando usar cada técnica | 15 min |

### **Técnicas Principais**

| Doc | Técnica | Mecanismo | Melhor Para | Complexidade |
|-----|---------|-----------|------------|--------------|
| **03** | [Tree of Thoughts (ToT) & Graph of Thoughts (GoT)](./03-TOT-E-GOT.md) | Exploração de múltiplos caminhos + poda | Raciocínio lógico, planejamento, matemática | Alto |
| **04** | [Self-Refine & Reflexion](./04-SELF-REFINE-E-REFLEXION.md) | Feedback loops + memória episódica | Código, escrita, correção factual | Médio |
| **05** | [Recursive Self-Alignment (NSRSA)](./05-RECURSIVE-ALIGNMENT.md) | Verificação simbólica + feedback formal | Alinhamento, segurança lógica | Muito Alto |
| **06** | [LLM-MCTS (Planejamento Integrado)](./06-LLM-MCTS.md) | MCTS com LLM como heurística | Decisão sequencial, planejamento, robótica | Muito Alto |
| **07** | [Multi-Agent Debate & Consenso](./07-MULTI-AGENT-DEBATE.md) | Múltiplos agentes + debate estruturado | Ética, medicina, direito, fact-checking | Alto |
| **08** | [Autoformalização & Prova Formal](./08-AUTOFORMALIZAÇÃO.md) | NL → Formal + verificação simbólica | Matemática, física, código formal | Crítico |

### **Aplicação Prática**

| Doc | Conteúdo | Público |
|-----|----------|---------|
| **09** | [Guia de Implementação](./09-IMPLEMENTACAO-PRATICA.md) | Desenvolvedores: endpoints, DB, integração |
| **10** | [Métricas & Benchmarks (2026)](./10-METRICAS-E-BENCHMARKS.md) | Pesquisadores: KPIs, curvas, avaliação |
| **11** | [Casos de Uso & Exemplos](./11-CASOS-DE-USO.md) | Todos: exemplos vivos, tutoriais |

---

## 🏗️ Arquitetura Geral do Sistema

```
┌──────────────────────────────────────────────────────────┐
│                    PROMPT-BOOST 2026                     │
│              (Raciocínio Recursivo Platform)             │
└──────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
  │  Frontend   │  │  Orchestrator│  │  Providers  │
  │  (React 19) │  │  (FastAPI)   │  │  (Multi-LLM)│
  └─────────────┘  └─────────────┘  └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌───────────────┐ ┌──────────────┐ ┌───────────────┐
  │ ToT/GoT Engine│ │Self-Refine   │ │ MCTS Planner  │
  │               │ │+ Reflexion   │ │               │
  └───────────────┘ └──────────────┘ └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐
  │ Alignment   │  │Multi-Agent Debate│  │Autoformal Prover│
  │ Verifier    │  │                  │  │                 │
  └─────────────┘  └──────────────────┘  └────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  Memory & State Layer   │
              │  (Database, Caching)    │
              └─────────────────────────┘
```

---

## 🚀 Quick Start por Técnica

### 1️⃣ **Para Começar: Self-Refine**
- **Complexidade**: ⭐⭐ (Baixa)
- **Impacto**: ⭐⭐⭐⭐ (Alto)
- **Tempo para produção**: 1-2 semanas
- **Leia primeiro**: [04-SELF-REFINE-E-REFLEXION.md](./04-SELF-REFINE-E-REFLEXION.md)

### 2️⃣ **Próximo Passo: Tree of Thoughts**
- **Complexidade**: ⭐⭐⭐ (Média)
- **Impacto**: ⭐⭐⭐⭐⭐ (Máximo em raciocínio)
- **Tempo para produção**: 2-3 semanas
- **Leia**: [03-TOT-E-GOT.md](./03-TOT-E-GOT.md)

### 3️⃣ **Avançado: Multi-Agent Debate**
- **Complexidade**: ⭐⭐⭐⭐ (Alta)
- **Impacto**: ⭐⭐⭐⭐ (Muito bom para consenso)
- **Tempo para produção**: 3-4 semanas
- **Leia**: [07-MULTI-AGENT-DEBATE.md](./07-MULTI-AGENT-DEBATE.md)

### 4️⃣ **Pesquisa: LLM-MCTS & Autoformalização**
- **Complexidade**: ⭐⭐⭐⭐⭐ (Crítica)
- **Impacto**: ⭐⭐⭐⭐⭐ (Máximo para problemas estruturados)
- **Tempo para produção**: 4-6 semanas
- **Leia**: [06-LLM-MCTS.md](./06-LLM-MCTS.md) e [08-AUTOFORMALIZAÇÃO.md](./08-AUTOFORMALIZAÇÃO.md)

---

## 📊 Comparação Rápida de Técnicas

```
Técnica              │ Domínio     │ Ganho   │ Custo CPU │ Iterações Típicas
─────────────────────┼─────────────┼─────────┼───────────┼──────────────────
ToT/GoT              │ Raciocínio  │ +24pp   │ Alto      │ 3-5
Self-Refine          │ Código      │ +30%    │ Médio     │ 2-3
Reflexion            │ Agentes     │ 2-4x    │ Baixo     │ 1-2
Recursive Alignment  │ Segurança   │ >90%    │ Muito     │ 3-5
LLM-MCTS             │ Planejamento│ +35%    │ Muito     │ 4-8
Multi-Agent Debate   │ Consenso    │ +40%    │ Muito     │ 2-4
Autoformalização     │ Matemática  │ 60-85%  │ Crítico   │ 5-10
```

---

## 🎓 Aprender por Objetivo

### 📝 "Quero melhorar a qualidade de prompts de programação"
→ Leia: **Self-Refine** (Doc 04) → **ToT** (Doc 03)

### 🤖 "Quero criar um agente autoaprendizado"
→ Leia: **Reflexion** (Doc 04) → **LLM-MCTS** (Doc 06)

### 🎯 "Quero resolver problemas de raciocínio complexo"
→ Leia: **ToT/GoT** (Doc 03) → **MCTS** (Doc 06)

### 🔐 "Quero garantir correção e alinhamento formal"
→ Leia: **Recursive Alignment** (Doc 05) → **Autoformalização** (Doc 08)

### 🗳️ "Quero consenso robusto e redução de viés"
→ Leia: **Multi-Agent Debate** (Doc 07)

---

## 🔄 Roadmap de Implementação (Prompt-Boost 2.0)

### **Fase 1 - Fundação (Semana 1-2)**
- [ ] Leitura completa de docs 01-02
- [ ] Refatoração da arquitetura `recursion.py`
- [ ] Setup de endpoints básicos no FastAPI
- [ ] Testes unitários de loop recursivo genérico

### **Fase 2 - Self-Refine (Semana 3-4)**
- [ ] Implementação de Self-Refine e Reflexion
- [ ] Endpoints `/api/improve-with-self-refine` e `/api/improve-with-reflexion`
- [ ] Frontend com UI de seleção de técnica
- [ ] Testes e integração

### **Fase 3 - ToT & GoT (Semana 5-7)**
- [ ] Implementação completa de ToT/GoT
- [ ] Algoritmo de poda e seleção de branches
- [ ] Visualização de árvore no frontend
- [ ] Benchmarks contra baseline

### **Fase 4 - Avançado (Semana 8-12)**
- [ ] Multi-Agent Debate
- [ ] LLM-MCTS com integração
- [ ] Recursive Alignment com verificadores simbólicos
- [ ] Autoformalização (beta)

### **Fase 5 - Produção (Semana 13+)**
- [ ] Métricas e monitoring
- [ ] Deploy em produção
- [ ] Documentação de usuário final
- [ ] Otimizações de performance

---

## 🔧 Requisitos Técnicos

### Backend
- Python 3.9+
- FastAPI com suporte a streaming (WebSocket)
- Pydantic V2
- SQLite com índices otimizados
- **Novos**: `z3-solver` (verificação), `networkx` (grafos), `openai[reasoning]`

### Frontend
- React 19+
- React Router
- WebSocket client
- Visualização de grafos (Cytoscape.js)
- Editor de código (Monaco)

### Provedores Suportados
- **OpenAI**: GPT-4o, o1 (reasoning)
- **Google**: Gemini 2.0 (extended thinking)
- **xAI**: Grok-2
- **Groq**: LLaMA-3.1-70b
- **OpenRouter**: Multi-model

---

## 📈 Métricas de Sucesso

Cada técnica será avaliada por:

1. **Accuracy**: Taxa de sucesso no benchmark específico
2. **Latency**: Tempo médio por iteração
3. **Token Efficiency**: Tokens gastos por problema resolvido
4. **User Satisfaction**: Feedback qualitativo
5. **Production Readiness**: Estabilidade e custo

---

## 🤝 Como Contribuir

1. Leia o documento relevante da técnica
2. Implemente o pseudocódigo em `recursion.py`
3. Adicione testes em `test_main.py`
4. Crie um PR com descrição técnica
5. Atualize este índice com progresso

---

## 📞 Suporte & Feedback

- **Issues técnicas**: Abra issue no GitHub com tag `[recursive-thinking]`
- **Sugestões**: Crie discussion em `Discussões` (GitHub)
- **Pesquisa**: Cite este documento em papers/blogs

---

## 📜 Licença

Documentação sob GPL-3.0 (mesmo do Prompt-Boost)

**Última atualização**: 2026-04-10
**Versão**: 1.0.0 (Documentação de Raciocínio Recursivo)
