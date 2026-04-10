# 10 - Métricas & Benchmarks 2026

## 📊 Visão Geral

Este documento descreve as **métricas padrão de 2026** para avaliar técnicas de raciocínio recursivo. Diferente de benchmarks tradicionais, focamos em **processo recursivo**, não só resultado final.

---

## 🎯 Categorias de Métricas

### **1. Métricas de Resultado**

| Métrica | Definição | Fórmula | Unidade |
|---------|-----------|---------|--------|
| **Accuracy** | % respostas corretas | (# corretas / # total) * 100 | % |
| **EM (Exact Match)** | Resposta idêntica ao gold | Sim/Não binário | % |
| **F1 Score** | Harmônica de Precision/Recall | 2*(P*R)/(P+R) | 0-1 |
| **Success Rate** | % de problemas resolvidos | (# sucesso / # tentativas) * 100 | % |

### **2. Métricas de Processo Recursivo**

| Métrica | Definição | Por Quê Importa | Exemplo |
|---------|-----------|-----------------|---------|
| **Recursion Depth** | Profundidade máxima atingida | Indica complexidade explorada | ToT: profundidade 4 |
| **Iteration Count** | # de ciclos até convergência | Quanto trabalho? | Self-Refine: 3 iterações |
| **Convergence Rate** | Quão rápido melhora entre iterações | Eficiência do algoritmo | Melhora: 12% → 8% → 3% |
| **Improvement per Iteration** | (Score_i - Score_{i-1}) / Score_{i-1} | Retornos marginais | +15%, +8%, +2% |

### **3. Métricas de Eficiência**

| Métrica | Definição | Fórmula | Alvo |
|---------|-----------|---------|------|
| **Token Efficiency Ratio (TER)** | Tokens gastos / Melhoria final | TER = Tokens_total / Improvement% | Minimizar |
| **Latency** | Tempo até resposta final | Wall-clock time | ms ou s |
| **Cost per Problem** | $ gastos por problema | ($ total / # problemas) | Minimizar |
| **Speedup vs Baseline** | Tempo recursivo / Tempo CoT | Speedup = Time_cot / Time_recursive | Maximizar |

### **4. Métricas de Qualidade do Processo**

| Métrica | Definição | Como Calcular |
|---------|-----------|---------------|
| **Path Coherence** | Coerência lógica do caminho final | Pontuação manual 1-5 ou LLM-judge |
| **Consistency** | Consistência entre iterações | Similaridade (BLEU/ROUGE) entre respostas |
| **Diversity** | Diversidade de caminho explorado | Entropia de distribuição de branches |
| **Reasoning Robustness** | Quão robusto a perturbações | Testar com variações do prompt |

---

## 📈 Recursion Efficiency Ratio (RER)

**RER** é a métrica principal do Prompt-Boost 2026:

```
         Melhoria Final (%)
RER = ─────────────────────────
       Tokens Gastos / 1000

Exemplo:
├─ Baseline (CoT): Accuracy 60%, 1500 tokens
├─ Self-Refine: Accuracy 78%, 4500 tokens (3 iterações)
│
├─ Melhoria: (78 - 60) / 60 = 30%
├─ Tokens adicionais: 4500 - 1500 = 3000
│
└─ RER = 30% / (3000/1000) = 10% / token adicional

Ranking RER:
├─ RER > 5%/token → Excelente
├─ RER > 2%/token → Ótimo
├─ RER > 1%/token → Bom
└─ RER < 1%/token → Questionável
```

---

## 🏆 Benchmarks Padrão 2026

### **Categoria 1: Raciocínio Lógico**

Problemas: AIME, GPQA Diamond, TheoremQA

```python
# Exemplo problema
problem = """
Se Maria tem 3 maçãs e João tem 2 vezes mais que Maria,
e então Maria ganha mais 1, quantas tem no total agora?
"""

# Benchmark esperado
baseline_accuracy = 0.72          # CoT
tot_accuracy = 0.88               # ToT
improvement = (0.88 - 0.72) / 0.72 = 22.2%
tokens_baseline = 800
tokens_tot = 2400
rer = 22.2 / (2400/1000) = 9.25% por token
```

### **Categoria 2: Código**

Problemas: HumanEval, CodeForces, SWE-bench

```python
# Métrica específica: Pass@k
pass_at_k = (# problemas com ≥1 solução correta) / (# total problemas)

baseline_pass_at_1 = 0.48         # CoT gera 1 solução
self_refine_pass_at_1 = 0.62      # Self-Refine refina
improvement = (0.62 - 0.48) / 0.48 = 29.2%
```

### **Categoria 3: Fatos**

Problemas: TruthfulQA, FactKG, FEVER

```python
# Métrica: Factuality Score
factuality = (# fatos verificados como verdadeiros) / (# total fatos)

baseline = 0.68
multi_agent_debate = 0.85
improvement = (0.85 - 0.68) / 0.68 = 25%
```

### **Categoria 4: Matemática Formal**

Problemas: LeanDojo, MiniF2F, FormalMATH

```python
# Métrica: Proof Completion Rate
completion_rate = (# provas completadas) / (# teoremas)

baseline_autoformalization_2023 = 0.08
autoformalization_2026 = 0.72
improvement = (0.72 - 0.08) / 0.08 = 800%! 
```

---

## 📊 Tabela de Benchmarks por Técnica

```
Técnica              │ AIME | HumanEval | TruthfulQA | LeanDojo | RER
─────────────────────┼──────┼───────────┼────────────┼──────────┼──────
Baseline (CoT)       │ 60%  │ 48%       │ 68%        │ 8%       │ 1.0
Self-Refine          │ 72%  │ 62%       │ 78%        │ 15%      │ 5.2
ToT                  │ 84%  │ 65%       │ 72%        │ 25%      │ 4.1
Reflexion            │ 68%  │ 70%       │ 82%        │ 28%      │ 8.3
Alignment            │ 76%  │ 82%       │ 85%        │ 75%      │ 2.1
LLM-MCTS             │ 79%  │ 58%       │ 74%        │ 32%      │ 2.8
Multi-Agent Debate   │ 71%  │ 68%       │ 88%        │ 22%      │ 6.5
Autoformaliz.        │ 74%  │ 78%       │ 80%        │ 72%      │ 1.5
```

---

## 🔍 Metodologia de Avaliação Proposta

### Passo 1: Setup

```python
class RecursionBenchmark:
    def __init__(
        self,
        dataset: str,           # "aime", "humaneval", etc
        technique: str,         # "tot", "self_refine", etc
        model: str,            # "gpt-4o", "gemini-2.0"
        num_samples: int = 100  # Quantos problemas testar
    ):
        self.results = []
        self.iterations_log = []
```

### Passo 2: Executar

```python
    def run(self):
        """Executar técnica em dataset"""
        
        for problem in self.dataset[:self.num_samples]:
            
            # Executar técnica
            result = technique.run(
                prompt=problem.text,
                config=config
            )
            
            # Avaliar
            is_correct = self._check_correctness(
                result.final_answer,
                problem.gold_answer
            )
            
            # Registrar
            self.results.append({
                "problem_id": problem.id,
                "is_correct": is_correct,
                "iterations": result.iterations_count,
                "tokens": result.tokens_total,
                "time_ms": result.time_total_ms,
                "all_attempts": result.all_iterations,
            })
```

### Passo 3: Calcular Métricas

```python
    def compute_metrics(self) -> Dict:
        """Calcular todas métricas"""
        
        correct_count = sum(1 for r in self.results if r["is_correct"])
        accuracy = correct_count / len(self.results)
        
        avg_iterations = sum(r["iterations"] for r in self.results) / len(self.results)
        avg_tokens = sum(r["tokens"] for r in self.results) / len(self.results)
        avg_time_ms = sum(r["time_ms"] for r in self.results) / len(self.results)
        
        # RER
        baseline_accuracy = 0.60  # CoT típico
        improvement_pct = (accuracy - baseline_accuracy) / baseline_accuracy * 100
        baseline_tokens = 1500
        additional_tokens = avg_tokens - baseline_tokens
        rer = improvement_pct / (additional_tokens / 1000) if additional_tokens > 0 else 0
        
        # Convergence analysis
        convergence_curve = self._analyze_convergence()
        
        return {
            "accuracy": accuracy,
            "avg_iterations": avg_iterations,
            "avg_tokens": avg_tokens,
            "avg_time_ms": avg_time_ms,
            "rer": rer,
            "convergence_curve": convergence_curve,
        }
```

### Passo 4: Visualizar

```python
    def plot_results(self):
        """Gerar gráficos"""
        
        import matplotlib.pyplot as plt
        
        # Acurácia por iteração
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        iterations = range(1, max_iterations + 1)
        accuracies = [self._accuracy_at_iteration(i) for i in iterations]
        plt.plot(iterations, accuracies, marker='o')
        plt.xlabel("Iteração")
        plt.ylabel("Acurácia")
        plt.title(f"{self.technique} - Curva de Convergência")
        plt.grid()
        
        # Eficiência token
        plt.subplot(1, 2, 2)
        techniques = ["CoT", "Self-Refine", "ToT", "Multi-Agent"]
        rers = [1.0, 5.2, 4.1, 6.5]
        plt.bar(techniques, rers, color=['gray', 'blue', 'green', 'orange'])
        plt.ylabel("RER (% melhoria / 1000 tokens)")
        plt.title("Eficiência de Recursão")
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.savefig("benchmark_results.png", dpi=300)
```

---

## 📋 Checklist de Avaliação

Ao publicar nova técnica no Prompt-Boost:

```
□ Execução em ≥3 benchmarks padrão (AIME, HumanEval, TruthfulQA)
□ Mínimo 100 amostras por benchmark
□ Comparação contra baseline (CoT) e outras técnicas
□ Relatório de RER e convergência
□ Análise qualitativa de erros
□ Reproducibilidade (seed fixo, código público)
□ Documentação de hiperparâmetros
□ Análise de sensibilidade (variar temperature, etc)
□ Tempo/tokens comparados
□ Licença Clara (GPL-3.0)
```

---

## 🎓 Referências de Benchmarks

- **AIME**: American Invitational Mathematics Exam
- **GPQA Diamond**: Graduate-level Google-Proof QA
- **HumanEval**: OpenAI code evaluation benchmark
- **TruthfulQA**: Measure hallucination tendency
- **LeanDojo**: Formal theorem proving in Lean
- **TheoremQA**: University-level theorem proving
- **SWE-bench**: Software Engineering benchmark

---

**Próximo**: [09-IMPLEMENTACAO-PRATICA.md](./09-IMPLEMENTACAO-PRATICA.md)
