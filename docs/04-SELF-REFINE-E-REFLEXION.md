# 04 - Self-Refine & Reflexion

## 📖 Visão Geral

**Self-Refine** e **Reflexion** são técnicas de feedback iterativo:

- **Self-Refine**: Loop explícito `gerar → criticar → refinar → repetir`
- **Reflexion**: Como Self-Refine, mas com **memória episódica persistente** que aprende entre sessões

**Ganho típico**: 
- Self-Refine: +15 a +30% em precisão após 2-3 ciclos
- Reflexion: 2-4x mais rápido em tarefas repetidas

---

## 🔄 Self-Refine: O Loop Clássico

### Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    SELF-REFINE LOOP                     │
│                                                          │
│  INPUT: prompt original                                │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────────────────────────┐               │
│  │ ITERATION 0: GENERATE               │               │
│  │ ─────────────────────────────────   │               │
│  │ prompt_0 = model.generate(          │               │
│  │     system_prompt,                  │               │
│  │     original_prompt                 │               │
│  │ )                                   │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ GENERATION 0                         │               │
│  │ "Um assistente de IA que ajuda       │               │
│  │  usuarios a escrever melhor..."      │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ CRITICIZE GENERATION 0              │               │
│  │ ─────────────────────────────────   │               │
│  │ critique_0 = critic.generate(       │               │
│  │     system="Você é crítico",        │               │
│  │     user="Analise este prompt:      │               │
│  │           {prompt_0}                │               │
│  │           Que melhorias?"           │               │
│  │ )                                   │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ CRITICISM 0                          │               │
│  │ "Pontos fracos:                     │               │
│  │  1. Vago ('melhor' não é claro)     │               │
│  │  2. Sem exemplos de uso              │               │
│  │  3. Sem constrangimentos             │               │
│  │ Melhorias: ser específico..."        │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ REFINE BASED ON CRITICISM           │               │
│  │ ─────────────────────────────────   │               │
│  │ prompt_1 = model.generate(          │               │
│  │     system="Melhore o prompt",      │               │
│  │     user="Prompt original:          │               │
│  │            {prompt_0}               │               │
│  │            Feedback: {critique_0}   │               │
│  │            Crie versão melhorada"   │               │
│  │ )                                   │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ REFINED GENERATION 1                 │               │
│  │ "Um assistente de IA especializado   │               │
│  │  que ajuda usuários a escrever       │               │
│  │  prompts efetivos. Exemplos:         │               │
│  │  1. Escrever artigos técnicos        │               │
│  │  2. Descrever tarefas de código      │               │
│  │  3. Briefings executivos             │               │
│  │  Constrangimentos: ..."              │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ CHECK TERMINATION:                  │               │
│  │   ├─ Iterações >= max? → END        │               │
│  │   ├─ Convergência? → END            │               │
│  │   ├─ Qualidade >= threshold? → END  │               │
│  │   └─ SENÃO: volta criticar prompt_1 │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               └─→ Próxima iteração...                  │
│                                                          │
│  OUTPUT: prompt_final (mais refinado)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Self-Refine: Pseudocódigo

