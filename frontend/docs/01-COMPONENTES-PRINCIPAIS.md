# 01 - Componentes Principais (React)

## 📋 Sumário de Componentes

Este documento detalha a implementação de cada componente React novo e modificado para o Prompt-Boost v2.0.

### Componentes Principais
1. **RecursiveOptions** - Seletor de técnicas e configurações
2. **TechniqueSelector** - Dropdown com 7 técnicas
3. **RecursiveSettings** - Painel de configurações avançadas
4. **IterationVisualizer** - Exibe iterações em timeline
5. **MetricsPanel** - Dashboard de métricas
6. **StreamingOutput** - Exibe status em tempo real
7. **TechniqueComparison** - Compara resultados de múltiplas técnicas
8. **ResultsPanel** - Container que alterna entre modos

---

## 1️⃣ RecursiveOptions (Container)

**Arquivo**: `frontend/src/components/RecursiveOptions/RecursiveOptions.js`

### Função
Container pai que agrupa TechniqueSelector, RecursiveSettings e ComparisonModeToggle. Gerencia estado de configuração e repasssa para MainPage.

### Props

```javascript
interface RecursiveOptionsProps {
  onTechniqueChange: (technique: string) => void;
  onConfigChange: (config: RecursionConfig) => void;
  onComparisonModeChange: (enabled: boolean) => void;
  isLoading?: boolean;
  currentTechnique?: string;
  currentConfig?: RecursionConfig;
}
```

### Estado Interno

```javascript
const [selectedTechnique, setSelectedTechnique] = useState('self_refine');
const [config, setConfig] = useState({
  provider: 'openai',
  model: 'gpt-4o',
  temperature: 0.7,
  max_iterations: 3,
  max_tokens_total: 10000,
  extra_params: {}
});
const [comparisonMode, setComparisonMode] = useState(false);
```

### Estrutura JSX

```javascript
export default function RecursiveOptions({
  onTechniqueChange,
  onConfigChange,
  onComparisonModeChange,
  isLoading = false,
  currentTechnique = 'self_refine',
  currentConfig = {}
}) {
  const [selectedTechnique, setSelectedTechnique] = useState(currentTechnique);
  const [config, setConfig] = useState({...DEFAULT_CONFIG, ...currentConfig});
  const [comparisonMode, setComparisonMode] = useState(false);

  const handleTechniqueChange = (technique) => {
    setSelectedTechnique(technique);
    onTechniqueChange(technique);
  };

  const handleConfigChange = (newConfig) => {
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  return (
    <div className="recursive-options">
      <h3>Opções de Raciocínio Recursivo</h3>
      
      <TechniqueSelector 
        selected={selectedTechnique}
        onChange={handleTechniqueChange}
        disabled={isLoading}
      />
      
      <RecursiveSettings 
        config={config}
        onChange={handleConfigChange}
        disabled={isLoading}
      />
      
      <ComparisonModeToggle
        enabled={comparisonMode}
        onChange={(enabled) => {
          setComparisonMode(enabled);
          onComparisonModeChange(enabled);
        }}
        disabled={isLoading}
      />
    </div>
  );
}
```

### Callbacks Executados

- `onTechniqueChange(technique)`: MainPage atualiza `selectedTechnique`
- `onConfigChange(config)`: MainPage atualiza `recursionConfig`
- `onComparisonModeChange(enabled)`: MainPage ativa/desativa modo comparação

---

## 2️⃣ TechniqueSelector

**Arquivo**: `frontend/src/components/RecursiveOptions/TechniqueSelector.js`

### Função
Dropdown/Radio group para selecionar qual técnica usar.

### Props

```javascript
interface TechniqueSelectorProps {
  selected: string;
  onChange: (technique: string) => void;
  disabled?: boolean;
}
```

### Constantes (em `frontend/src/utils/constants.js`)

