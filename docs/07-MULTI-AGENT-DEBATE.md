# 07 - Multi-Agent Debate & Consenso

## 📖 Visão Geral

**Multi-Agent Debate** usa múltiplas instâncias de IA em **papéis adversários** para debater, contra-argumentar e sintetizar respostas.

**Ganho típico**: +20 a +40% em precisão factual e redução de polarização

**Melhor para**: Ética, medicina, direito, fact-checking, redução de viés

---

## 🗣️ Arquitetura de Debate

```
┌──────────────────────────────────────────┐
│     MULTI-AGENT DEBATE LOOP              │
│                                          │
│  ROUND 1: INITIAL ARGUMENTS              │
│  ├─ Agent A: argumento favorável       │
│  ├─ Agent B: argumento contrário       │
│  └─ Moderador: resume                  │
│                                          │
│  ROUND 2: REBUTTALS                      │
│  ├─ Agent A: contra-argumento           │
│  ├─ Agent B: contra-argumento           │
│  └─ Moderador: atualiza posição         │
│                                          │
│  ROUND 3: SYNTHESIS                      │
│  ├─ Juiz: analisa ambos lados           │
│  └─ Decisão final: posição consenso     │
│                                          │
│  CHECK CONVERGENCE: Loop até consenso    │
└──────────────────────────────────────────┘
```

---

## 🧠 Pseudocódigo Multi-Agent Debate

```python
class MultiAgentDebateEngine(RecursiveThinkingEngine):
    """Debate entre múltiplos agentes"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Execute multi-agent debate
        
        Args:
            prompt: questão/tópico a debater
            config: configuração (num_agents, rounds, etc)
        
        Returns:
            RecursionResult com consenso
        """
        
        num_agents = config.extra_params.get("num_agents", 3)
        max_rounds = config.extra_params.get("max_debate_rounds", 3)
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="multi_agent_debate",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config,
            memory_pool={"debate_history": []}
        )
        
        # Criar agentes com papéis
        agents = []
        roles = [
            "PROPONENT",  # Favorável
            "OPPONENT",   # Contra
            "NEUTRAL"     # Neutro/Mediador
        ]
        
        for i in range(num_agents):
            role = roles[i % len(roles)]
            agent = DebateAgent(
                agent_id=f"agent_{i}",
                role=role,
                provider=config.provider,
                model=config.model
            )
            agents.append(agent)
        
        # Debate iterativo
        iteration = 0
        positions = {}  # Manter posição de cada agente
        
        for round_num in range(max_rounds):
            iteration += 1
            
            # ─────────────────────────────────────
            # ROUND: GENERATE ARGUMENTS
            # ─────────────────────────────────────
            
            round_arguments = {}
            
            for agent in agents:
                # Construir contexto
                context = self._build_debate_context(
                    agent,
                    positions,
                    state.memory_pool["debate_history"]
                )
                
                # Gerar argumento
                argument = agent.generate_argument(
                    prompt=prompt,
                    round_num=round_num,
                    context=context,
                    config=config
                )
                
                round_arguments[agent.agent_id] = argument
                positions[agent.agent_id] = argument
            
            # ─────────────────────────────────────
            # ROUND: EVALUATE ARGUMENTS
            # ─────────────────────────────────────
            
            for agent_id, argument in round_arguments.items():
                score = self._evaluate_argument(
                    argument,
                    prompt,
                    positions,
                    config
                )
                
                round_arguments[agent_id] = {
                    "text": argument,
                    "score": score
                }
            
            # ─────────────────────────────────────
            # ROUND: CHECK CONVERGENCE
            # ─────────────────────────────────────
            
            convergence_score = self._check_convergence(
                round_arguments,
                config
            )
            
            # ─────────────────────────────────────
            # STORE ROUND
            # ─────────────────────────────────────
            
            round_record = {
                "round_num": round_num,
                "arguments": round_arguments,
                "convergence": convergence_score,
                "timestamp": datetime.now()
            }
            
            state.memory_pool["debate_history"].append(round_record)
            
            # Parar se convergiu
            if convergence_score >= \
               config.extra_params.get("convergence_threshold", 0.85):
                break
        
        # ─────────────────────────────────────
        # SYNTHESIS: JUIZ DECIDE
        # ─────────────────────────────────────
        
        judge = JudgeAgent(
            provider=config.provider,
            model=config.model
        )
        
        consensus = judge.synthesize(
            prompt=prompt,
            debate_history=state.memory_pool["debate_history"],
            config=config
        )
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        result = RecursionResult(
            final_answer=consensus,
            iterations_count=iteration,
            improvement_percent=0,
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=[],
            metadata={
                "technique": "multi_agent_debate",
                "num_agents": num_agents,
                "num_rounds": iteration,
                "convergence_score": convergence_score,
                "debate_history": state.memory_pool["debate_history"]
            }
        )
        
        return result
    
    def _build_debate_context(
        self,
        agent: DebateAgent,
        positions: Dict[str, str],
        history: List[Dict]
    ) -> str:
        """Construir contexto com posições anteriores"""
        
        context = f"Seu papel: {agent.role}\n\n"
        
        if agent.role == "PROPONENT":
            context += "Defenda a posição FAVORÁVEL.\n"
        elif agent.role == "OPPONENT":
            context += "Defenda a posição CONTRÁRIA.\n"
        else:
            context += "Avalie ambos os lados com imparcialidade.\n"
        
        # Adicionar histórico
        if history:
            context += "\nHistórico de argumentos:\n"
            for round_rec in history[-1:]:  # Última round
                for agent_id, arg in round_rec["arguments"].items():
                    context += f"- {agent_id}: {arg['text'][:100]}...\n"
        
        return context
    
    def _evaluate_argument(
        self,
        argument: str,
        question: str,
        positions: Dict[str, str],
        config: RecursionConfig
    ) -> float:
        """Avaliar força de um argumento (0 a 1)"""
        
        eval_prompt = f"""
Avalie a força e qualidade deste argumento em escala 0-1:

Pergunta: {question}
Argumento: {argument}

Critérios:
- Lógica (coerência interna)
- Evidência (baseado em fatos)
- Persuasão (convince?)
- Refutabilidade (resiste a contraargumentos)

Score (0-1):
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é um crítico de argumentos.",
            user_prompt=eval_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            return float(response.strip())
        except:
            return 0.5
    
    def _check_convergence(
        self,
        round_arguments: Dict[str, Dict],
        config: RecursionConfig
    ) -> float:
        """Medir quanto os agentes concordam (0 a 1)"""
        
        # Extrair scores
        scores = [
            arg["score"] for arg in round_arguments.values()
        ]
        
        if not scores:
            return 0.0
        
        # Desvio padrão dos scores (quanto menor, mais consenso)
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Converter para score de convergência (0 a 1)
        # Sem variância = 1.0 (total convergência)
        convergence = max(0.0, 1.0 - std_dev)
        
        return convergence
```

