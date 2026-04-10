# 11 - Casos de Uso & Exemplos Práticos

## 🎯 Visão Geral

Este documento fornece **exemplos reais e tutoriais** de como usar cada técnica no Prompt-Boost para resolver problemas específicos.

---

## 📚 Exemplo 1: Melhorar Prompt de Programação (Self-Refine)

### Problema
> Usuário tem um prompt ruim para gerar código e quer melhorá-lo iterativamente

### Entrada

```json
{
    "prompt": "Escreva um código que faz um parser",
    "technique": "self_refine",
    "config": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_iterations": 3,
        "critique_provider": "openai",
        "critique_model": "gpt-4o-mini"
    }
}
```

### Processo

```
Iteração 1:
├─ Gerado: "Um parser é um programa que..."
├─ Crítica: "Vago. Qual tipo de parser? Qual linguagem?"
└─ Refinado: "Escreva em Python um parser JSON otimizado..."

Iteração 2:
├─ Gerado: "Escrever parser JSON em Python..."
├─ Crítica: "Melhor, mas falta exemplos de entrada/saída"
└─ Refinado: "Escreva em Python um parser JSON otimizado...
             Entrada: {\"name\": \"John\"}
             Saída: {'name': 'John'}"

Iteração 3:
├─ Gerado: "Parser JSON completo com validação..."
├─ Crítica: "Excelente! Adicione handling de erro"
└─ Refinado: "Parser JSON em Python com validação e tratamento de erro..."

Final: Prompt altamente específico pronto para uso
```

### Código no Prompt-Boost

```bash
curl -X POST http://localhost:8000/api/improve-prompt-recursive \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Escreva um código que faz um parser",
    "technique": "self_refine",
    "config": {
      "provider": "openai",
      "model": "gpt-4o",
      "max_iterations": 3,
      "temperature": 0.7
    }
  }'
```

### Resultado Esperado

```json
{
    "final_answer": "Escreva em Python um parser JSON otimizado que valida entrada e trata erros corretamente. Input: {...}, Output: {...}",
    "iterations_count": 3,
    "tokens_total": 4200,
    "improvement_percent": 45,
    "metadata": {
        "quality_score": 0.92
    }
}
```

---

## 🧠 Exemplo 2: Raciocínio Matemático (Tree of Thoughts)

### Problema
> Resolver problema matemático complexo explorando múltiplos caminhos

### Entrada

```json
{
    "prompt": "Prove que a soma de três números consecutivos é sempre divisível por 3",
    "technique": "tot",
    "config": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_iterations": 5,
        "extra_params": {
            "k_candidates": 3,
            "beam_width": 2,
            "prune_strategy": "top_k",
            "original_problem": "Prove que a soma de três números consecutivos é sempre divisível por 3"
        }
    }
}
```

### Processo (Árvore)

```
                    RAIZ: Problema
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    BRANCH 1          BRANCH 2          BRANCH 3
    Abordagem         Abordagem         Abordagem
    Algébrica         Modular           Indução
        │                │                │
        ├─ Seja n,n+1,  ├─ Usar mod 3   ├─ Base: 1,2,3
        │  n+2          │  propriedades  │
        │               │                │
        ├─ Soma =       ├─ Qualquer int ├─ Passo: assume
        │  3n+3         │  é ≡ 0,1,2    │  k,k+1,k+2 soma
        │               │  (mod 3)       │  é ÷3
        │               │                │
        ├─ = 3(n+1)     ├─ Prova: teste ├─ Prove k+1, k+2, k+3
        │               │  todos casos  │  soma = anterior + 3
        ├─ ✓ Divisível  │                │
        │                ├─ ✓ Divisível  ├─ ✓ Divisível
        │                │                │
        └─ SCORE: 0.95   └─ SCORE: 0.88   └─ SCORE: 0.92

Seleção: Branch 1 (maior score)
Refinamento: Expandir Branch 1
Final: Prova algébrica formal
```

### Código no Prompt-Boost