```python
class SelfRefineEngine(RecursiveThinkingEngine):
    """Self-Refine: Feedback-based iterative refinement"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Execute Self-Refine loop
        
        Args:
            prompt: prompt/solução a refinar
            config: configuração (provider, crítico, etc)
        
        Returns:
            RecursionResult com prompt refinado
        """
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="self_refine",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config
        )
        
        iteration = 0
        
        while not self._should_terminate(state, config):
            iteration += 1
            
            # ─────────────────────────────────────
            # STAGE 1: GENERATE
            # ─────────────────────────────────────
            
            system_prompt = config.extra_params.get(
                "generation_system_prompt",
                self._default_generation_system_prompt()
            )
            
            generated = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt=system_prompt,
                user_prompt=state.current_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens_per_iteration
            )
            
            # ─────────────────────────────────────
            # STAGE 2: EVALUATE (com critério de qualidade)
            # ─────────────────────────────────────
            
            quality_score = self._evaluate_quality(
                generated,
                state,
                config
            )
            
            # ─────────────────────────────────────
            # STAGE 3: CRITICIZE
            # ─────────────────────────────────────
            
            critique_provider = config.extra_params.get(
                "critique_provider",
                config.provider  # Usar mesmo provider se não especificado
            )
            
            critique_model = config.extra_params.get(
                "critique_model",
                config.model
            )
            
            critique_system_prompt = """
Você é um crítico expert que fornece feedback estruturado.

Para cada resposta, identifique:
1. PONTOS FORTES: 2-3 aspectos bem executados
2. ÁREAS DE MELHORA: 2-3 pontos críticos a melhorar
3. SUGESTÕES: 2-3 recomendações específicas

Seja conciso e direto. Formato:
PONTOS FORTES:
- [ponto 1]
- [ponto 2]

ÁREAS DE MELHORA:
- [área 1]
- [área 2]

SUGESTÕES:
- [sugestão 1]
- [sugestão 2]
            """
            
            criticism = call_model(
                provider=critique_provider,
                model=critique_model,
                system_prompt=critique_system_prompt,
                user_prompt=f"""
Analise este prompt/solução:

{generated}

Contexto original:
{state.original_prompt}
                """,
                temperature=0.7,
                max_tokens=500
            )
            
            # ─────────────────────────────────────
            # STAGE 4: REFINE
            # ─────────────────────────────────────
            
            refine_system_prompt = """
Você é um especialista em refinamento. Dada uma solução e crítica,
melhore a solução incorporando o feedback.

Mantenha:
- Essência original
- Qualidades identificadas
- Estrutura geral

Melhore:
- Áreas de fragilidade
- Clareza e concisão
- Completude
            """
            
            refined = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt=refine_system_prompt,
                user_prompt=f"""
Solução atual:
{generated}

Feedback para melhoria:
{criticism}

Crie versão melhorada que incorpora o feedback.
                """,
                temperature=config.temperature,
                max_tokens=config.max_tokens_per_iteration
            )
            
            # ─────────────────────────────────────
            # STORE ITERATION
            # ─────────────────────────────────────
            
            iteration_record = IterationRecord(
                iteration_number=iteration,
                timestamp=datetime.now(),
                generated_candidates=[generated, refined],
                evaluation_scores=[quality_score, 0.0],  # Será atualizado
                selected_best=refined,
                feedback_from_critic=criticism,
                refined_prompt=refined,
                tokens_this_iteration=count_tokens(
                    generated + criticism + refined
                ),
                duration_ms=0,
                extra_data={
                    "quality_score": quality_score,
                    "critique_provider": critique_provider,
                }
            )
            
            state.all_iterations.append(iteration_record)
            state.current_prompt = refined
            state.iteration = iteration
            
            # ─────────────────────────────────────
            # CHECK TERMINATION
            # ─────────────────────────────────────
            
            # Atualizar melhor solução
            if quality_score > (state.best_solution.quality_score if state.best_solution else 0):
                state.best_solution = Solution(
                    text=refined,
                    quality_score=quality_score,
                    iteration=iteration
                )
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        result = RecursionResult(
            final_answer=state.best_solution.text,
            iterations_count=iteration,
            improvement_percent=self._calculate_improvement(state),
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=state.all_iterations,
            metadata={
                "technique": "self_refine",
                "best_quality_score": state.best_solution.quality_score,
                "convergence_iteration": iteration,
            }
        )
        
        return result
    
    def _evaluate_quality(
        self,
        candidate: str,
        state: RecursionState,
        config: RecursionConfig
    ) -> float:
        """Avaliar qualidade (0 a 1)"""
        
        eval_prompt = f"""
Avalie a qualidade desta resposta para "{state.original_prompt}"
em uma escala de 0 a 1:

Resposta: {candidate}

Critérios:
- Clareza (0-1)
- Completude (0-1)
- Precisão (0-1)
- Utilidade (0-1)

Retorne apenas um número de 0 a 1 (média dos critérios).
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é um avaliador de qualidade.",
            user_prompt=eval_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def _should_terminate(
        self,
        state: RecursionState,
        config: RecursionConfig
    ) -> bool:
        """Critérios de parada para Self-Refine"""
        
        # Limite de iterações
        if state.iteration >= config.max_iterations:
            return True
        
        # Convergência (melhora < threshold)
        if state.iteration > 1:
            recent_scores = [
                it.extra_data.get("quality_score", 0)
                for it in state.all_iterations[-2:]
            ]
            
            if len(recent_scores) == 2:
                improvement = (recent_scores[-1] - recent_scores[-2]) / \
                              (recent_scores[-2] + 1e-6)
                
                if improvement < config.extra_params.get(
                    "min_improvement_threshold", 0.01
                ):
                    state.iterations_no_improvement = \
                        state.iterations_no_improvement + 1
                    
                    if state.iterations_no_improvement >= \
                       config.extra_params.get("max_no_improvement", 2):
                        return True
        
        # Limite de tokens
        if state.tokens_used >= config.max_tokens_total:
            return True
        
        return False
```