---

## 🎭 Estrutura de Agentes

```python
class DebateAgent:
    """Um agente participante do debate"""
    
    agent_id: str
    role: str  # "PROPONENT", "OPPONENT", "NEUTRAL"
    provider: str
    model: str
    position_history: List[str]  # Argumentos prévios
    
    def generate_argument(
        self,
        prompt: str,
        round_num: int,
        context: str,
        config: RecursionConfig
    ) -> str:
        """Gerar argumento para esta rodada"""
        
        if round_num == 0:
            # Argumento inicial
            system = f"""
Você é um expert preparando um debate.
Seu papel: {self.role}

Gere um argumento INICIAL forte para {self.role}.
Máximo 2-3 parágrafos.
            """
            
            user = f"Pergunta: {prompt}"
        
        else:
            # Argumento com refutação
            system = f"""
Você é um debater expert.
Seu papel: {self.role}

Dado o argumento prévio do outro lado,
refute pontos fracos e reforce sua posição.
Máximo 2-3 parágrafos.
            """
            
            user = f"""
Contexto: {context}

Pergunta original: {prompt}

Seu contra-argumento:
            """
        
        response = call_model(
            provider=self.provider,
            model=self.model,
            system_prompt=system,
            user_prompt=user,
            temperature=0.8,
            max_tokens=500
        )
        
        self.position_history.append(response)
        return response

class JudgeAgent:
    """Juiz que sintetiza debate e chega a consenso"""
    
    provider: str
    model: str
    
    def synthesize(
        self,
        prompt: str,
        debate_history: List[Dict],
        config: RecursionConfig
    ) -> str:
        """Analisar debate e chegar a conclusão final"""
        
        # Formatear histórico
        history_text = ""
        for round_rec in debate_history:
            history_text += f"\n=== ROUND {round_rec['round_num']} ===\n"
            for agent_id, arg in round_rec["arguments"].items():
                history_text += f"{agent_id}: {arg['text']}\n"
        
        synthesis_prompt = f"""
Você é um juiz imparcial analisando um debate.

PERGUNTA: {prompt}

HISTÓRICO DO DEBATE:
{history_text}

TAREFA: Síntese final considerando todos argumentos.
- Identifique pontos válidos de cada lado
- Reconheça limitações
- Chegue a uma posição CONSENSO equilibrada

Resposta final (máximo 3-4 parágrafos):
        """
        
        consensus = call_model(
            provider=self.provider,
            model=self.model,
            system_prompt="Você é um juiz árbitro imparcial.",
            user_prompt=synthesis_prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        return consensus
```

---

## 📊 Configuração Multi-Agent Debate

```python
{
    "technique": "multi_agent_debate",
    "provider": "openai",
    "model": "gpt-4o",
    
    "extra_params": {
        # Debate
        "num_agents": 3,               # PROPONENT, OPPONENT, NEUTRAL
        "max_debate_rounds": 3,        # Máximo de rodadas
        "convergence_threshold": 0.85, # Parar se >85% em consenso
        
        # Personagens
        "agent_personas": {
            "PROPONENT": "Um advogado defendendo a posição favorável",
            "OPPONENT": "Um crítico rigoroso",
            "NEUTRAL": "Um mediador equilibrado"
        }
    },
    
    "max_iterations": 10,
    "max_tokens_total": 12000,
    "max_time_ms": 90000
}
```

---

## 🎯 Casos de Uso

| Caso | Melhor | Por quê |
|------|--------|---------|
| Ética médica | ✅✅✅ | Múltiplas perspectivas |
| Fact-checking | ✅✅✅ | Reduz desinformação |
| Direito | ✅✅ | Argumentos baseados em precedentes |
| Redação acadêmica | ✅✅ | Exame crítico |
| Consenso empresarial | ✅✅ | Decisão coletiva |

---

## 📈 Métricas

| Métrica | Definição |
|---------|-----------|
| **Convergence Time** | Rodadas até consenso |
| **Argument Diversity** | Quantos ângulos únicos |
| **Bias Reduction** | Redução vs resposta única |

---

## 📚 Referências

- Du et al., "Improving Factuality and Reasoning in Language Models through Multiagent Debate" (OpenAI, 2024)

**Próximo**: [08-AUTOFORMALIZAÇÃO.md](./08-AUTOFORMALIZAÇÃO.md)
