# 02 - Comparação de Técnicas e Matriz de Decisão

## 📊 Matriz Comparativa Rápida

| Técnica | Entrada | Saída | Complexidade | Custo | Ganho | Convergência | Melhor Para |
|---------|---------|-------|--------------|-------|-------|--------------|------------|
| **ToT** | Pergunta | Árvore de pensamentos | ⭐⭐⭐ | Médio | +24pp | 3-5 it. | Raciocínio lógico |
| **Self-Refine** | Solução | Solução refinada | ⭐⭐ | Baixo | +30% | 2-3 it. | Código/escrita |
| **Reflexion** | Tarefa | Com aprendizado | ⭐⭐⭐ | Médio | 2-4x | 1-2 it. | Agentes contínuos |
| **Alignment** | Teorema | Prova válida | ⭐⭐⭐⭐ | Alto | >90% | 5-10 it. | Matemática formal |
| **LLM-MCTS** | Objetivo | Plano/ação | ⭐⭐⭐⭐ | Muito Alto | +35% | 4-8 it. | Planejamento |
| **Debate** | Questão | Consenso | ⭐⭐⭐ | Alto | +40% | 2-4 it. | Ética/medicina |
| **Autoformal** | NL teorema | Prova Lean | ⭐⭐⭐⭐⭐ | Crítico | 60-85% | 5-15 it. | Provas formais |

---

## 🎯 Matriz de Decisão (Quando Usar Qual?)

### Por Tipo de Problema

```
┌─────────────────────────────────────────────────────────┐
│  TIPO DE PROBLEMA                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ❓ FATO SIMPLES                                        │
│  └─ "Qual a capital da França?"                        │
│     ✓ Nenhuma técnica recursiva necessária             │
│     ✓ CoT baseline é suficiente                        │
│                                                          │
│  ❓ PERGUNTA COM MÚLTIPLOS PASSOS                       │
│  └─ "Quais são as 5 maiores economias?"                │
│     ✓ Self-Refine (1-2 iterações)                      │
│     ✓ CoT é benchmark                                   │
│                                                          │
│  ❓ DECISÃO ENTRE OPÇÕES                                │
│  └─ "Qual linguagem escolher para projeto?"            │
│     ✓ Multi-Agent Debate                               │
│     ✓ ToT para explorar opções                         │
│                                                          │
│  ❓ RACIOCÍNIO LÓGICO PROFUNDO                          │
│  └─ "Prove que √2 é irracional"                        │
│     ✓ ToT (exploração de caminhos)                     │
│     ✓ Autoformalização se matemática rigorosa         │
│                                                          │
│  ❓ GERAÇÃO DE CÓDIGO                                   │
│  └─ "Escreva um parser JSON otimizado"                 │
│     ✓ Self-Refine (refinar até correto)               │
│     ✓ Recursive Alignment (verificação formal)         │
│                                                          │
│  ❓ PLANEJAMENTO SEQUENCIAL                             │
│  └─ "Planejar robô para cozinhar omelete"             │
│     ✓ LLM-MCTS (estrutura busca)                       │
│     ✓ Reflexion (aprender de tentativas)              │
│                                                          │
│  ❓ REDAÇÃO/CONTEÚDO CRIATIVO                           │
│  └─ "Escreva artigo sobre IA em 2026"                 │
│     ✓ Self-Refine (refinar iterativamente)            │
│     ✓ Reflexion com memória (consistência)            │
│                                                          │
│  ❓ ANÁLISE EQUILIBRADA DE TÓPICO                       │
│  └─ "Vantagens e desvantagens do trabalho remoto"      │
│     ✓ Multi-Agent Debate                               │
│     ✓ ToT para explorar perspectivas                   │
│                                                          │
│  ❓ GARANTIA DE CORREÇÃO FORMAL                         │
│  └─ "Verificar algoritmo criptográfico"               │
│     ✓ Recursive Alignment (simbólico)                  │
│     ✓ Autoformalização em Lean4                        │
│                                                          │
│  ❓ AGENTE AUTOAPRENDIZADO                              │
│  └─ "Chatbot que melhora com tempo"                    │
│     ✓ Reflexion (com memória episódica)               │
│     ✓ Multi-Agent Debate (múltiplas visões)           │
│                                                          │
│  ❓ FACT-CHECKING                                       │
│  └─ "Esta afirmação é verdadeira?"                     │
│     ✓ Multi-Agent Debate (consenso)                    │
│     ✓ Self-Refine (iterar até confirmação)            │
└─────────────────────────────────────────────────────────┘
```

