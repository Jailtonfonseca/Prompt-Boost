# 09 - Guia de Implementação Prática no Prompt-Boost

## 🎯 Objetivo

Este documento fornece instruções **passo-a-passo** para implementar técnicas de raciocínio recursivo no backend do Prompt-Boost.

---

## 🏗️ Arquitetura Atual vs Nova

### Arquitetura Atual (v1.4.0)

```
main.py
├─ FastAPI app
├─ Endpoints básicos (/api/improve-prompt)
└─ recursion.py (Self-Refine simples)
```

### Arquitetura Nova Proposta

```
main.py
├─ FastAPI app
├─ Novo endpoint: /api/improve-prompt-recursive
├─ WebSocket: /ws/recursive (streaming)
└─ RecursionRouter (dispatcher)
    ├─ tot_engine.py (ToT/GoT)
    ├─ self_refine_engine.py (Self-Refine/Reflexion)
    ├─ alignment_engine.py (Verificação formal)
    ├─ mcts_engine.py (LLM-MCTS)
    ├─ debate_engine.py (Multi-Agent)
    ├─ autoformal_engine.py (Prova formal)
    └─ base_engine.py (Abstração comum)
```

---

## 📝 Passo 1: Refatorar recursion.py

### Criar base_engine.py

```python
# backend/engines/base_engine.py

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class RecursionState(BaseModel):
    """Estado compartilhado por todas técnicas"""
    execution_id: str
    technique: str
    original_prompt: str
    current_prompt: str
    iteration: int = 0
    tokens_used: int = 0
    compute_time: float = 0.0
    all_iterations: List[Dict] = []
    best_solution: Optional[Dict] = None
    memory_pool: Dict = {}

class IterationRecord(BaseModel):
    """Um passo do loop recursivo"""
    iteration_number: int
    timestamp: datetime
    generated_candidates: List[str]
    evaluation_scores: List[float]
    selected_best: str
    feedback_from_critic: str
    tokens_this_iteration: int
    extra_data: Dict = {}

class RecursionConfig(BaseModel):
    """Configuração compartilhada"""
    technique: str
    provider: str
    model: str
    temperature: float = 0.7
    max_iterations: int = 3
    max_tokens_total: int = 10000
    max_time_ms: int = 120000
    extra_params: Dict = {}

class RecursionResult(BaseModel):
    """Resultado final"""
    final_answer: str
    iterations_count: int
    tokens_total: int
    time_total_ms: float
    all_iterations: List[IterationRecord]
    metadata: Dict

class RecursiveThinkingEngine(ABC):
    """Base class para todos engines"""
    
    @abstractmethod
    def run(
        self, 
        prompt: str, 
        config: RecursionConfig
    ) -> RecursionResult:
        """Execute técnica recursiva"""
        pass
    
    def _call_model(self, **kwargs) -> str:
        """Helper para chamar modelo"""
        # Usar providers.py existente
        from providers import create_provider
        provider = create_provider(
            kwargs.get("provider"),
            kwargs.get("api_key")
        )
        return provider.generate(
            system_prompt=kwargs.get("system_prompt", ""),
            user_prompt=kwargs.get("user_prompt", ""),
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000)
        )
```

### Atualizar recursion.py

```python
# backend/recursion.py (refatorado)

from engines.base_engine import (
    RecursionState, RecursionConfig, RecursionResult,
    IterationRecord, RecursiveThinkingEngine
)

from engines.self_refine_engine import SelfRefineEngine
from engines.tot_engine import TreeOfThoughtsEngine
from engines.debate_engine import MultiAgentDebateEngine
# ... importar outros engines

class RecursionRouter:
    """Dispatcher central para técnicas"""
    
    ENGINES = {
        "none": None,
        "self_refine": SelfRefineEngine,
        "reflexion": SelfRefineEngine,  # Mesma engine, config diferente
        "tot": TreeOfThoughtsEngine,
        "got": TreeOfThoughtsEngine,
        "multi_agent_debate": MultiAgentDebateEngine,
        "alignment": AlignmentEngine,
        "mcts": MCTSEngine,
        "autoformal": AutoformalEngine,
    }
    
    @classmethod
    def route(
        cls,
        technique: str,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """Rotear para técnica apropriada"""
        
        if technique not in cls.ENGINES:
            raise ValueError(f"Técnica desconhecida: {technique}")
        
        if technique == "none":
            # Retornar CoT baseline
            return cls._run_cot(prompt, config)
        
        engine_class = cls.ENGINES[technique]
        engine = engine_class()
        
        return engine.run(prompt, config)
    
    @staticmethod
    def _run_cot(prompt: str, config: RecursionConfig) -> RecursionResult:
        """Baseline: Chain-of-Thought simples"""
        # Implementação CoT existente
        pass
```

