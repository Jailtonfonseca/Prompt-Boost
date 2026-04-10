# 01 - Fundamentos de Raciocínio Recursivo

## 📚 Introdução

Este documento descreve os **fundamentos técnicos** que subjazem todas as 7 técnicas de raciocínio recursivo. Compreender este capítulo é essencial antes de mergulhar em técnicas específicas.

---

## 🔄 O Ciclo Recursivo Genérico

Todas as técnicas de raciocínio recursivo seguem uma **arquitetura abstrata comum**:

```
┌─────────────────────────────────────────────────────────┐
│                  RECURSIVE LOOP PATTERN                 │
│                                                          │
│  INPUT (prompt, context)                               │
│           │                                             │
│           ▼                                             │
│  ┌───────────────────┐                                 │
│  │ INITIALIZE STATE  │  (iteration=0, memory={}, etc)  │
│  └────────┬──────────┘                                 │
│           │                                             │
│   ╔═══════▼════════════════════════════╗               │
│   ║  WHILE not_termination_condition: ║               │
│   ╚═══════╤════════════════════════════╝               │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 1. GENERATE        │  (criar variações)           │
│    │    candidates = [] │                              │
│    │    for i in range  │                              │
│    │      to branches: │                              │
│    │      c = model    │                              │
│    │      .generate()   │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 2. EVALUATE        │  (avaliar cada uma)          │
│    │    scores =        │                              │
│    │    evaluator       │                              │
│    │    (candidates)    │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 3. FEEDBACK        │  (crítica ou contexto)       │
│    │    feedback =      │                              │
│    │    critic(best)    │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 4. REFINE          │  (incorporar feedback)       │
│    │    prompt +=       │                              │
│    │    feedback        │                              │
│    │    state.update()  │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 5. STORE           │  (guardar iteração)          │
│    │    iterations.     │                              │
│    │    append(...)     │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│    ┌──────▼──────────────┐                             │
│    │ 6. CHECK           │  (parar ou continuar?)       │
│    │    TERMINATION     │                              │
│    │    if should_stop()│                              │
│    │      break         │                              │
│    └──────┬──────────────┘                             │
│           │                                             │
│           └────┐ (próxima iteração)                    │
│                ▼                                        │
│           [volta ao topo]                              │
│                                                          │
│  OUTPUT (result, iterations, metadata)                 │
│           ▲                                             │
│           │                                             │
│  ┌────────┴─────────────┐                              │
│  │ AGGREGATE RESULT    │  (sintetizar iterações)      │
│  │ (best, insights)    │                              │
│  └─────────────────────┘                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Componentes Principais

### **1. Estado Recursivo (RecursionState)**

```python
class RecursionState:
    """Encapsula o estado completo de uma execução recursiva"""
    
    # Identificação
    execution_id: str                    # UUID único por execução
    technique: str                       # "tot", "self_refine", etc
    
    # Progresso
    iteration: int                       # Contador de iteração (0, 1, 2, ...)
    max_iterations: int                  # Limite configurável
    
    # Conteúdo
    original_prompt: str                 # Prompt inicial (imutável)
    current_prompt: str                  # Prompt após refinamentos
    
    # Histórico
    all_iterations: List[IterationRecord]  # Todos os passos
    best_solution: Optional[Solution]      # Melhor solução encontrada
    
    # Memória
    memory_pool: Dict[str, any]          # Cache/episódios para reflexion
    metrics: MetricsCollector            # Coleta de KPIs
    
    # Recursos
    tokens_used: int                     # Tokens consumidos até agora
    compute_time: float                  # Tempo decorrido
    
    # Configuração
    config: RecursionConfig              # Parâmetros específicos da técnica
```

### **2. Iteração (IterationRecord)**

```python
class IterationRecord:
    """Um passo completo do loop recursivo"""
    
    iteration_number: int                 # 0, 1, 2, ...
    timestamp: datetime                   # Quando ocorreu
    
    # Saídas do passo
    generated_candidates: List[str]       # N variações geradas
    evaluation_scores: List[float]        # Pontuação de cada uma
    selected_best: str                    # Melhor selecionado
    
    # Feedback e refinamento
    feedback_from_critic: str             # Crítica estruturada (se houver)
    refined_prompt: str                   # Prompt após incorporar feedback
    
    # Metadados
    tokens_this_iteration: int            # Tokens gastos neste passo
    duration_ms: float                    # Tempo em ms
    
    # Técnica específica
    extra_data: Dict[str, any]            # Dados adicionais por técnica
                                          # (ex: tree branches em ToT)