---

## 🧠 Reflexion: Com Memória Episódica

**Reflexion** estende Self-Refine adicionando **memória episódica persistente**:

```python
class ReflexionEngine(SelfRefineEngine):
    """Reflexion: Self-Refine com memória episódica"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig,
        memory_pool: Optional[MemoryPool] = None
    ) -> RecursionResult:
        """
        Execute Reflexion loop com memória
        
        Args:
            prompt: tarefa a executar
            config: configuração
            memory_pool: experiências anteriores (opcional)
        
        Returns:
            RecursionResult com resposta + lições aprendidas
        """
        
        # Inicializar ou reusar memory pool
        if memory_pool is None:
            memory_pool = MemoryPool()
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="reflexion",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config,
            memory_pool={
                "episodes": memory_pool.episodes,
                "lessons": memory_pool.lessons
            }
        )
        
        # ─────────────────────────────────────
        # RETRIEVE RELEVANT EXPERIENCES
        # ─────────────────────────────────────
        
        relevant_episodes = memory_pool.retrieve_similar(
            prompt,
            top_k=config.extra_params.get("memory_top_k", 3)
        )
        
        # Construir contexto de memória
        memory_context = self._build_memory_context(
            relevant_episodes,
            memory_pool.lessons
        )
        
        iteration = 0
        
        while not self._should_terminate(state, config):
            iteration += 1
            
            # ─────────────────────────────────────
            # STAGE 1: GENERATE (com contexto de memória)
            # ─────────────────────────────────────
            
            system_prompt = f"""
Você é um assistente que aprende com experiências.

LIÇÕES APRENDIDAS ANTERIORMENTE:
{memory_context}

Agora, execute a tarefa abaixo utilizando essas lições.
            """
            
            generated = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt=system_prompt,
                user_prompt=state.current_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens_per_iteration
            )
            
            # ─────────────────────────────────────
            # STAGE 2: EVALUATE
            # ─────────────────────────────────────
            
            quality_score = self._evaluate_quality(
                generated,
                state,
                config
            )
            
            # ─────────────────────────────────────
            # STAGE 3: CRITICIZE
            # ─────────────────────────────────────
            
            criticism = self._get_criticism(
                generated,
                state,
                config
            )
            
            # ─────────────────────────────────────
            # STAGE 4: LEARN LESSON
            # (diferente de Self-Refine!)
            # ─────────────────────────────────────
            
            lesson = self._extract_lesson(
                prompt,
                generated,
                criticism,
                quality_score,
                config
            )
            
            # ─────────────────────────────────────
            # STAGE 5: REFINE
            # ─────────────────────────────────────
            
            refined = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt="Melhore a resposta incorporando o feedback.",
                user_prompt=f"""
Resposta atual: {generated}
Crítica: {criticism}
Lição a aplicar: {lesson}

Versão melhorada:
                """,
                temperature=config.temperature,
                max_tokens=config.max_tokens_per_iteration
            )
            
            # ─────────────────────────────────────
            # STORE IN MEMORY
            # (diferente de Self-Refine!)
            # ─────────────────────────────────────
            
            episode = Episode(
                task=prompt,
                attempts=[generated, refined],
                lesson=lesson,
                quality_score=quality_score,
                timestamp=datetime.now(),
                metadata={"provider": config.provider, "model": config.model}
            )
            
            memory_pool.add_episode(episode)
            
            # ─────────────────────────────────────
            # STORE ITERATION
            # ─────────────────────────────────────
            
            iteration_record = IterationRecord(
                iteration_number=iteration,
                timestamp=datetime.now(),
                generated_candidates=[generated, refined],
                evaluation_scores=[quality_score, 0.0],
                selected_best=refined,
                feedback_from_critic=criticism,
                refined_prompt=refined,
                tokens_this_iteration=count_tokens(
                    generated + criticism + refined
                ),
                duration_ms=0,
                extra_data={
                    "quality_score": quality_score,
                    "lesson": lesson,
                    "memory_hits": len(relevant_episodes),
                }
            )
            
            state.all_iterations.append(iteration_record)
            state.current_prompt = refined
            state.iteration = iteration
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        result = RecursionResult(
            final_answer=state.best_solution.text if state.best_solution else refined,
            iterations_count=iteration,
            improvement_percent=self._calculate_improvement(state),
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=state.all_iterations,
            metadata={
                "technique": "reflexion",
                "lessons_learned": [
                    it.extra_data.get("lesson")
                    for it in state.all_iterations
                ],
                "memory_pool_size": len(memory_pool.episodes),
            }
        )
        
        return result
    
    def _extract_lesson(
        self,
        task: str,
        response: str,
        criticism: str,
        quality: float,
        config: RecursionConfig
    ) -> str:
        """Extrair lição reutilizável da experiência"""
        
        lesson_prompt = f"""
Baseado na tarefa, resposta e crítica abaixo,
extraia uma LIÇÃO APRENDIDA que pode ser aplicada
a tarefas similares no futuro.

Formato: "[Contexto] → [Ação] → [Resultado positivo]"

Tarefa: {task}
Resposta: {response}
Crítica: {criticism}
Qualidade: {quality}

Lição (máximo 1 parágrafo):
        """
        
        lesson = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você extrai insights de experiências.",
            user_prompt=lesson_prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        return lesson.strip()
    
    def _build_memory_context(
        self,
        episodes: List[Episode],
        lessons: List[str]
    ) -> str:
        """Construir contexto a partir de memória"""
        
        context = ""
        
        for i, lesson in enumerate(lessons[:5]):  # Top 5
            context += f"{i+1}. {lesson}\n"
        
        return context if context else "Nenhuma lição anterior."
```