---

## 📈 Por Orçamento de Token

```
Orçamento    │ Técnica Recomendada
─────────────┼──────────────────────────────────────────────
< 1K tokens  │ Nenhuma (use baseline CoT)
1-3K         │ Self-Refine (1-2 iterações máximo)
3-10K        │ Self-Refine, Reflexion, Multi-Agent Debate
10-20K       │ ToT, Alignment, LLM-MCTS
> 20K        │ Autoformalização, LLM-MCTS profundo
```

---

## ⏱️ Por Latência Aceitável

```
Latência         │ Técnica Recomendada
─────────────────┼──────────────────────────────────────────
Real-time        │ Nenhuma recursiva (use CoT)
< 5 segundos     │ Self-Refine (1 iteração)
< 30 segundos    │ Self-Refine, Reflexion (2-3 iterações)
< 2 minutos      │ ToT, Multi-Agent Debate
> 5 minutos      │ LLM-MCTS, Autoformalização
```

---

## 🎓 Combinações Recomendadas

### Para Codificação

```
1. Self-Refine
   └─ Gerar código
   └─ Crítico identifica bugs
   └─ Refinar
   
2. +Alignment (opcional)
   └─ Se código crítico: verificar formalmente
   └─ Testes unitários automáticos
```

### Para Pesquisa Acadêmica

```
1. Multi-Agent Debate
   └─ Perspectiva 1: Pró
   └─ Perspectiva 2: Contra
   └─ Perspectiva 3: Neutra
   └─ Síntese equilibrada

2. +Self-Refine
   └─ Refinar síntese
   └─ Melhorar estrutura
```

### Para Raciocínio Complexo

```
1. ToT
   └─ Explorar múltiplos caminhos
   └─ Podar ramos fracos
   └─ Encontrar melhor caminho

2. +Autoformalização (opcional)
   └─ Se matemática: validar prova
```

### Para Agente Autoaprendiz

```
1. Reflexion
   └─ Executar tarefa
   └─ Aprender lição
   └─ Armazenar em memória
   
2. Próxima execução: recuperar lições
   └─ Convergir mais rápido
```

### Para Planejamento Robótico

```
1. LLM-MCTS
   └─ Simular múltiplas sequências de ações
   └─ Backpropagate rewards
   └─ Encontrar plano ótimo

2. +Reflexion
   └─ Aprender dos planos bem-sucedidos
```

---

## 📋 Árvore de Decisão (Simples)

```
PERGUNTA: Qual técnica usar?

├─ É uma pergunta factual simples?
│  ├─ SIM → Não use técnica recursiva (CoT é o suficiente)
│  └─ NÃO ↓
│
├─ Precisa garantia de correção formal?
│  ├─ SIM ↓
│  │  ├─ É prova matemática?
│  │  │  ├─ SIM → AUTOFORMALIZAÇÃO
│  │  │  └─ NÃO → RECURSIVE ALIGNMENT
│  │  └─ Fim
│  └─ NÃO ↓
│
├─ É questão que exige consenso/múltiplas visões?
│  ├─ SIM → MULTI-AGENT DEBATE
│  └─ NÃO ↓
│
├─ É tarefa de planejamento sequencial?
│  ├─ SIM → LLM-MCTS
│  └─ NÃO ↓
│
├─ É código ou escrita a refinar?
│  ├─ SIM ↓
│  │  ├─ É tarefa única?
│  │  │  ├─ SIM → SELF-REFINE
│  │  │  └─ NÃO → REFLEXION
│  │  └─ Fim
│  └─ NÃO ↓
│
├─ Precisa explorar múltiplos caminhos?
│  ├─ SIM → TREE OF THOUGHTS (ToT)
│  └─ NÃO → SELF-REFINE (padrão)
│
└─ Fim
```