```

### **3. Critério de Terminação**

```python
class TerminationCondition:
    """Define quando parar o loop recursivo"""
    
    # Condições básicas
    max_iterations: int = 3               # Parar após N iterações
    max_tokens: int = 10000               # Parar após N tokens
    max_time_ms: int = 60000              # Parar após N ms
    
    # Convergência
    min_improvement_threshold: float = 0.01  # Se melhora < X%, parar
    iterations_without_improvement: int = 2  # Parar após X iterações sem melhora
    
    # Qualidade
    target_quality_score: float = 0.95    # Se atingir qualidade X, parar
    consistency_threshold: float = 0.98   # Se últimas N respostas são >=X% iguais
    
    def should_terminate(self, state: RecursionState) -> bool:
        """Verificar se deve parar"""
        
        # 1. Limites duros
        if state.iteration >= self.max_iterations:
            return True
        if state.tokens_used >= self.max_tokens:
            return True
        if state.compute_time >= self.max_time_ms:
            return True
        
        # 2. Convergência
        if len(state.all_iterations) > 1:
            recent_scores = [it.evaluation_scores[0] 
                           for it in state.all_iterations[-3:]]
            improvement = (recent_scores[-1] - recent_scores[-2]) / recent_scores[-2]
            
            if improvement < self.min_improvement_threshold:
                state.iterations_no_improvement += 1
                if state.iterations_no_improvement >= self.iterations_without_improvement:
                    return True
        
        # 3. Qualidade
        if state.best_solution.quality_score >= self.target_quality_score:
            return True
        
        return False
```

---

## 🧠 Funções Abstratas Principais

### **A. Generate (Geração de Candidatos)**

```python
def generate_candidates(
    state: RecursionState,
    config: RecursionConfig,
    num_branches: int = 3
) -> List[str]:
    """
    Gera N variações de um prompt/solução
    
    Mecanismo:
    - Cada técnica define como explorar o espaço de variações
    - ToT: diferentes caminhos de raciocínio
    - Self-Refine: mesma linha base com contexto de crítica anterior
    - Reflexion: usando memória episódica
    
    Args:
        state: estado recursivo atual
        config: parâmetros (temperature, top_k, etc)
        num_branches: quantas variações gerar
    
    Returns:
        Lista de str com candidatos
    """
    
    candidates = []
    
    for i in range(num_branches):
        # Construir prompt para modelo
        system_prompt = build_system_prompt(state, i)
        user_prompt = state.current_prompt
        
        # Chamar modelo (via providers.py)
        response = call_model(
            provider=config.provider,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens_per_iteration
        )
        
        candidates.append(response)
        state.metrics.tokens_used += count_tokens(response)
    
    return candidates
```

### **B. Evaluate (Avaliação)**

```python
def evaluate_candidates(
    candidates: List[str],
    state: RecursionState,
    config: RecursionConfig
) -> List[float]:
    """
    Avalia cada candidato gerando um score [0, 1]
    
    Mecanismo:
    - Pode ser automático (LLM-as-judge) ou simbólico (verificador)
    - Técnicas diferentes usam heurísticas diferentes
    
    Args:
        candidates: variações a avaliar
        state: contexto da execução
        config: parâmetros de avaliação
    
    Returns:
        Lista de scores [0, 1]
    """
    
    scores = []
    
    for candidate in candidates:
        # Avaliar de acordo com técnica
        if config.technique == "tot":
            # Heurística de "promessa" para ToT
            score = evaluate_thought_promise(candidate, state)
        
        elif config.technique == "self_refine":
            # Uso de modelo de crítica
            score = evaluate_with_critic_model(candidate, state, config)
        
        elif config.technique == "alignment":
            # Verificação formal
            score = evaluate_formal_validity(candidate, state, config)
        
        else:
            # Padrão: LLM-as-judge
            score = evaluate_with_llm_judge(candidate, state, config)
        
        scores.append(score)
    
    return scores