```bash
curl -X POST http://localhost:8000/api/improve-prompt-recursive \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Prove que a soma de três números consecutivos é sempre divisível por 3",
    "technique": "tot",
    "config": {
      "provider": "openai",
      "model": "gpt-4o",
      "max_iterations": 5,
      "extra_params": {
        "k_candidates": 3,
        "beam_width": 2
      }
    }
  }'
```

### Resultado

```json
{
    "final_answer": "Seja n, n+1, n+2 três consecutivos. Soma = 3n + 3 = 3(n+1), sempre ÷3",
    "iterations_count": 5,
    "tree_depth": 4,
    "nodes_generated": 15,
    "metadata": {
        "best_path": ["Algébrica", "Formalizar", "Simplificar", "QED"]
    }
}
```

---

## 🗳️ Exemplo 3: Análise Equilibrada (Multi-Agent Debate)

### Problema
> Analisar um tópico polêmico com múltiplas perspectivas para reduzir viés

### Entrada

```json
{
    "prompt": "A Inteligência Artificial vai substituir programadores em 2030?",
    "technique": "multi_agent_debate",
    "config": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_iterations": 3,
        "extra_params": {
            "num_agents": 3,
            "max_debate_rounds": 3,
            "convergence_threshold": 0.85
        }
    }
}
```

### Processo

```
ROUND 1: ARGUMENTOS INICIAIS

Agent Proponent (Favorável):
"Sim, IA vai substituir. Razões:
 - Modelos de código (Copilot, ChatGPT) já fazem 80% das tarefas simples
 - Automação é tendência histórica
 - 20 anos: IA fará debug, refatoração, otimização"

Agent Opponent (Contrário):
"Não vai substituir. Razões:
 - Criatividade e design ainda é humano
 - IA precisa de humanos para feedback/direção
 - Histórico: cada automação criou novas profissões"

Agent Neutral (Mediador):
"Ambos têm pontos. Questão verdadeira é: qual o timeline e escopo?"

┌──────────────┬──────────────┬──────────────┐
│  Proponent   │    Neutral   │   Opponent   │
│   Score: 0.7 │   Score: 0.6 │   Score: 0.65│
└──────────────┴──────────────┴──────────────┘
Convergência: 0.33 (baixa → continuar)

---

ROUND 2: REBUTTALS

Agent Proponent:
"Concordo que humanos ainda dirigem, mas:
 - IA já faz 80% das tarefas operacionais
 - Em 10 anos será 90%+
 - Programadores evoluem para 'Prompt Engineers'"

Agent Opponent:
"Ponto aceito, mas discordo timeline:
 - Ainda há 10+ anos até IA fazer design complexo
 - Prompt Engineering é ainda programação"

Agent Neutral:
"Consenso emergindo: mudança SERÁ, mas qual escopo?"

┌──────────────┬──────────────┬──────────────┐
│  Proponent   │    Neutral   │   Opponent   │
│   Score: 0.7 │   Score: 0.72│   Score: 0.68│
└──────────────┴──────────────┴──────────────┘
Convergência: 0.70 (média → próximo round)

---

ROUND 3: SÍNTESE

Juiz (Judge Agent):
"Análise equilibrada:

PONTOS DE CONSENSO:
✓ IA SERÁ disruptiva na programação
✓ Mudança ocorrerá em próxima década
✓ Humanos redirecionar para design/arquitetura

DISCORDÂNCIAS REMANESCENTES:
✗ Timeline exata: 10-20 anos?
✗ Escopo: 80% ou 95% dos jobs?

RECOMENDAÇÃO:
Verdade provavelmente: IA substituirá 80-90% de tarefas
ROTINEIRAS, mas humanos permanecerão para:
- Arquitetura de sistemas
- Decisões de design
- Liderança técnica
"

┌──────────────┬──────────────┬──────────────┐
│  Proponent   │    Neutral   │   Opponent   │
│   Score: 0.72│   Score: 0.75│   Score: 0.71│
└──────────────┴──────────────┴──────────────┘
Convergência: 0.73 ✓ Próximo ao threshold (0.85)
```