---

## 🔌 Passo 2: Criar Novos Endpoints

### main.py (modificações)

```python
# backend/main.py - adicionar

from fastapi import WebSocket
from fastapi.responses import StreamingResponse
import asyncio
from recursion import RecursionRouter, RecursionConfig

# ─────────────────────────────────────────
# ENDPOINT 1: Recursive Improvement (POST)
# ─────────────────────────────────────────

@app.post("/api/improve-prompt-recursive")
async def improve_prompt_recursive(request: dict) -> dict:
    """
    Endpoint principal para técnicas recursivas
    
    Payload:
    {
        "prompt": "string",
        "technique": "tot|self_refine|...",
        "config": {
            "provider": "openai",
            "model": "gpt-4o",
            "max_iterations": 3,
            ...
        }
    }
    """
    
    try:
        prompt = request.get("prompt", "")
        technique = request.get("technique", "self_refine")
        config_dict = request.get("config", {})
        
        # Validar
        if not prompt:
            return {"error": "Prompt vazio"}
        
        # Criar config
        config = RecursionConfig(
            technique=technique,
            provider=config_dict.get("provider", "openai"),
            model=config_dict.get("model", "gpt-4o"),
            temperature=config_dict.get("temperature", 0.7),
            max_iterations=config_dict.get("max_iterations", 3),
            max_tokens_total=config_dict.get("max_tokens_total", 10000),
            max_time_ms=config_dict.get("max_time_ms", 120000),
            extra_params=config_dict.get("extra_params", {})
        )
        
        # Executar via router
        result = RecursionRouter.route(
            technique=technique,
            prompt=prompt,
            config=config
        )
        
        return {
            "success": True,
            "final_answer": result.final_answer,
            "iterations_count": result.iterations_count,
            "tokens_total": result.tokens_total,
            "time_total_ms": result.time_total_ms,
            "metadata": result.metadata
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ─────────────────────────────────────────
# ENDPOINT 2: WebSocket Streaming
# ─────────────────────────────────────────

@app.websocket("/ws/recursive")
async def websocket_recursive(websocket: WebSocket):
    """
    WebSocket para streaming de iterações em tempo real
    
    Mensagens recebidas:
    {
        "action": "start",
        "prompt": "...",
        "technique": "...",
        "config": {...}
    }
    
    Mensagens enviadas:
    {
        "type": "iteration",
        "iteration_number": 1,
        "generated": "...",
        "score": 0.85,
        "feedback": "..."
    }
    {
        "type": "complete",
        "final_answer": "...",
        "iterations_count": 3
    }
    """
    
    await websocket.accept()
    
    try:
        # Receber configuração
        init_msg = await websocket.receive_json()
        
        prompt = init_msg.get("prompt", "")
        technique = init_msg.get("technique", "self_refine")
        config_dict = init_msg.get("config", {})
        
        config = RecursionConfig(**config_dict, technique=technique)
        
        # Wrapper para capturar iterações
        class StreamingEngine(RecursionRouter.ENGINES[technique]):
            async def run_streaming(self, prompt, config, ws):
                """Run com callbacks WebSocket"""
                # Overriding run() para enviar updates
                # (implementação específica por engine)
                pass
        
        # Executar e streamar
        async for update in stream_recursive(prompt, technique, config):
            await websocket.send_json(update)
        
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    
    finally:
        await websocket.close()

# ─────────────────────────────────────────
# ENDPOINT 3: Listar Técnicas Disponíveis
# ─────────────────────────────────────────

@app.get("/api/recursive-techniques")
async def list_techniques() -> dict:
    """Listar técnicas disponíveis"""
    
    return {
        "techniques": [
            {
                "id": "self_refine",
                "name": "Self-Refine",
                "description": "Refinamento iterativo com crítica",
                "complexity": "baixa",
                "est_tokens_per_iteration": 1500,
                "typical_iterations": 3
            },
            {
                "id": "tot",
                "name": "Tree of Thoughts",
                "description": "Exploração de múltiplos caminhos",
                "complexity": "alta",
                "est_tokens_per_iteration": 3000,
                "typical_iterations": 5
            },
            # ... outras técnicas
        ]
    }
```

