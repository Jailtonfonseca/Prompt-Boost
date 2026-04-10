# 05 - Casos de Uso Frontend & Exemplos Práticos

## 🎯 Visão Geral

Este documento fornece exemplos práticos de como usar cada técnica de raciocínio recursivo através da interface do Prompt-Boost v2.0.

---

## 📝 Caso 1: Desenvolvedor Melhorando Prompt de Código

### Cenário
Desenvolvedor precisa gerar código Python otimizado e quer refinar o prompt iterativamente.

### Input
```javascript
originalPrompt: "Escreva um código que parseia JSON"
technique: "self_refine"
config: {
  provider: "openai",
  model: "gpt-4o",
  temperature: 0.5,  // Mais determinístico para código
  max_iterations: 3,
  max_tokens_total: 5000
}
```

### Fluxo Visual (Frontend)

```
┌─ Step 1: Input ───────────────────────────┐
│ "Escreva um código que parseia JSON"      │
└───────────────────────────────────────────┘
        │
        ▼
┌─ Step 2: Selecionar Self-Refine ─────────┐
│ 🔄 Self-Refine [SELECTED]                │
│ Temperature: 0.5 (código) ←───────────── │
│ Max Iterations: 3                        │
└───────────────────────────────────────────┘
        │
        ▼ "🚀 Melhorar Prompt"
┌─ Step 3: Streaming em Tempo Real ────────┐
│ Status: 🧠 Pensando... (Iteração 1/3)    │
│ Tokens: 320/5000                         │
│ Progresso: [████░░░░░░░░░░░░░] 20%      │
│                                          │
│ ┌─ Iteração #1 ─────────────────────┐   │
│ │ Score: 65% (Vago)                 │   │
│ │ Feedback: "Qual tipo de parser?   │   │
│ │  Qual linguagem?"                 │   │
│ └────────────────────────────────────┘   │
└───────────────────────────────────────────┘
        │
        ├─ (Backend processa próxima iteração)
        │
        ▼
┌─ Step 4: Iteração 2 ──────────────────────┐
│ Status: 🧠 Pensando... (Iteração 2/3)     │
│ Tokens: 890/5000                         │
│ Progresso: [████████░░░░░░░░░░░░░░] 50%  │
│                                           │
│ ┌─ Iteração #1 ────────────────────────┐ │
│ │ Score: 65%                           │ │
│ │ ▶ [collapsed]                        │ │
│ └────────────────────────────────────────┘ │
│                                           │
│ ┌─ Iteração #2 ────────────────────────┐ │
│ │ Score: 78% (Melhor!)                 │ │
│ │ ▼ [expanded]                         │ │
│ │                                       │ │
│ │ Gerado:                              │ │
│ │  • "Parser é um programa que..."     │ │
│ │  • "Em Python, parser JSON..."  ← ✓  │ │
│ │  • "Escreva código..."               │ │
│ │                                       │ │
│ │ Feedback: "Melhor! Específico em    │ │
│ │ Python. Mas falta exemplos E/S"     │ │
│ └────────────────────────────────────────┘ │
└────────────────────────────────────────────┘
        │
        ├─ (Backend processa última iteração)
        │
        ▼
┌─ Step 5: Resultado Final ────────────────────┐
│ Status: ✅ Concluído (Iteração 3/3)         │
│ Tokens: 2,340/5000                          │
│ Progresso: [████████████████████████] 100%  │
│                                             │
│ ┌─ Métricas ──────────────────────────────┐ │
│ │ 🔄 Iterações: 3    ⭐ Qualidade: 92%   │ │
│ │ 📊 Tokens: 2,340   📈 RER Score: 1.92  │ │
│ │ ⏱️ Tempo: 18s      🧠 Self-Refine     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─ Prompt Melhorado ──────────────────────┐ │
│ │                                         │ │
│ │ "Escreva em Python um parser JSON      │ │
│ │  otimizado que:                        │ │
│ │  1. Valida entrada corretamente        │ │
│ │  2. Trata erros de sintaxe com msgs    │ │
│ │     amigáveis                          │ │
│ │  3. Inclui exemplos de I/O             │ │
│ │                                        │ │
│ │  Exemplo entrada: {\"name\": \"John\"} │ │
│ │  Exemplo saída: {'name': 'John'}"     │ │
│ │                                         │ │
│ │ [📋 Copiar] [⬇️ Download] [🔄 Refinar] │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Código Frontend Correspondente

```javascript
import { MainPage } from './MainPage';
import { useRecursiveThinking } from '../hooks/useRecursiveThinking';
import { useRecursionStore } from '../store/recursionStore';