### Estrutura de Memória Episódica

```python
class MemoryPool:
    """Armazena e recupera episódios de experiência"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.episodes: List[Episode] = []
        self.lessons: List[str] = []
        self.storage_path = storage_path or "./reflexion_memory.json"
        self.load_from_disk()
    
    def add_episode(self, episode: Episode):
        """Adicionar novo episódio à memória"""
        self.episodes.append(episode)
        self.lessons.append(episode.lesson)
        self.save_to_disk()
    
    def retrieve_similar(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Episode]:
        """Recuperar episódios similares via embedding similarity"""
        
        # Usar embedding para similaridade
        query_embedding = embed(query)
        
        scores = []
        for episode in self.episodes:
            episode_embedding = embed(episode.task)
            similarity = cosine_similarity(
                query_embedding,
                episode_embedding
            )
            scores.append((episode, similarity))
        
        # Retornar Top-K
        scores.sort(key=lambda x: x[1], reverse=True)
        return [episode for episode, _ in scores[:top_k]]
    
    def save_to_disk(self):
        """Persistir memória em JSON"""
        data = {
            "episodes": [ep.to_dict() for ep in self.episodes],
            "lessons": self.lessons
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_from_disk(self):
        """Carregar memória de JSON"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.episodes = [
                    Episode.from_dict(ep) for ep in data.get("episodes", [])
                ]
                self.lessons = data.get("lessons", [])

class Episode:
    """Uma experiência completa (tarefa, tentativas, lição)"""
    
    task: str                          # Tarefa realizada
    attempts: List[str]                # Diferentes tentativas
    lesson: str                        # Lição aprendida
    quality_score: float               # Qualidade final [0, 1]
    timestamp: datetime                # Quando ocorreu
    metadata: Dict[str, any]           # Extras (provider, model, etc)
```