---

## 📁 Passo 3: Estrutura de Pastas

```
backend/
├── main.py                    (modificado)
├── recursion.py              (refatorado → RecursionRouter)
├── providers.py              (existente)
├── database.py               (existente)
├── engines/                  (NOVO)
│   ├── __init__.py
│   ├── base_engine.py        (abstração)
│   ├── self_refine_engine.py
│   ├── tot_engine.py
│   ├── alignment_engine.py
│   ├── mcts_engine.py
│   ├── debate_engine.py
│   └── autoformal_engine.py
├── verifiers/                (NOVO - para Alignment/Autoformal)
│   ├── __init__.py
│   ├── lean4_verifier.py
│   ├── isabelle_verifier.py
│   └── coq_verifier.py
├── utils/                    (NOVO - utilitários)
│   ├── __init__.py
│   ├── token_counter.py
│   ├── embedding.py          (para Reflexion)
│   └── validators.py
└── requirements.txt          (modificado)
```

---

## 📦 Passo 4: Atualizar Dependências

```bash
# backend/requirements.txt

# Existentes
fastapi
uvicorn[standard]
openai
pydantic-settings
python-decouple
requests
pytest
pytest-asyncio
httpx
google-generativeai

# Novos para técnicas recursivas
networkx                # Para grafos (ToT/GoT)
z3-solver               # Para verificação simbólica
numpy                   # Para MCTS
matplotlib              # Para visualização
aiohttp                 # Para async HTTP
redis                   # Para caching (opcional)

# Optionais para verificadores
# lean4                 # Instalação manual: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
# isabelle              # Instalação manual
```

---

## 🔄 Passo 5: Integração com Frontend

### Frontend: Seleção de Técnica

```javascript
// frontend/src/RecursiveOptions.js

import React, { useState } from 'react';

export function RecursiveOptions({ onRun }) {
    const [technique, setTechnique] = useState('self_refine');
    const [maxIterations, setMaxIterations] = useState(3);
    const [useWebSocket, setUseWebSocket] = useState(true);
    
    const techniques = [
        { id: 'none', label: 'Nenhuma (CoT)', icon: '🔄' },
        { id: 'self_refine', label: 'Self-Refine', icon: '✨' },
        { id: 'tot', label: 'Tree of Thoughts', icon: '🌳' },
        { id: 'multi_agent_debate', label: 'Debate', icon: '🗣️' },
        { id: 'reflexion', label: 'Reflexion', icon: '💭' },
        { id: 'alignment', label: 'Alignment', icon: '✓' },
        { id: 'mcts', label: 'MCTS', icon: '🎲' },
        { id: 'autoformal', label: 'Prova Formal', icon: '📐' },
    ];
    
    const handleRun = () => {
        onRun({
            technique,
            config: {
                max_iterations: maxIterations,
                temperature: 0.7,
                use_streaming: useWebSocket
            }
        });
    };
    
    return (
        <div className="recursive-options">
            <h3>Técnica de Raciocínio Recursivo</h3>
            
            <div className="technique-grid">
                {techniques.map(t => (
                    <button
                        key={t.id}
                        className={`technique-btn ${technique === t.id ? 'active' : ''}`}
                        onClick={() => setTechnique(t.id)}
                    >
                        <span>{t.icon}</span>
                        <span>{t.label}</span>
                    </button>
                ))}
            </div>
            
            <div className="controls">
                <label>
                    Máximo de iterações: {maxIterations}
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={maxIterations}
                        onChange={(e) => setMaxIterations(parseInt(e.target.value))}
                    />
                </label>
                
                <label>
                    <input
                        type="checkbox"
                        checked={useWebSocket}
                        onChange={(e) => setUseWebSocket(e.target.checked)}
                    />
                    Stream em tempo real
                </label>
            </div>
            
            <button onClick={handleRun} className="run-btn">
                Executar Recursivo
            </button>
        </div>
    );
}
```