export function DeveloperWorkflow() {
  const [originalPrompt, setOriginalPrompt] = useState(
    'Escreva um código que parseia JSON'
  );
  const { improve, status, iterations, result } = useRecursiveThinking();
  const store = useRecursionStore();

  const handleImprove = async () => {
    const config = {
      provider: 'openai',
      model: 'gpt-4o',
      temperature: 0.5,
      max_iterations: 3,
      max_tokens_total: 5000
    };

    try {
      await improve(originalPrompt, 'self_refine', config);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="developer-workflow">
      <textarea
        value={originalPrompt}
        onChange={(e) => setOriginalPrompt(e.target.value)}
        placeholder="Cole seu prompt"
      />

      <RecursiveOptions
        onTechniqueChange={() => {}} // Self-Refine já selecionado
        onConfigChange={() => {}}
        isLoading={status !== 'idle'}
      />

      <button onClick={handleImprove} disabled={status !== 'idle'}>
        🚀 Melhorar Prompt
      </button>

      {status !== 'idle' && (
        <>
          <StreamingOutput status={status} metrics={store.currentExecution.metrics} />
          <IterationVisualizer iterations={iterations} />
        </>
      )}

      {result && (
        <div className="result">
          <h3>Prompt Melhorado</h3>
          <p>{result.final_answer}</p>
          <button onClick={() => navigator.clipboard.writeText(result.final_answer)}>
            📋 Copiar
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 📐 Caso 2: Pesquisador Resolvendo Problema Matemático

### Cenário
Pesquisador quer explorar múltiplos caminhos para resolver problema matemático com verificação formal.

### Input
```javascript
originalPrompt: "Prove que a soma de três números consecutivos é sempre divisível por 3"
technique: "tot"  // Tree of Thoughts
config: {
  provider: "openai",
  model: "gpt-4o",
  temperature: 0.7,
  max_iterations: 5,
  max_tokens_total: 15000,
  extra_params: {
    k_candidates: 3,      // 3 branches por nível
    beam_width: 2,        // Manter os 2 melhores
    prune_strategy: "top_k"
  }
}
```

### Wireframe Visual

```
┌─ Seleção de Técnica ──────────────────────────┐
│ 🔄 Self-Refine                               │
│ 🌳 Tree of Thoughts [SELECTED]                │
│ 🕸️  Graph of Thoughts                         │
│ 🗣️  Debate                                    │
└───────────────────────────────────────────────┘
        │
        ▼ "🚀 Melhorar Prompt"
┌─ Resultado com Árvore ────────────────────────┐
│ Status: ✅ Árvore Explorada (5/5 iterações)  │
│                                              │
│ ┌─ Estrutura da Árvore ──────────────────────┐ │
│ │                                            │ │
│ │           Raiz: Problema                   │ │
│ │               │                            │ │
│ │    ┌──────────┼──────────┐                 │ │
│ │    │          │          │                 │ │
│ │  Abord.1   Abord.2    Abord.3             │ │
│ │ Algébrica  Modular   Indução              │ │
│ │  (95%)      (88%)      (92%)              │ │
│ │                                            │ │
│ │    ┌─ Branch 1 Expandido ──────────────┐ │ │
│ │    │ Seja n, n+1, n+2                  │ │ │
│ │    │ Soma = 3n + 3 = 3(n+1)            │ │ │
│ │    │ ∴ Divisível por 3 ✓               │ │ │
│ │    │                                    │ │ │
│ │    │ Rigor: 95%                        │ │ │
│ │    │ [Ver Detalhes] [Expandir]         │ │ │
│ │    └────────────────────────────────────┘ │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
│                                              │
│ ┌─ Resultado Melhorado ──────────────────────┐ │
│ │                                            │ │
│ │ "Prove algebricamente que a soma de três  │ │
│ │  números consecutivos é sempre divisível │ │
│ │  por 3, usando notação matemática formal. │ │
│ │  Comece definindo os números como n,     │ │
│ │  n+1, n+2 e demonstre cada passo."       │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
│                                              │
│ ┌─ Métricas ────────────────────────────────┐ │
│ │ Iterações: 5 | Branches Exploradas: 15   │ │
│ │ Tokens: 8,450 | Tempo: 32s | Score: 94%  │ │
│ └────────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

---

## 🗣️ Caso 3: Modo Comparação - Múltiplas Técnicas

### Cenário
Usuário quer testar várias técnicas no mesmo prompt para entender trade-offs.

### Input
```javascript
originalPrompt: "Escreva um prompt para gerar código de alta qualidade"
comparisonMode: true
techniques: ["self_refine", "tot", "debate", "alignment"]
config: {
  // Config compartilhada por todas
  provider: "openai",
  model: "gpt-4o",
  temperature: 0.6,
  max_iterations: 3,
  max_tokens_total: 12000
}
```

### Wireframe Visual

```
┌─ Comparação de 4 Técnicas ────────────────────────────┐
│                                                       │
│ [Self-Refine] [ToT] [Debate] [Alignment]            │
│                                                       │
│ ┌─ Self-Refine [Selected] ──────────────────────────┐ │
│ │ Iterações: 3 | Tokens: 3,200 | Tempo: 12s       │ │
│ │ Qualidade: 88% | RER: 2.75                       │ │
│ │                                                   │ │
│ │ "Escreva um prompt detalhado para gerar código  │ │
│ │  Python de alta qualidade que..."               │ │
│ │                                                   │ │
│ │ [Copiar] [Detalhes]                             │ │
│ └───────────────────────────────────────────────────┘ │
│                                                       │
│ ┌─ Tabela Comparativa ──────────────────────────────┐ │
│ │                                                   │ │
│ │ Técnica    │ Qualid. │ Tokens │ Tempo │ RER      │ │
│ │ ───────────┼─────────┼────────┼───────┼────────── │ │
│ │ Self-Refine│ 88%     │ 3,200  │ 12s   │ 2.75    │ │
│ │ ToT        │ 92% ⭐  │ 5,100  │ 18s   │ 1.80    │ │
│ │ Debate     │ 95% ⭐⭐│ 7,200  │ 26s   │ 1.32    │ │
│ │ Alignment  │ 90%     │ 4,100  │ 15s   │ 2.20    │ │
│ │                                                   │ │
│ │ Recomendação: Debate (melhor qualidade)         │ │
│ │              Self-Refine (melhor RER)           │ │
│ │                                                   │ │
│ └───────────────────────────────────────────────────┘ │
│                                                       │
│ ┌─ Comparação de Tempo ────────────────────────────┐ │
│ │ ToT      ███████░░░░ 18s                         │ │
│ │ Debate   ███████████░ 26s                        │ │
│ │ Alignment████░░░░░░░░ 15s                       │ │
│ │ Self-Ref ██████░░░░░░ 12s                       │ │
│ └───────────────────────────────────────────────────┘ │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Código Frontend

```javascript
export function ComparisonMode() {
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const store = useRecursionStore();

  const techniques = ['self_refine', 'tot', 'debate', 'alignment'];

  const runComparison = async () => {
    const config = {
      provider: 'openai',
      model: 'gpt-4o',
      temperature: 0.6,
      max_iterations: 3,
      max_tokens_total: 12000
    };

    const promises = techniques.map(async (technique) => {
      setLoading((prev) => ({ ...prev, [technique]: true }));
      try {
        const result = await improvePromptRecursive(
          originalPrompt,
          technique,
          config
        );
        setResults((prev) => ({ ...prev, [technique]: result }));
      } finally {
        setLoading((prev) => ({ ...prev, [technique]: false }));
      }
    });

    await Promise.all(promises);
  };

  return (
    <div className="comparison-mode">
      <h2>Comparação de Técnicas</h2>

      <textarea
        value={originalPrompt}
        onChange={(e) => setOriginalPrompt(e.target.value)}
        placeholder="Cole seu prompt"
      />

      <button onClick={runComparison} disabled={Object.values(loading).some((x) => x)}>
        🚀 Executar Comparação
      </button>

      {/* Tabs para cada técnica */}
      <div className="tabs">
        {techniques.map((tech) => (
          <button key={tech} className="tab">
            {tech}
            {loading[tech] && ' ⏳'}
            {results[tech] && ' ✓'}
          </button>
        ))}
      </div>

      {/* Tabela Comparativa */}
      <ComparisonTable results={results} />

      {/* Gráficos */}
      <MetricsCharts results={results} />
    </div>
  );
}

function ComparisonTable({ results }) {
  const techniques = Object.keys(results);

  return (
    <table className="comparison-table">
      <thead>
        <tr>
          <th>Técnica</th>
          <th>Qualidade</th>
          <th>Tokens</th>
          <th>Tempo</th>
          <th>RER</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        {techniques.map((tech) => {
          const result = results[tech];
          const rer = calculateRER(result.quality_score, result.tokens_total);
          return (
            <tr key={tech}>
              <td>{tech}</td>
              <td>{(result.quality_score * 100).toFixed(0)}%</td>
              <td>{result.tokens_total}</td>
              <td>{(result.time_total_ms / 1000).toFixed(1)}s</td>
              <td>{rer.toFixed(2)}</td>
              <td>
                <button onClick={() => copyToClipboard(result.final_answer)}>
                  Copiar
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
```

---

## ⚡ Caso 4: Verificação Formal de Prova Matemática

### Cenário
Usuário quer converter prova informal para formato formal (Lean4) com verificação.

### Input
```javascript
originalPrompt: "Prove por indução que 1+2+...+n = n(n+1)/2"
technique: "autoformal"
config: {
  provider: "openai",
  model: "gpt-4o",
  temperature: 0.3,  // Baixo para fidelidade formal
  max_iterations: 5,
  max_tokens_total: 20000,
  extra_params: {
    formal_language: "lean4",
    verify_with_backend: true
  }
}
```

### Processo Visual

```
┌─ Iteração 1: Prova Informal ──────────────────────┐
│ Entrada do Usuário:                              │
│ "Prove por indução que 1+2+...+n = n(n+1)/2"    │
│                                                  │
│ Score: 30% (ainda informal)                      │
│ Feedback: "Estruture para Lean4"                 │
└──────────────────────────────────────────────────┘
        │
        ▼
┌─ Iteração 2-4: Refinamento Progressivo ──────────┐
│ Iteração 2: Semi-formalizado com estrutura      │
│   Score: 60% | Tokens: 1,200                    │
│                                                  │
│ Iteração 3: Syntax Lean4 correto                │
│   Score: 78% | Tokens: 1,800                    │
│                                                  │
│ Iteração 4: Verificado pelo backend             │
│   Score: 92% | Tokens: 2,100                    │
│   ✓ Compila em Lean4!                           │
└──────────────────────────────────────────────────┘
        │
        ▼
┌─ Resultado Final: Prova Formal Verificada ──────┐
│                                                  │
│ theorem sum_formula (n : ℕ) :                   │
│   (Finset.range (n + 1)).sum id = n * (n + 1)/2 │
│ := by                                           │
│   induction n with                              │
│   | zero => simp                                │
│   | succ n ih =>                                │
│     simp [Finset.sum_succ, ih]                 │
│     ring                                        │
│                                                  │
│ ✅ Prova verificada e compilada em Lean4        │
│ 📊 Tokens: 5,100 | Tempo: 24s | Score: 92%     │
│                                                  │
│ [📋 Copiar Código] [⬇️ Download .lean]          │
│ [▶️ Executar em Try-Lean] [🔄 Refinar]          │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🎯 Caso 5: Content Creator - Copywriting

### Scenario
Content creator quer otimizar prompt de copywriting com múltiplos refinamentos rápidos.

### Config
```javascript
originalPrompt: "Escreva um email de vendas para produção XYZ"
technique: "self_refine"
config: {
  provider: "anthropic",  // Claude é bom para copywriting
  model: "claude-3-sonnet",
  temperature: 0.8,  // Mais criativo
  max_iterations: 4,
  max_tokens_total: 8000
}
```

### Quick Workflow

```
┌─ Input ──────────────────────────────────────────┐
│ "Escreva um email de vendas para produção XYZ" │
└───────────────────────────────────────────────────┘
       │
       ▼ [🚀 Melhorar]
┌─────────────────────────────────────────────────┐
│ Streaming em Tempo Real                        │
│                                                │
│ Iteração 1 ▶ 2 ▶ 3 ▶ 4 ✓                      │
│                                                │
│ Progress: [████████████████████] 100%         │
│ Time: 8s | Tokens: 3,200                      │
│ Quality: 96%                                   │
│                                                │
│ ┌─ Resultado ────────────────────────────────┐ │
│ │ Assunto: 🎯 Transforme Seu Workflow em    │ │
│ │           Minutos com [Produto]           │ │
│ │                                            │ │
│ │ Olá [Nome],                                │ │
│ │                                            │ │
│ │ Sabemos como é difícil...                 │ │
│ │ [email completo otimizado]                 │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ [📋 Copiar] [📧 Testar] [🔄 Refinar] [❤️]    │
│                                                │
└─────────────────────────────────────────────────┘
```

---

## 💾 Caso 6: Salvando Configurações Predefinidas

### Fluxo

```javascript
// Salvar uma configuração comum para uso futuro
const saveConfigAsPreset = async () => {
  store.saveConfig('Code Generation - GPT-4', {
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.5,
    max_iterations: 3,
    max_tokens_total: 5000
  });
};

// Usar configuração salva
const loadSavedConfig = (configId) => {
  store.loadConfig(configId);
  // Config agora está em store.currentExecution.config
};

// Listar todas as configurações salvas
const savedConfigs = store.savedConfigs.map((cfg) => (
  <option key={cfg.id} value={cfg.id}>
    {cfg.name} - {cfg.config.provider}/{cfg.config.model}
  </option>
));
```

---

## 🔍 Caso 7: Análise de Histórico

```javascript
export function HistoryAnalytics() {
  const store = useRecursionStore();

  // Técnicas mais usadas
  const usageByTechnique = Object.values(
    store.executionHistory.reduce((acc, exec) => {
      acc[exec.technique] = (acc[exec.technique] || 0) + 1;
      return acc;
    }, {})
  );

  // Melhor resultado por métrica
  const bestQuality = store.getBestResultByMetric('quality_score');
  const bestEfficiency = store.getBestResultByMetric('rer_score');

  // Evolução temporal
  const lastWeek = store.executionHistory.filter(
    (exec) => new Date(exec.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  );

  return (
    <div className="analytics">
      <h2>Analytics</h2>

      <div className="stats">
        <div className="stat-card">
          <h3>Total Execuções</h3>
          <p className="value">{store.executionHistory.length}</p>
        </div>

        <div className="stat-card">
          <h3>Técnica Preferida</h3>
          <p className="value">
            {Object.entries(usageByTechnique).sort(([, a], [, b]) => b - a)[0]?.[0]}
          </p>
        </div>

        <div className="stat-card">
          <h3>Melhor Qualidade</h3>
          <p className="value">
            {(bestQuality?.result?.quality_score * 100).toFixed(0)}%
          </p>
        </div>

        <div className="stat-card">
          <h3>Melhor Eficiência</h3>
          <p className="value">
            {calculateRER(
              bestEfficiency?.result?.quality_score,
              bestEfficiency?.result?.tokens_total
            ).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Gráfico de uso por técnica */}
      <TechniqueUsageChart data={usageByTechnique} />

      {/* Timeline de últimas execuções */}
      <ExecutionTimeline executions={lastWeek} />
    </div>
  );
}
```

---

## 🎓 Padrão de Integração: "Quick Start" Template

```javascript
// Template para desenvolvedores integrarem rapidamente

import { useRecursiveThinking } from '../hooks/useRecursiveThinking';

export function QuickStartExample() {
  const [prompt, setPrompt] = useState('');
  const { improve, status, result, error } = useRecursiveThinking();

  const handleImprove = async () => {
    await improve(prompt, 'self_refine', {
      provider: 'openai',
      model: 'gpt-4o',
      temperature: 0.7,
      max_iterations: 3,
      max_tokens_total: 10000
    });
  };

  return (
    <>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <button onClick={handleImprove} disabled={status !== 'idle'}>
        {status === 'idle' ? 'Melhorar' : `${status}...`}
      </button>

      {error && <ErrorDisplay error={error} />}
      {result && <p>{result.final_answer}</p>}
    </>
  );
}
```

---

## 📋 Checklist de Casos de Uso

- [ ] Desenvolvedor (código)
- [ ] Pesquisador (matemática)
- [ ] Content Creator (copywriting)
- [ ] Modo Comparação implementado
- [ ] Verificação Formal (Lean4)
- [ ] Histórico e Analytics
- [ ] Configurações Predefinidas
- [ ] Export/Import (JSON)
- [ ] Compartilhamento de Resultados
- [ ] Integração com APIs externas

---

**Referências Cruzadas**:
- Arquitetura: `/frontend/docs/00-ARQUITETURA-FRONTEND.md`
- Componentes: `/frontend/docs/01-COMPONENTES-PRINCIPAIS.md`
- Hooks: `/frontend/docs/04-ESTADO-GLOBAL-E-HOOKS.md`
- UX/Fluxo: `/frontend/docs/03-FLUXO-DE-USUARIO.md`