```

### **C. Feedback (Crítica Estruturada)**

```python
def get_feedback(
    best_candidate: str,
    state: RecursionState,
    config: RecursionConfig
) -> str:
    """
    Gera feedback estruturado para refinar próxima iteração
    
    Mecanismo:
    - Crítica automática que identifica falhas ou melhorias
    - Pode vir de outro modelo (crítico) ou regras simbólicas
    
    Args:
        best_candidate: melhor variação da iteração
        state: contexto
        config: parâmetros
    
    Returns:
        Feedback estruturado (texto)
    """
    
    if config.feedback_type == "llm_critique":
        # Usar modelo crítico
        feedback = call_model(
            provider=config.critique_provider,
            system_prompt=CRITIQUE_SYSTEM_PROMPT,
            user_prompt=f"""
Analise esta resposta e identifique:
1. Pontos fortes
2. Áreas de melhora
3. Sugestões específicas

Resposta:
{best_candidate}

Prompt original:
{state.original_prompt}
            """,
            temperature=0.7,
            max_tokens=500
        )
        return feedback
    
    elif config.feedback_type == "rule_based":
        # Feedback com base em regras
        feedback_items = []
        
        # Verificar comprimento
        if len(best_candidate.split()) < 50:
            feedback_items.append("Expansão: adicione mais detalhes")
        
        # Verificar estrutura
        if not has_clear_structure(best_candidate):
            feedback_items.append("Estrutura: organize em seções claras")
        
        # Verificar logicidade
        if not is_logically_consistent(best_candidate):
            feedback_items.append("Lógica: corrija inconsistências")
        
        return "\n".join(feedback_items)
    
    else:
        return ""  # Sem feedback
```

### **D. Refine (Incorporar Feedback)**

```python
def refine_prompt(
    current_prompt: str,
    feedback: str,
    state: RecursionState
) -> str:
    """
    Incorpora feedback no prompt para próxima iteração
    
    Mecanismo:
    - Atualiza prompt com crítica, mantendo intenção original
    - Ou constrói novo prompt baseado em feedback
    
    Args:
        current_prompt: prompt atual
        feedback: feedback da iteração
        state: contexto
    
    Returns:
        Novo prompt refinado
    """
    
    if not feedback:
        return current_prompt
    
    # Construir refinado com feedback
    refined = f"""
{current_prompt}

---
FEEDBACK DA ITERAÇÃO ANTERIOR:
{feedback}

---
APLICAR MELHORIAS ACIMA NA PRÓXIMA VERSÃO.
    """
    
    return refined
```

### **E. Aggregation (Síntese Final)**

```python
def aggregate_result(
    state: RecursionState,
    config: RecursionConfig
) -> RecursionResult:
    """
    Sintetiza todas as iterações em resultado final
    
    Args:
        state: estado final
        config: configuração usada
    
    Returns:
        Resultado estruturado com insights
    """
    
    # Encontrar melhor solução geral
    best_solution = max(
        state.all_iterations,
        key=lambda it: max(it.evaluation_scores)
    )
    
    # Calcular estatísticas
    improvement = (
        state.all_iterations[-1].evaluation_scores[0] -
        state.all_iterations[0].evaluation_scores[0]
    ) / state.all_iterations[0].evaluation_scores[0] * 100
    
    return RecursionResult(
        final_answer=best_solution.selected_best,
        iterations_count=state.iteration,
        improvement_percent=improvement,
        tokens_total=state.tokens_used,
        time_total_ms=state.compute_time,
        all_iterations=state.all_iterations,
        metadata={
            "technique": config.technique,
            "provider": config.provider,
            "quality_score": state.best_solution.quality_score,
        }
    )
```

---

## 🎯 Padrões Diferenciais por Técnica

| Técnica | Generate | Evaluate | Feedback | Refine | Termination |
|---------|----------|----------|----------|--------|-------------|
| **ToT** | N ramos diferentes | Heurística + score | Foco em branches bons | Poda | Depth + convergência |
| **Self-Refine** | Mesmo contexto + crítica | Crítico dedicado | Crítica estruturada | Incorpora crítica | Melhora plateauing |
| **Reflexion** | Com episódios da memória | Histórico | Lições aprendidas | Com contexto passado | Convergência + recall |
| **Alignment** | Normal | Verificador simbólico | Contraexemplos formais | Prova de correção | Validade formal |
| **LLM-MCTS** | Função de valor | UCB1 score | Reward | MCTS update | Ganho marginal |
| **Debate** | Cada agente gera | Votação/convergência | Argumentos adversários | Síntese | Consenso atingido |
| **Autoformal** | NL gerado | Lean4/Isabelle | Erro de prova | Código formal | Prova válida |

---

## 📊 Estruturas de Dados Essenciais

```python
# Enums para técnicas
class RecursionTechnique(Enum):
    NONE = "none"
    TOT = "tot"
    GOT = "got"
    SELF_REFINE = "self_refine"
    REFLEXION = "reflexion"
    ALIGNMENT = "alignment"
    MCTS = "mcts"
    DEBATE = "debate"
    AUTOFORMAL = "autoformal"