### Frontend: Visualização de Iterações

```javascript
// frontend/src/IterationVisualizer.js

export function IterationVisualizer({ iterations, technique }) {
    return (
        <div className="iterations-container">
            {iterations.map((iter, idx) => (
                <div key={idx} className="iteration-card">
                    <h4>Iteração {iter.iteration_number}</h4>
                    
                    {/* Mostrar candidatos gerados */}
                    <div className="candidates">
                        {iter.generated_candidates.slice(0, 3).map((cand, i) => (
                            <div key={i} className="candidate">
                                <span className="score">
                                    Score: {iter.evaluation_scores[i]?.toFixed(2)}
                                </span>
                                <p>{cand.substring(0, 100)}...</p>
                            </div>
                        ))}
                    </div>
                    
                    {/* Feedback do crítico */}
                    {iter.feedback_from_critic && (
                        <div className="feedback">
                            <strong>Crítica:</strong>
                            <p>{iter.feedback_from_critic}</p>
                        </div>
                    )}
                    
                    {/* Técnica específica */}
                    {technique === 'tot' && iter.extra_data?.tree_depth && (
                        <div className="tot-stats">
                            Profundidade: {iter.extra_data.tree_depth}
                            | Nós: {iter.extra_data.nodes_count}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
```

---

## 🧪 Passo 6: Testes

```python
# backend/test_recursive_engines.py

import pytest
from engines.self_refine_engine import SelfRefineEngine
from engines.tot_engine import TreeOfThoughtsEngine
from base_engine import RecursionConfig

@pytest.fixture
def config():
    return RecursionConfig(
        technique="self_refine",
        provider="openai",
        model="gpt-4o",
        temperature=0.7,
        max_iterations=2,
        max_tokens_total=5000
    )

def test_self_refine_improves(config):
    """Testar que Self-Refine melhora o prompt"""
    engine = SelfRefineEngine()
    
    initial_prompt = "Um bom prompt é..."  # Prompt ruim
    result = engine.run(initial_prompt, config)
    
    assert result.iterations_count == 2
    assert len(result.all_iterations) == 2
    assert len(result.final_answer) > len(initial_prompt)

def test_tot_explores_branches(config):
    """Testar que ToT explora múltiplos caminhos"""
    config.technique = "tot"
    config.extra_params = {"k_candidates": 3, "beam_width": 2}
    
    engine = TreeOfThoughtsEngine()
    result = engine.run("Resolva: 2x + 5 = 13", config)
    
    assert "tree_depth" in result.metadata
    assert "nodes_generated" in result.metadata
    assert result.metadata["tree_depth"] > 1

def test_token_counting(config):
    """Testar que tokens são contados corretamente"""
    engine = SelfRefineEngine()
    result = engine.run("Teste", config)
    
    assert result.tokens_total > 0
    assert result.tokens_total < config.max_tokens_total
```

---

## 🚀 Plano de Rollout

### Semana 1-2
- [ ] Implementar base_engine.py
- [ ] Refatorar recursion.py
- [ ] Criar self_refine_engine.py
- [ ] Testar Self-Refine

### Semana 3-4
- [ ] Implementar tot_engine.py
- [ ] Criar endpoints /api/improve-prompt-recursive
- [ ] Frontend: seletor de técnica
- [ ] Testar ToT

### Semana 5-6
- [ ] Multi-Agent Debate
- [ ] WebSocket streaming
- [ ] Visualização de iterações
- [ ] Benchmarking

### Semana 7-8
- [ ] Alignment + verificadores
- [ ] LLM-MCTS
- [ ] Documentação de deployment
- [ ] Release 2.0.0

---

## ✅ Checklist de Release

- [ ] Todos tests passando
- [ ] Documentação README atualizada
- [ ] CHANGELOG.md com v2.0.0
- [ ] Docker build funcional
- [ ] Performance baseline medido
- [ ] Exemplos de uso documentados

---

**Próximo**: [11-CASOS-DE-USO.md](./11-CASOS-DE-USO.md)