### Resultado

```json
{
    "final_answer": "IA substituirá 80-90% de tarefas ROTINEIRAS em 10 anos, não a profissão inteira. Programadores evoluem para arquitetura/design.",
    "iterations_count": 3,
    "convergence_score": 0.73,
    "debate_perspectives": [
        {
            "agent": "Proponent",
            "position": "IA substituirá principalmente",
            "final_score": 0.72
        },
        {
            "agent": "Opponent",
            "position": "Humanos permanecem essenciais",
            "final_score": 0.71
        },
        {
            "agent": "Neutral",
            "position": "Mudança disruptiva mas não extinção",
            "final_score": 0.75
        }
    ]
}
```

---

## 🧪 Exemplo 4: Aprendizado Contínuo (Reflexion)

### Problema
> Chatbot que melhora ao longo do tempo aprendendo de tentativas anteriores

### Primeira Sessão

```
Task: "Escreva um resumo de 3 linhas sobre IA"

Generation 1:
"IA é tecnologia que simula inteligência. É usada em muitos lugares. É importante para o futuro."
(Qualidade: 0.45 - Vago e genérico)

Crítica:
"Muito vago. Adicione exemplos específicos. Use linguagem técnica."

Lesson Extraída:
"Ao summarizar IA: ser específico (ex: ML, NLP), mencionar aplicações concretas (visão, voz), use termos técnicos"

Salvar na Memória:
```json
{
    "task": "Resumo de IA",
    "lesson": "Ser específico, exemplos, jargão técnico",
    "quality_achieved": 0.72,
    "timestamp": "2026-04-10T10:00:00Z"
}
```

### Segunda Sessão (Próximo Dia)

```
Task: "Escreva um resumo de 3 linhas sobre Machine Learning"

Recuperar Memória:
"Lesson da última vez: Ser específico, exemplos, termos técnicos"

Generation 1 (com contexto):
"Machine Learning é subconjunto de IA que permite sistemas aprender de dados (ex: classificação de imagens, recomendação). Treina modelos via algoritmos estatísticos."
(Qualidade: 0.88 - MUITO MELHOR!)

✓ Convergiu em 1 iteração (vs 3 antes)
```

### Código

```bash
# Criar session com memória persistente
curl -X POST http://localhost:8000/api/improve-prompt-recursive \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Escreva resumo de ML",
    "technique": "reflexion",
    "config": {
      "provider": "openai",
      "model": "gpt-4o",
      "memory_storage_path": "./memories/my_agent.json",
      "memory_top_k": 3
    }
  }'
```

---

## 🔐 Exemplo 5: Garantia Formal (Autoformalização)

### Problema
> Converter prova matemática para Lean4 e validar formalmente

### Entrada

```json
{
    "prompt": "Prove que a raiz quadrada de 2 é irracional",
    "technique": "autoformal",
    "config": {
        "provider": "openai",
        "model": "gpt-4o",
        "target_language": "lean4",
        "max_iterations": 10,
        "lake_path": "/usr/bin/lake"
    }
}
```

### Processo

```
Iteração 1:
└─ LLM gera Lean4:
   theorem sqrt2_irrational : irrational (Real.sqrt 2) := by
     sorry
   
   Lean4 retorna: ✗ Error: "irrational" not defined
                  sugestão: import Data.Real.Irrational

Iteração 2:
└─ LLM gera (com erro):
   import Data.Real.Irrational
   theorem sqrt2_irrational : irrational (Real.sqrt 2) := by
     exact irrational_sqrt_two
   
   Lean4 retorna: ✓ Valid! Prova encontrada!
                  (simplificar?)

Iteração 3: (Simplificar)
└─ LLM tenta forma mais elegante:
   import Data.Real.Irrational
   theorem sqrt2_irrational : ¬ (∃ p q : ℚ, p ^ 2 = 2 * q ^ 2) := by
     intro ⟨p, q, hpq⟩
     ...
   
   Lean4 retorna: ✓ Valid! Forma mais elegante!