---

## 📊 Configuração Self-Refine & Reflexion

```python
# Self-Refine Config
{
    "technique": "self_refine",
    "provider": "openai",
    "model": "gpt-4o",
    
    "extra_params": {
        # Provedor de crítica (pode ser diferente!)
        "critique_provider": "openai",
        "critique_model": "gpt-4o",
        
        # Sistema prompts customizados
        "generation_system_prompt": "Você é um especialista...",
        "critique_system_prompt": "Você é um crítico...",
        
        # Terminação
        "min_improvement_threshold": 0.01,
        "max_no_improvement": 2,
    },
    
    "max_iterations": 4,
    "max_tokens_total": 8000,
    "max_time_ms": 60000
}

# Reflexion Config
{
    "technique": "reflexion",
    "provider": "openai",
    "model": "gpt-4o",
    
    "extra_params": {
        "critique_provider": "openai",
        "critique_model": "gpt-4o",
        
        # Memória
        "memory_top_k": 3,
        "memory_storage_path": "./memories/reflexion.json",
        
        # Terminação
        "min_improvement_threshold": 0.01,
        "max_no_improvement": 2,
    },
    
    "max_iterations": 3,
    "max_tokens_total": 7000,
    "max_time_ms": 50000
}
```

---

## 🎯 Quando Usar Self-Refine vs Reflexion

| Situação | Self-Refine | Reflexion |
|----------|---|---|
| Uma tarefa única | ✅✅✅ | ✅ |
| Muitas tarefas similares | ✅ | ✅✅✅ |
| Sem histórico | ✅✅✅ | ❌ |
| Com histórico | ✅ | ✅✅✅ |
| Codificação | ✅✅✅ | ✅✅ |
| Escrita | ✅✅ | ✅✅✅ |
| Agentes autoaprendizes | ❌ | ✅✅✅ |

---

## 📈 Métricas de Avaliação

| Métrica | Self-Refine | Reflexion |
|---------|---|---|
| **Melhoria por iteração** | +5-10% | +3-8% (depois crescente) |
| **Convergência** | 2-3 iterações | 1-2 iterações (com memória) |
| **Taxa de falsos positivos** | ~20% | <5% (com memória boa) |
| **Token efficiency** | Moderada | Excelente (reutiliza contexto) |
| **Escalabilidade** | Linear | Super-linear com memória |

---

## 🚀 Exemplo: De Self-Refine a Reflexion

```
Iteração 1 (Self-Refine):
  Prompt: "Escreva um bom prompt para..."
  Crítica: "Muito vago, adicione exemplos"
  Melhoria: +12%

Iteração 2 (Self-Refine):
  Prompt: "...com exemplos"
  Crítica: "Falta contexto"
  Melhoria: +8%

Iteração 3 (Self-Refine):
  Prompt: "...com contexto"
  Crítica: "Perfeito!"
  Melhoria: +3%

Salvar Lições → Memory Pool

Próxima Sessão (Reflexion):
  Recuperar: "Escreva prompts → sempre adicione exemplos e contexto"
  Geração já leva em conta → Converge em 1-2 iterações!
```

---

## 📚 Referências

- Madaan et al., "Self-Refine: Iterative Refinement with Self-Feedback" (ICLR 2023)
- Shinn et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (ICLR 2024)

**Próximo**: [05-RECURSIVE-ALIGNMENT.md](./05-RECURSIVE-ALIGNMENT.md)