# Configuração genérica
class RecursionConfig(BaseModel):
    technique: RecursionTechnique
    provider: str  # "openai", "gemini", etc
    model: str     # "gpt-4o", "gemini-2.0", etc
    
    # Geração
    temperature: float = 0.7
    top_k: int = 50
    max_tokens_per_iteration: int = 1000
    num_branches: int = 3
    
    # Terminação
    max_iterations: int = 5
    max_tokens_total: int = 10000
    max_time_ms: int = 120000
    min_improvement_threshold: float = 0.01
    
    # Técnica específica
    extra_params: Dict[str, any] = {}

# Resultado final
class RecursionResult(BaseModel):
    final_answer: str
    iterations_count: int
    improvement_percent: float
    tokens_total: int
    time_total_ms: float
    all_iterations: List[IterationRecord]
    metadata: Dict[str, any]
    
    # Qualidade
    quality_score: float         # [0, 1]
    confidence: float            # [0, 1]
    explanation: str             # Por que é bom
```

---

## 🔐 Princípios de Design

### **1. Separação de Responsabilidades**
- Cada função tem uma responsabilidade clara
- Técnicas herdam do padrão base mas override métodos específicos

### **2. State Management Explícito**
- Estado completo em `RecursionState`
- Cada iteração é rastreável e auditável

### **3. Configurabilidade**
- Todos os parâmetros em `RecursionConfig`
- Permite experimentação e tuning

### **4. Eficiência de Token**
- Token counting em cada chamada
- Early stopping se limite atingido

### **5. Extensibilidade**
- Novas técnicas implementam o padrão base
- Novos avaliadores podem ser plugados

---

## 📈 Fluxo Típico de Uma Sessão

```
1. Usuário entra (Frontend)
   └─ Seleciona técnica + configurações

2. POST /api/improve-prompt-recursive
   ├─ Payload: {prompt, technique, config}
   └─ Backend criando RecursionState

3. RecursionRouter dispatcher
   ├─ Identifica técnica
   ├─ Instancia engine específica
   └─ Inicia WebSocket para streaming

4. Engine inicia loop
   ├─ Iteração 1:
   │  ├─ Generate (3 candidatos)
   │  ├─ Evaluate (scores: 0.72, 0.85, 0.78)
   │  ├─ Feedback (crítica)
   │  ├─ Refine (prompt atualizado)
   │  ├─ Stream para frontend
   │  └─ Salvar IterationRecord no DB
   │
   ├─ Iteração 2:
   │  ├─ (idem)
   │  └─ Verificar terminação
   │
   └─ Iteração 3:
      ├─ (idem)
      └─ should_terminate() = True → break

5. Aggregation
   ├─ Sintetizar resultado
   ├─ Calcular estatísticas
   └─ Stream final response

6. Frontend recebe
   ├─ Exibe resultado final
   ├─ Mostra todas iterações
   ├─ Permite inspect cada passo
   └─ Opção de refinar mais ou copiar
```

---

## 🚀 Próximos Passos

Agora que você entende a **arquitetura genérica**, passe para:

1. **Doc 02**: Comparação de técnicas para decidir qual estudar
2. **Doc 03**: Tree of Thoughts (recomendado como próximo passo)
3. **Doc 04**: Self-Refine (recomendado se quer começar simples)

---

## 📚 Referências & Citações

- Yao et al., "Tree of Thoughts: Deliberate Problem Solving with LLMs" (2023)
- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" (2023)
- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023)
- Brown et al., "Recursive Reasoning with Formal Verification" (2025)
- Combinatorial search + LLMs (MCTS pattern) - Emergent research

**Próximo doc**: [02-COMPARACAO-TECNICAS.md](./02-COMPARACAO-TECNICAS.md)
