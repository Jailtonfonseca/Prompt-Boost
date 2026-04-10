# 01 - Implementação de Engines & Padrão Genérico

## 🎯 Objetivo

Este documento descreve como implementar um engine de raciocínio recursivo, com o padrão genérico que todos os 7 engines seguem.

---

## 🏗️ Padrão Genérico (GENERATE → EVALUATE → REFINE)

Todos os engines executam o mesmo loop, com variações específicas:

```
┌──────────────────────────────────┐
│ INITIALIZE                       │
│ ├─ Verificar config              │
│ ├─ Criar provider                │
│ └─ Iniciar logger                │
└─────────────┬──────────────────┘
              │
              ▼
        ┌─────────────────┐
        │ ITERATION LOOP  │ (até max_iterations ou convergência)
        │ (max: 10)       │
        ├─────────────────┤
        │ 1. GENERATE     │ Criar N candidatos (3-5)
        │    ↓            │
        │ 2. EVALUATE     │ Score cada um (0-1)
        │    ↓            │
        │ 3. FEEDBACK     │ Crítica/contexto
        │    ↓            │
        │ 4. REFINE       │ Incorporar feedback
        │    ↓            │
        │ 5. TERMINATE?   │ Parar ou continuar?
        │                 │
        │ YIELD iteration │ → Frontend (WebSocket)
        │                 │
        └─────────────────┘
              │
    ┌─────────┴─────────┐
    │ (terminou?)       │
    └─────────┬─────────┘
              │
        NO   │    SIM
            │         ▼
            │    ┌─────────────────┐
            │    │ FINALIZE        │
            │    │ ├─ Best solution│
            │    │ ├─ Metrics      │
            │    │ └─ Persist      │
            │    └────────┬────────┘
            │             │
            │             ▼
            │        ┌──────────────┐
            └───────→│ YIELD RESULT │
                     └──────────────┘
```

---

## 📝 Base Engine: Implementação Completa

### Arquivo: `backend/src/engines/base_engine.py`

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional, AsyncIterator
from pydantic import BaseModel
import time
import uuid
import logging

# ===== MODELOS DE DADOS =====

class RecursionConfig(BaseModel):
    """Configuração compartilhada por todos engines"""
    technique: str                  # 'self_refine', 'tot', etc
    provider: str                   # 'openai', 'anthropic', etc
    model: str                      # 'gpt-4o', 'claude-3', etc
    temperature: float = 0.7
    max_iterations: int = 3         # 1-10
    max_tokens_total: int = 10000   # 1000-100000
    max_time_ms: int = 120000       # 120 segundos
    extra_params: Dict = {}         # Técnica-específica

class IterationRecord(BaseModel):
    """Um passo do loop recursivo"""
    iteration_number: int
    timestamp: str                  # ISO 8601
    generated_candidates: List[str]
    evaluation_scores: List[float]  # 0-1
    selected_best: str
    feedback_from_critic: str
    tokens_this_iteration: int
    extra_data: Dict = {}

class RecursionState(BaseModel):
    """Estado durante execução"""
    execution_id: str
    technique: str
    original_prompt: str
    current_prompt: str
    iteration: int = 0
    tokens_used: int = 0
    start_time: float
    all_iterations: List[IterationRecord] = []
    best_solution: Optional[str] = None
    memory_pool: Dict = {}          # Episodic memory para algumas técnicas

class RecursionResult(BaseModel):
    """Resultado final"""
    type: str = "complete"
    execution_id: str
    final_answer: str
    iterations_count: int
    tokens_total: int
    time_total_ms: float
    quality_score: float            # 0-1 (baseline = 0.5)
    rer_score: float                # Recursion Efficiency Ratio
    all_iterations: List[IterationRecord]
    metadata: Dict

# ===== BASE ENGINE =====