---

## 💰 Análise de Custo-Benefício

```
Técnica          │ Investimento | Ganho    | ROI      | Viável
─────────────────┼──────────────┼──────────┼──────────┼─────────────
Self-Refine      │ ⭐           │ ⭐⭐⭐⭐  │ Excelente│ ✅ Production
ToT              │ ⭐⭐⭐       │ ⭐⭐⭐⭐  │ Ótimo    │ ✅ Production
Reflexion        │ ⭐⭐         │ ⭐⭐⭐⭐  │ Ótimo    │ ✅ Production
Alignment        │ ⭐⭐⭐⭐     │ ⭐⭐⭐⭐⭐│ Bom      │ 🟡 Research
LLM-MCTS         │ ⭐⭐⭐⭐     │ ⭐⭐⭐⭐  │ Bom      │ 🟡 Research
Multi-Agent      │ ⭐⭐⭐       │ ⭐⭐⭐⭐⭐│ Excelente│ ✅ Production
Autoformal       │ ⭐⭐⭐⭐⭐   │ ⭐⭐⭐⭐⭐│ Bom      │ 🟡 Research
```

---

## 🚀 Recomendação por Estágio

### Estágio 1: MVP (Semana 1-2)
→ **Self-Refine** apenas
- Implementação: 3-4 dias
- Impacto: Alto
- Custo: Baixo

### Estágio 2: Expansão (Semana 3-4)
→ **Self-Refine + Multi-Agent Debate**
- Adiciona perspectiva múltipla
- Bom para consenso
- Rápido de implementar

### Estágio 3: Avançado (Semana 5-8)
→ **+ ToT + Reflexion**
- Raciocínio profundo
- Agentes que aprendem
- Mais complexo

### Estágio 4: Pesquisa (Semana 9+)
→ **+ Alignment + LLM-MCTS + Autoformalização**
- Garantia formal
- Planejamento estruturado
- Alto custo computacional

---

## 🎯 Exemplos Práticos

### Caso: Gerador de Prompts para IA

```
Necessidade: "Melhorar prompts de usuários"

Solução proposta:
├─ Self-Refine (2-3 ciclos)
│  ├─ Gerar versão melhorada
│  ├─ Crítica automática
│  └─ Refinar
│
├─ Opcional: ToT
│  └─ Explorar múltiplos estilos de prompt
│
└─ ROI: 90% de usuarios satisfeitos (baseline: 40%)
```

### Caso: Verificação de Código

```
Necessidade: "Garantir código correto antes deploy"

Solução proposta:
├─ Self-Refine (código)
│  └─ Gerar + refinar iterativamente
│
├─ + Recursive Alignment (verificação formal)
│  └─ Checar propriedades críticas
│
├─ + Testes unitários
│  └─ Validar comportamento
│
└─ ROI: 95% menos bugs em produção
```

### Caso: Agente de Planejamento

```
Necessidade: "Robô executar tarefas complexas"

Solução proposta:
├─ LLM-MCTS
│  └─ Simular planos
│
├─ + Reflexion
│  └─ Aprender de tentativas
│
└─ ROI: 70% de sucesso em primeira tentativa (baseline: 20%)
```

---

## 📚 Próximos Passos

1. **Leia documentos de técnicas** na ordem de interesse
2. **Escolha 1-2 para começar** (Self-Refine recomendado)
3. **Implemente e teste** contra baseline
4. **Expanda para outras** conforme necessário

---

**Próximo**: [03-TOT-E-GOT.md](./03-TOT-E-GOT.md)