```javascript
export const TECHNIQUES = {
  SELF_REFINE: {
    id: 'self_refine',
    label: 'Self-Refine',
    description: 'Melhoria iterativa via crítica interna',
    icon: '🔄',
    category: 'Básico',
    bestFor: 'Prompts gerais'
  },
  TOT: {
    id: 'tot',
    label: 'Tree of Thoughts',
    description: 'Exploração em árvore com backtracking',
    icon: '🌳',
    category: 'Avançado',
    bestFor: 'Problemas estruturados'
  },
  GOT: {
    id: 'got',
    label: 'Graph of Thoughts',
    description: 'Exploração em grafo com múltiplos caminhos',
    icon: '🕸️',
    category: 'Avançado',
    bestFor: 'Problemas complexos interdependentes'
  },
  LLM_MCTS: {
    id: 'llm_mcts',
    label: 'LLM-MCTS',
    description: 'Monte Carlo Tree Search com LLM',
    icon: '🎲',
    category: 'Avançado',
    bestFor: 'Busca otimizada'
  },
  DEBATE: {
    id: 'debate',
    label: 'Multi-Agent Debate',
    description: 'Múltiplos agentes debatendo soluções',
    icon: '🗣️',
    category: 'Especialista',
    bestFor: 'Problemas com múltiplas perspectivas'
  },
  ALIGNMENT: {
    id: 'alignment',
    label: 'Recursive Alignment',
    description: 'Verificação formal com constraints',
    icon: '✓',
    category: 'Especialista',
    bestFor: 'Verificação de correção'
  },
  AUTOFORMAL: {
    id: 'autoformal',
    label: 'AutoFormalization',
    description: 'Conversão para prova formal (Lean4)',
    icon: '📐',
    category: 'Especialista',
    bestFor: 'Provas matemáticas'
  }
};
```

### Implementação

```javascript
import { TECHNIQUES } from '../../utils/constants';
import './TechniqueSelector.css';

export default function TechniqueSelector({ selected, onChange, disabled = false }) {
  return (
    <div className="technique-selector">
      <label>Técnica de Raciocínio</label>
      
      <div className="technique-grid">
        {Object.values(TECHNIQUES).map((tech) => (
          <div
            key={tech.id}
            className={`technique-card ${selected === tech.id ? 'active' : ''}`}
            onClick={() => !disabled && onChange(tech.id)}
          >
            <div className="technique-icon">{tech.icon}</div>
            <div className="technique-label">{tech.label}</div>
            <div className="technique-category">{tech.category}</div>
            <div className="technique-description">{tech.description}</div>
            <div className="technique-best-for">{tech.bestFor}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### CSS (em `frontend/src/styles/RecursiveOptions.css`)

```css
.technique-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.technique-card {
  border: 2px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg-primary);
}

.technique-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 102, 204, 0.1);
  transform: translateY(-2px);
}

.technique-card.active {
  border-color: var(--color-primary);
  background: rgba(0, 102, 204, 0.05);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
}

.technique-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.technique-label {
  font-weight: 600;
  font-size: 1.05rem;
  margin-bottom: 0.25rem;
}