Final: Prova formalmente verificada
```

### Resultado

```json
{
    "final_answer": "theorem sqrt2_irrational : irrational (Real.sqrt 2) := exact irrational_sqrt_two",
    "iterations_count": 2,
    "is_formally_valid": true,
    "target_language": "lean4",
    "verification_time_ms": 1250
}
```

---

## 📊 Exemplo 6: Planejamento Robótico (LLM-MCTS)

### Problema
> Planejar sequência de ações para robô fazer tarefa

### Entrada

```json
{
    "prompt": "Planejar sequência de ações para robô pegar xícara da mesa e levar até cozinha",
    "technique": "mcts",
    "config": {
        "provider": "openai",
        "model": "gpt-4o",
        "extra_params": {
            "num_simulations": 50,
            "objective": "Xícara na cozinha"
        }
    }
}
```

### Processo (Simulações MCTS)

```
Simulação 1-10: Exploração aleatória
├─ Caminho 1: Aproximar → Agarrar → Ir cozinha → Soltar ✓ (Success: 1.0)
├─ Caminho 2: Aproximar → Cair → Restart ✗ (Success: 0.0)
├─ Caminho 3: Ver obstáculo → Contornar → Agarrar → Cozinha ✓ (Success: 1.0)
└─ Melhor score: Abordagem com contorno

Simulação 11-30: Foco em variações com contorno
├─ Caminho A: Contorno rápido (5 passos) ✓ (Success: 0.95)
├─ Caminho B: Contorno lento mas seguro (8 passos) ✓ (Success: 1.0)
└─ Melhor score: Contorno lento (mais robusto)

Simulação 31-50: Refinamento
├─ Testar: Contorno lento + diferentes velocidades
├─ Validar: Margem de erro com perturbações
└─ Plano final: [Scan, Contour, Approach, Grasp, Lift, MoveToCook, Release]

┌─────────┬─────────┬──────────┐
│ Caminho │ Success │  Reward  │
├─────────┼─────────┼──────────┤
│ Simples │  0.70   │  -0.30   │
│ Contour │  0.95   │  +0.45   │
│ Robusto │  1.00   │  +0.50   │
└─────────┴─────────┴──────────┘

Seleção: Caminho Robusto (melhor valor)
```

### Resultado

```json
{
    "final_answer": "[Scan environment, Contour obstacles, Approach table, Grasp cup carefully, Lift slowly, Move to kitchen, Release gently]",
    "iterations_count": 50,
    "tree_depth": 7,
    "best_path_success_rate": 1.0
}
```

---

## 🎓 Referências Rápidas

| Caso | Técnica | Razão |
|------|---------|-------|
| Melhorar texto/código | Self-Refine | Rápido, iterativo |
| Resolver problema lógico | ToT | Explora múltiplos caminhos |
| Análise imparcial | Multi-Agent | Múltiplas perspectivas |
| Aprendizado contínuo | Reflexion | Memória episódica |
| Garantia matemática | Autoformal | Prova formal |
| Planejamento | LLM-MCTS | Busca estruturada |

---

## 🚀 Como Começar

1. **Escolha técnica** adequada para seu caso
2. **Use exemplos acima** como template
3. **Ajuste parâmetros** (max_iterations, temperature, etc)
4. **Compare com baseline** (sem recursão)
5. **Measure RER** para validar ROI

---

**Fim da Documentação de Raciocínio Recursivo v1.0**

Próximos passos:
- Implementar engines conforme Passo 1-5 do [09-IMPLEMENTACAO-PRATICA.md](./09-IMPLEMENTACAO-PRATICA.md)
- Testar contra benchmarks em [10-METRICAS-E-BENCHMARKS.md](./10-METRICAS-E-BENCHMARKS.md)
- Deploy em produção após validação