class RecursiveThinkingEngine(ABC):
    """
    Base class para todos os 7 engines de raciocínio recursivo.
    Define o padrão genérico que todos seguem.
    """
    
    def __init__(
        self,
        provider,                   # LLMProvider instance
        config: RecursionConfig,
        logger: Optional[logging.Logger] = None
    ):
        self.provider = provider
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Métricas
        self.tokens_used = 0
        self.start_time = time.time()
        self.iterations_completed = 0
    
    async def run(self, original_prompt: str) -> AsyncIterator[Dict]:
        """
        Executa o engine com streaming.
        
        Yield:
            - {"type": "iteration", ...}
            - {"type": "complete", ...}
            - {"type": "error", ...}
        """
        execution_id = str(uuid.uuid4())
        state = RecursionState(
            execution_id=execution_id,
            technique=self.config.technique,
            original_prompt=original_prompt,
            current_prompt=original_prompt,
            start_time=time.time()
        )
        
        try:
            # Main loop
            while self._should_continue(state):
                # STEP 1: GENERATE
                candidates = await self._generate_candidates(
                    state.current_prompt,
                    n=self.config.extra_params.get('n_candidates', 3)
                )
                
                # STEP 2: EVALUATE
                scores = await self._evaluate_candidates(candidates)
                best_idx = max(range(len(scores)), key=lambda i: scores[i])
                best_candidate = candidates[best_idx]
                best_score = scores[best_idx]
                
                # STEP 3: FEEDBACK
                feedback = await self._generate_feedback(
                    state.original_prompt,
                    best_candidate
                )
                
                # STEP 4: REFINE
                refined_prompt = await self._refine_prompt(
                    state.current_prompt,
                    best_candidate,
                    feedback
                )
                
                # Update state
                state.iteration += 1
                state.current_prompt = refined_prompt
                state.best_solution = refined_prompt
                self.iterations_completed += 1
                
                # Create iteration record
                iteration_record = IterationRecord(
                    iteration_number=state.iteration,
                    timestamp=datetime.now().isoformat(),
                    generated_candidates=candidates,
                    evaluation_scores=scores,
                    selected_best=best_candidate,
                    feedback_from_critic=feedback,
                    tokens_this_iteration=self._estimate_tokens([
                        *candidates, feedback
                    ]),
                    extra_data={
                        'score': best_score,
                        'convergence': best_score > 0.9
                    }
                )
                
                state.all_iterations.append(iteration_record)
                
                # YIELD iteration to WebSocket
                yield {
                    'type': 'iteration',
                    'execution_id': execution_id,
                    **iteration_record.dict()
                }
                
                # STEP 5: CHECK TERMINATION
                if self._should_terminate(state):
                    break
            
            # Final result
            final_result = RecursionResult(
                execution_id=execution_id,
                final_answer=state.current_prompt,
                iterations_count=state.iteration,
                tokens_total=self.tokens_used,
                time_total_ms=(time.time() - state.start_time) * 1000,
                quality_score=self._calculate_quality_score(state),
                rer_score=self._calculate_rer(state),
                all_iterations=state.all_iterations,
                metadata={
                    'technique': self.config.technique,
                    'model': self.config.model,
                    'provider': self.config.provider
                }
            )
            
            yield final_result.dict()
            
        except Exception as e:
            self.logger.error(f"Engine error: {str(e)}", exc_info=True)
            yield {
                'type': 'error',
                'execution_id': execution_id,
                'error_code': 'ENGINE_ERROR',
                'error_message': str(e)
            }
    
    # ===== ABSTRACT METHODS (Override em subclasses) =====
    
    @abstractmethod
    async def _generate_candidates(
        self,
        prompt: str,
        n: int = 3
    ) -> List[str]:
        """
        Gera N candidatos baseado no prompt.
        Override em subclass com lógica específica.
        """
        pass
    
    @abstractmethod
    async def _evaluate_candidates(
        self,
        candidates: List[str]
    ) -> List[float]:
        """
        Avalia cada candidato retornando scores 0-1.
        Override em subclass (pode usar embedding, LLM, etc).
        """
        pass
    
    # ===== TEMPLATE METHODS (Implementado, pode override) =====
    
    async def _generate_feedback(
        self,
        original_prompt: str,
        best_candidate: str
    ) -> str:
        """Gera feedback/crítica via LLM"""
        critique_prompt = f"""Analise este prompt melhorado:

Original: {original_prompt}

Melhorado: {best_candidate}

Forneça crítica CONSTRUTIVA em 2-3 frases:
- O que melhorou?
- O que ainda falta?
- Qual é a próxima melhoria?"""
        
        feedback = await self.provider.generate(
            critique_prompt,
            temperature=0.5  # Determinístico
        )
        return feedback
    
    async def _refine_prompt(
        self,
        current_prompt: str,
        best_candidate: str,
        feedback: str
    ) -> str:
        """Refina o prompt incorporando feedback"""
        refine_system = f"""Você é um expert em engenharia de prompts.
Incorpore o feedback dado para melhorar ainda mais o prompt.
Retorne APENAS o prompt melhorado, sem explicações."""
        
        refine_user = f"""Feedback: {feedback}

Prompt atual: {best_candidate}

Prompt melhorado:"""
        
        refined = await self.provider.generate(
            refine_user,
            system=refine_system,
            temperature=0.3  # Mais conservador
        )
        
        return refined
    
    def _should_continue(self, state: RecursionState) -> bool:
        """Verifica se deve continuar iterando"""
        # Critério 1: Atingiu max iterações?
        if state.iteration >= self.config.max_iterations:
            return False
        
        # Critério 2: Atingiu max tokens?
        if self.tokens_used >= self.config.max_tokens_total:
            return False
        
        # Critério 3: Atingiu max tempo?
        elapsed_ms = (time.time() - state.start_time) * 1000
        if elapsed_ms >= self.config.max_time_ms:
            return False
        
        return True
    
    def _should_terminate(self, state: RecursionState) -> bool:
        """Verifica se deve terminar (convergência, etc)"""
        # Se tem feedback muito positivo, pode terminar mais cedo
        if len(state.all_iterations) > 1:
            last_iteration = state.all_iterations[-1]
            best_score = max(last_iteration.evaluation_scores)
            
            if best_score > 0.95:  # Muito bom!
                self.logger.info(f"Early termination: high quality score {best_score}")
                return True
        
        return False
    
    def _estimate_tokens(self, texts: List[str]) -> int:
        """Estima tokens (4 chars ≈ 1 token)"""
        total_chars = sum(len(t) for t in texts)
        return max(10, total_chars // 4)  # Mínimo 10
    
    def _calculate_quality_score(self, state: RecursionState) -> float:
        """
        Calcula qualidade do resultado final.
        Baseado em:
        - Score da última iteração
        - Convergência (melhora consistente)
        - Número de iterações (mais = melhor exploração)
        """
        if not state.all_iterations:
            return 0.5
        
        last_scores = state.all_iterations[-1].evaluation_scores
        best_score = max(last_scores)
        
        # Bônus por convergência
        convergence_bonus = 0.0
        if len(state.all_iterations) >= 2:
            prev_score = max(state.all_iterations[-2].evaluation_scores)
            if best_score > prev_score:
                convergence_bonus = 0.05 * min(1.0, best_score - prev_score)
        
        return min(1.0, best_score + convergence_bonus)
    
    def _calculate_rer(self, state: RecursionState) -> float:
        """
        RER = Recursion Efficiency Ratio
        RER = (Quality Improvement %) / (Tokens Adicionais / 1000)
        
        Mede eficiência: quanto de melhoria por token gasto
        """
        if self.tokens_used == 0:
            return 0.0
        
        quality = self._calculate_quality_score(state)
        baseline_quality = 0.5  # Qualidade esperada sem recursão
        improvement = quality - baseline_quality
        
        tokens_per_1k = self.tokens_used / 1000.0
        
        if tokens_per_1k == 0:
            return 0.0
        
        rer = (improvement * 100) / tokens_per_1k
        return max(0.0, rer)
    
    def __str__(self):
        return f"{self.__class__.__name__}(model={self.config.model})"
```

---

## 🔧 Exemplos: Diferentes Implementações

### Exemplo 1: Self-Refine (Simples)

```python
class SelfRefineEngine(RecursiveThinkingEngine):
    """Self-refine: melhoria iterativa via crítica interna"""
    
    async def _generate_candidates(self, prompt: str, n: int = 3) -> List[str]:
        """Gera n variações do prompt"""
        candidates = []
        for i in range(n):
            candidate = await self.provider.generate(
                f"Melhore este prompt (versão {i+1}):\n{prompt}",
                temperature=0.7
            )
            candidates.append(candidate)
        return candidates
    
    async def _evaluate_candidates(self, candidates: List[str]) -> List[float]:
        """Avalia by length + specificity heuristic"""
        scores = []
        for candidate in candidates:
            # Heurística: prompts mais longos e específicos são melhores
            length_score = min(1.0, len(candidate) / 500)  # Esperado 500 chars
            specificity_score = sum(1 for word in ['exemplo', 'específico', 'exatamente']
                                   if word in candidate.lower()) * 0.1
            score = min(1.0, 0.7 * length_score + 0.3 * specificity_score)
            scores.append(score)
        return scores
```

### Exemplo 2: Tree of Thoughts (Avançado)

```python
class TreeOfThoughtsEngine(RecursiveThinkingEngine):
    """ToT: exploração em árvore com pruning"""
    
    async def _generate_candidates(self, prompt: str, n: int = 3) -> List[str]:
        """Gera n pensamentos (caminho na árvore)"""
        candidates = []
        for i in range(n):
            thought = await self.provider.generate(
                f"Pense sobre como melhorar:\n{prompt}\nPensamento {i+1}:",
                temperature=0.7
            )
            candidates.append(thought)
        return candidates
    
    async def _evaluate_candidates(self, candidates: List[str]) -> List[float]:
        """Avalia by logical structure (via LLM)"""
        scores = []
        for candidate in candidates:
            eval_prompt = f"Rate this thought (0-1): {candidate}"
            eval_response = await self.provider.generate(eval_prompt, temperature=0.3)
            try:
                score = float(eval_response.strip().split()[0])
                score = min(1.0, max(0.0, score))
            except:
                score = 0.5
            scores.append(score)
        return scores
    
    async def _refine_prompt(self, current_prompt, best_candidate, feedback):
        """Refina expandindo melhor branch"""
        refined = await self.provider.generate(
            f"Expand on this thought:\n{best_candidate}\nFeedback: {feedback}",
            temperature=0.3
        )
        return refined
```

---

## 📊 Fluxo de Token Accounting

```
Iteração 1:
├─ GENERATE (3 candidates):        500 tokens
├─ EVALUATE (scoring):             200 tokens
├─ FEEDBACK (critique):            350 tokens
└─ REFINE:                         400 tokens
   Total Iteração 1:             1,450 tokens

Iteração 2:
├─ GENERATE:                       500 tokens
├─ EVALUATE:                       200 tokens
├─ FEEDBACK:                       350 tokens
└─ REFINE:                         400 tokens
   Total Iteração 2:             1,450 tokens

Iteração 3:
├─ GENERATE:                       500 tokens
├─ EVALUATE:                       200 tokens
├─ FEEDBACK:                       350 tokens
└─ REFINE:                         400 tokens
   Total Iteração 3:             1,450 tokens

─────────────────────────────────────
TOTAL:                           4,350 tokens
```

---

## 🧪 Testando um Engine

```python
# tests/unit/test_engines.py

@pytest.mark.asyncio
async def test_self_refine_engine():
    # Setup
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock(return_value="improved prompt")
    
    config = RecursionConfig(
        technique="self_refine",
        provider="openai",
        model="gpt-4o",
        max_iterations=2
    )
    
    engine = SelfRefineEngine(mock_provider, config)
    
    # Run
    results = []
    async for result in engine.run("original prompt"):
        results.append(result)
    
    # Assert
    assert len(results) == 3  # 2 iterations + 1 complete
    assert results[-1]['type'] == 'complete'
    assert results[-1]['iterations_count'] == 2
```

---

## 🎯 Checklist de Implementação

- [ ] Criar `backend/src/engines/base_engine.py` com RecursiveThinkingEngine
- [ ] Implementar RecursionState, IterationRecord, RecursionResult
- [ ] Implementar 7 subclasses de engine
- [ ] Testes unitários para cada engine
- [ ] Integração com providers
- [ ] WebSocket streaming
- [ ] Database persistence

---

**Referências Cruzadas**:
- Arquitetura: `/backend/docs/00-ARQUITETURA-BACKEND.md`
- Self-Refine: `/backend/docs/02-SELF-REFINE-ENGINE.md`
- ToT: `/backend/docs/03-TOT-GOT-ENGINES.md`

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