.technique-category {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.technique-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.technique-best-for {
  font-size: 0.75rem;
  font-style: italic;
  color: var(--color-text-secondary);
}
```

---

## 3️⃣ RecursiveSettings

**Arquivo**: `frontend/src/components/RecursiveOptions/RecursiveSettings.js`

### Função
Painel de configurações para ajustar parâmetros de recursão e modelo.

### Props

```javascript
interface RecursiveSettingsProps {
  config: RecursionConfig;
  onChange: (newConfig: RecursionConfig) => void;
  disabled?: boolean;
}

interface RecursionConfig {
  provider: string;
  model: string;
  temperature: number;
  max_iterations: number;
  max_tokens_total: number;
  extra_params: object;
}
```

### Implementação

```javascript
import { useState, useEffect } from 'react';
import { PROVIDERS, MODELS_BY_PROVIDER } from '../../utils/constants';

export default function RecursiveSettings({ config, onChange, disabled = false }) {
  const [expanded, setExpanded] = useState(false);
  const [localConfig, setLocalConfig] = useState(config);
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    setAvailableModels(MODELS_BY_PROVIDER[localConfig.provider] || []);
  }, [localConfig.provider]);

  const handleChange = (field, value) => {
    const updated = { ...localConfig, [field]: value };
    setLocalConfig(updated);
    onChange(updated);
  };

  const handleExtraParamChange = (key, value) => {
    const updated = {
      ...localConfig,
      extra_params: { ...localConfig.extra_params, [key]: value }
    };
    setLocalConfig(updated);
    onChange(updated);
  };

  return (
    <div className="recursive-settings">
      <button 
        className="settings-toggle"
        onClick={() => setExpanded(!expanded)}
        disabled={disabled}
      >
        ⚙️ Configurações {expanded ? '▼' : '▶'}
      </button>

      {expanded && (
        <div className="settings-panel">
          
          {/* Provider Selection */}
          <div className="setting-group">
            <label>Provider LLM</label>
            <select 
              value={localConfig.provider}
              onChange={(e) => handleChange('provider', e.target.value)}
              disabled={disabled}
            >
              {Object.values(PROVIDERS).map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          {/* Model Selection */}
          <div className="setting-group">
            <label>Modelo</label>
            <select 
              value={localConfig.model}
              onChange={(e) => handleChange('model', e.target.value)}
              disabled={disabled}
            >
              {availableModels.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.inputPrice}/${m.outputPrice} por 1M tokens)
                </option>
              ))}
            </select>
          </div>

          {/* Temperature Slider */}
          <div className="setting-group">
            <label>Temperatura: {localConfig.temperature.toFixed(2)}</label>
            <input 
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={localConfig.temperature}
              onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
              disabled={disabled}
            />
            <small>Mais baixo = mais determinístico, Mais alto = mais criativo</small>
          </div>

          {/* Max Iterations */}
          <div className="setting-group">
            <label>Máximo de Iterações: {localConfig.max_iterations}</label>
            <input 
              type="range"
              min="1"
              max="10"
              step="1"
              value={localConfig.max_iterations}
              onChange={(e) => handleChange('max_iterations', parseInt(e.target.value))}
              disabled={disabled}
            />
          </div>

          {/* Max Tokens */}
          <div className="setting-group">
            <label>Máximo de Tokens Totais</label>
            <input 
              type="number"
              min="1000"
              max="100000"
              step="1000"
              value={localConfig.max_tokens_total}
              onChange={(e) => handleChange('max_tokens_total', parseInt(e.target.value))}
              disabled={disabled}
            />
            <small>Limite de tokens para toda operação recursiva</small>
          </div>

          {/* Advanced Toggle */}
          <details className="advanced-params">
            <summary>Parâmetros Avançados</summary>
            
            {/* Técnica-específica */}
            {localConfig.provider === 'openai' && (
              <div className="setting-group">
                <label>
                  <input 
                    type="checkbox"
                    checked={localConfig.extra_params.use_reasoning_effort || false}
                    onChange={(e) => handleExtraParamChange('use_reasoning_effort', e.target.checked)}
                    disabled={disabled}
                  />
                  Usar Reasoning Effort (para o1-preview)
                </label>
              </div>
            )}

            <div className="setting-group">
              <label>Seed (para reprodutibilidade)</label>
              <input 
                type="number"
                value={localConfig.extra_params.seed || ''}
                onChange={(e) => handleExtraParamChange('seed', e.target.value ? parseInt(e.target.value) : null)}
                disabled={disabled}
                placeholder="Deixe vazio para aleatório"
              />
            </div>
          </details>

        </div>
      )}
    </div>
  );
}
```

### CSS

```css
.recursive-settings {
  margin: 1.5rem 0;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg-secondary);
}

.settings-toggle {
  width: 100%;
  padding: 1rem;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  text-align: left;
  font-weight: 600;
  transition: background 0.2s;
}

.settings-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
}

.settings-panel {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-group label {
  font-weight: 600;
  font-size: 0.95rem;
}

.setting-group input[type="range"],
.setting-group select,
.setting-group input[type="number"] {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.95rem;
}

.setting-group small {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.advanced-params {
  grid-column: 1 / -1;
  padding: 1rem;
  background: var(--color-bg-primary);
  border-radius: 4px;
}

.advanced-params summary {
  cursor: pointer;
  font-weight: 600;
  user-select: none;
}
```

---

## 4️⃣ IterationVisualizer

**Arquivo**: `frontend/src/components/Results/IterationVisualizer.js`

### Função
Exibe timeline de iterações com cards contendo dados de cada passo.

### Props

```javascript
interface IterationVisualizerProps {
  iterations: IterationRecord[];
  isLoading?: boolean;
  compact?: boolean; // true = versão compacta para comparação
}

interface IterationRecord {
  iteration_number: number;
  timestamp: string;
  generated_candidates: string[];
  evaluation_scores: number[];
  selected_best: string;
  feedback_from_critic: string;
  tokens_this_iteration: number;
  extra_data?: object;
}
```

### Implementação

```javascript
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './IterationVisualizer.css';

export default function IterationVisualizer({ 
  iterations = [], 
  isLoading = false,
  compact = false 
}) {
  const [expandedIteration, setExpandedIteration] = useState(null);

  if (isLoading) {
    return (
      <div className="iteration-visualizer loading">
        <div className="loader">Gerando iterações...</div>
      </div>
    );
  }

  if (!iterations || iterations.length === 0) {
    return <div className="iteration-visualizer empty">Sem iterações para exibir</div>;
  }

  return (
    <div className={`iteration-visualizer ${compact ? 'compact' : 'full'}`}>
      <h4>Processo de Melhoria Iterativa</h4>
      
      <div className="iterations-timeline">
        {iterations.map((iter, idx) => (
          <div 
            key={idx}
            className={`iteration-card ${expandedIteration === idx ? 'expanded' : ''}`}
          >
            {/* Card Header */}
            <div 
              className="iteration-header"
              onClick={() => setExpandedIteration(expandedIteration === idx ? null : idx)}
            >
              <div className="iteration-number">
                <span className="badge">#{iter.iteration_number}</span>
              </div>
              <div className="iteration-summary">
                <div className="best-score">
                  Score: <strong>{(Math.max(...iter.evaluation_scores) * 100).toFixed(0)}%</strong>
                </div>
                <div className="tokens-info">
                  {iter.tokens_this_iteration} tokens
                </div>
              </div>
              <div className="expand-icon">
                {expandedIteration === idx ? '▼' : '▶'}
              </div>
            </div>

            {/* Expandable Content */}
            {expandedIteration === idx && (
              <div className="iteration-details">
                
                {/* Candidates */}
                <div className="detail-section">
                  <h5>Candidatos Gerados ({iter.generated_candidates.length})</h5>
                  <div className="candidates-list">
                    {iter.generated_candidates.map((candidate, cIdx) => (
                      <div key={cIdx} className="candidate">
                        <div className="candidate-header">
                          <span className="candidate-label">Opção {cIdx + 1}</span>
                          <span className="candidate-score">
                            Score: {(iter.evaluation_scores[cIdx] * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="candidate-text">
                          <ReactMarkdown>{candidate}</ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Feedback */}
                {iter.feedback_from_critic && (
                  <div className="detail-section feedback">
                    <h5>Crítica do Modelo</h5>
                    <div className="feedback-text">
                      <ReactMarkdown>{iter.feedback_from_critic}</ReactMarkdown>
                    </div>
                  </div>
                )}

                {/* Selected Best */}
                <div className="detail-section selected">
                  <h5>✓ Melhor Selecionado</h5>
                  <div className="selected-text">
                    <ReactMarkdown>{iter.selected_best}</ReactMarkdown>
                  </div>
                </div>

                {/* Extra Data (técnica-específica) */}
                {iter.extra_data && Object.keys(iter.extra_data).length > 0 && (
                  <div className="detail-section extra">
                    <h5>Dados Adicionais</h5>
                    <pre>{JSON.stringify(iter.extra_data, null, 2)}</pre>
                  </div>
                )}

              </div>
            )}

            {/* Timeline Connector */}
            {idx < iterations.length - 1 && <div className="timeline-connector" />}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### CSS

```css
.iteration-visualizer {
  margin: 2rem 0;
}

.iteration-visualizer.empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.iteration-visualizer.loading {
  padding: 2rem;
  text-align: center;
}

.loader {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.iterations-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
}

.iteration-card {
  background: var(--color-iteration-bg);
  border: 1px solid #d0e4f7;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.iteration-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.iteration-header {
  display: grid;
  grid-template-columns: 60px 1fr 40px;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: white;
  cursor: pointer;
  user-select: none;
}

.iteration-number .badge {
  display: inline-block;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0066cc, #003d99);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.iteration-summary {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.best-score {
  font-size: 0.95rem;
}

.best-score strong {
  color: var(--color-success);
  font-size: 1.1rem;
}

.tokens-info {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.expand-icon {
  text-align: center;
  font-size: 0.8rem;
}

.iteration-details {
  padding: 1.5rem;
  background: white;
  border-top: 1px solid #d0e4f7;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  border-left: 3px solid var(--color-primary);
  padding-left: 1rem;
}

.detail-section h5 {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  font-weight: 600;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.candidate {
  background: var(--color-bg-secondary);
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 2px solid var(--color-warning);
}

.candidate-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.candidate-text {
  font-size: 0.9rem;
  line-height: 1.4;
}

.detail-section.feedback {
  border-left-color: var(--color-warning);
  background: rgba(255, 193, 7, 0.05);
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 3px solid var(--color-warning);
}

.detail-section.selected {
  border-left-color: var(--color-success);
  background: rgba(40, 167, 69, 0.05);
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 3px solid var(--color-success);
}

.selected-text {
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.5;
}

.detail-section.extra pre {
  background: var(--color-bg-secondary);
  padding: 0.75rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.8rem;
}

.timeline-connector {
  width: 2px;
  height: 0.5rem;
  background: #d0e4f7;
  margin-left: 29px;
}

.iteration-visualizer.compact .iteration-card {
  margin-bottom: 0.5rem;
}

.iteration-visualizer.compact .iteration-header {
  padding: 0.75rem;
  grid-template-columns: 50px 1fr 30px;
  font-size: 0.9rem;
}

.iteration-visualizer.compact .iteration-details {
  max-height: 200px;
  overflow-y: auto;
  font-size: 0.85rem;
}
```

---

## 5️⃣ MetricsPanel

**Arquivo**: `frontend/src/components/Results/MetricsPanel.js`

### Função
Exibe KPIs da execução: tokens, tempo, qualidade, RER score.

### Props

```javascript
interface MetricsPanelProps {
  result: RecursionResult;
  technique: string;
  isLoading?: boolean;
}

interface RecursionResult {
  final_answer: string;
  iterations_count: number;
  tokens_total: number;
  time_total_ms: number;
  quality_score?: number;
  all_iterations: IterationRecord[];
}
```

### Implementação

```javascript
import { formatDistanceStrict } from 'date-fns';
import './MetricsPanel.css';

function calculateRER(qualityImprovement, tokensAdded) {
  // RER = Improvement (%) / (Tokens Adicionais / 1000)
  if (tokensAdded === 0) return qualityImprovement * 100;
  return (qualityImprovement * 100) / (tokensAdded / 1000);
}

function getQualityLevel(score) {
  if (score >= 0.9) return { label: 'Excelente', color: '#28a745' };
  if (score >= 0.75) return { label: 'Bom', color: '#17a2b8' };
  if (score >= 0.6) return { label: 'Aceitável', color: '#ffc107' };
  return { label: 'Abaixo', color: '#dc3545' };
}

export default function MetricsPanel({ result, technique, isLoading = false }) {
  if (isLoading) {
    return <div className="metrics-panel loading">Coletando métricas...</div>;
  }

  if (!result) {
    return <div className="metrics-panel empty">Nenhuma execução realizada</div>;
  }

  const qualityLevel = getQualityLevel(result.quality_score || 0.7);
  const rer = calculateRER(result.quality_score || 0.7, result.tokens_total);
  const timeInSeconds = (result.time_total_ms / 1000).toFixed(2);

  return (
    <div className="metrics-panel">
      <h4>Métricas da Execução</h4>
      
      <div className="metrics-grid">
        
        {/* Iterações */}
        <div className="metric-card">
          <div className="metric-icon">🔄</div>
          <div className="metric-info">
            <div className="metric-label">Iterações</div>
            <div className="metric-value">{result.iterations_count}</div>
          </div>
        </div>

        {/* Tokens */}
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-info">
            <div className="metric-label">Tokens Utilizados</div>
            <div className="metric-value">{result.tokens_total.toLocaleString()}</div>
          </div>
        </div>

        {/* Tempo */}
        <div className="metric-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-info">
            <div className="metric-label">Tempo Total</div>
            <div className="metric-value">{timeInSeconds}s</div>
          </div>
        </div>

        {/* Qualidade */}
        <div className="metric-card">
          <div className="metric-icon">⭐</div>
          <div className="metric-info">
            <div className="metric-label">Qualidade</div>
            <div className="metric-value" style={{color: qualityLevel.color}}>
              {(result.quality_score * 100).toFixed(0)}%
            </div>
            <div className="metric-sublabel">{qualityLevel.label}</div>
          </div>
        </div>

        {/* RER Score */}
        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-info">
            <div className="metric-label">RER Score</div>
            <div className="metric-value">{rer.toFixed(2)}</div>
            <div className="metric-sublabel">Eficiência de Recursão</div>
          </div>
        </div>

        {/* Técnica */}
        <div className="metric-card">
          <div className="metric-icon">🧠</div>
          <div className="metric-info">
            <div className="metric-label">Técnica Usada</div>
            <div className="metric-value">{technique}</div>
          </div>
        </div>

      </div>

      {/* Detalhes por Iteração */}
      <div className="iteration-breakdown">
        <h5>Consumo por Iteração</h5>
        <div className="breakdown-table">
          <div className="breakdown-header">
            <div className="col col-iter">Iter.</div>
            <div className="col col-tokens">Tokens</div>
            <div className="col col-score">Score</div>
            <div className="col col-time">Tempo (ms)</div>
          </div>
          {result.all_iterations.map((iter, idx) => (
            <div key={idx} className="breakdown-row">
              <div className="col col-iter">#{iter.iteration_number}</div>
              <div className="col col-tokens">{iter.tokens_this_iteration}</div>
              <div className="col col-score">
                {(Math.max(...iter.evaluation_scores) * 100).toFixed(0)}%
              </div>
              <div className="col col-time">
                {(iter.extra_data?.time_ms || '-')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### CSS

```css
.metrics-panel {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.metrics-panel.empty,
.metrics-panel.loading {
  color: var(--color-text-secondary);
  text-align: center;
  padding: 2rem;
}

.metrics-panel h4 {
  margin: 0 0 1rem 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.metric-icon {
  font-size: 2rem;
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-text-primary);
}

.metric-sublabel {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.iteration-breakdown {
  border-top: 1px solid var(--color-border);
  padding-top: 1.5rem;
  margin-top: 1.5rem;
}

.iteration-breakdown h5 {
  margin: 0 0 1rem 0;
}

.breakdown-table {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--color-bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.breakdown-header,
.breakdown-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0.5rem;
  padding: 0.75rem;
  align-items: center;
}

.breakdown-header {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  font-size: 0.85rem;
}

.breakdown-row {
  background: white;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

.breakdown-row:last-child {
  border-bottom: none;
}

.col {
  text-align: center;
}

.col.col-iter,
.col.col-tokens {
  text-align: left;
}
```

---

## Próximas Seções

Os componentes **StreamingOutput**, **TechniqueComparison** e **ResultsPanel** serão documentados em detalhes nos próximos arquivos de documentação.

---

**Referências Cruzadas**:
- Estado Global: `/frontend/docs/04-ESTADO-GLOBAL-E-HOOKS.md`
- WebSocket: `/frontend/docs/02-INTEGRACAO-WEBSOCKET.md`
- Arquitetura: `/frontend/docs/00-ARQUITETURA-FRONTEND.md`
