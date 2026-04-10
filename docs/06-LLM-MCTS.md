# 06 - LLM-MCTS (Planejamento com Monte Carlo Tree Search)

## 📖 Visão Geral

**LLM-MCTS** combina **Monte Carlo Tree Search** com LLM. O MCTS estrutura a busca enquanto o LLM fornece heurísticas (valor + simulação).

**Ganho típico**: +18 a +35% em tarefas de planejamento de longo prazo

**Melhor para**: Planejamento, decisão sequencial, robótica, webshop

---

## 🌳 MCTS: Os 4 Passos

```
┌─────────────────────────────────────────────┐
│       MCTS CYCLE (Simulação Única)          │
│                                             │
│  1. SELECTION                              │
│     └─ Descender na árvore usando UCB1     │
│        até folha não-visitada              │
│                                             │
│  2. EXPANSION                              │
│     └─ Gerar filhos usando LLM             │
│                                             │
│  3. SIMULATION (Rollout)                   │
│     └─ LLM simula até terminal state       │
│                                             │
│  4. BACKPROPAGATION                        │
│     └─ Atualizar reward de todos nós       │
│        no caminho de volta                 │
│                                             │
│  Loop: Repetir 100-1000x                   │
└─────────────────────────────────────────────┘

Após simulações:
└─ Selecionar ação com melhor valor médio
```

---

## 🧠 Pseudocódigo LLM-MCTS

```python
class LLMMCTSEngine(RecursiveThinkingEngine):
    """LLM-based Monte Carlo Tree Search"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Execute LLM-MCTS sobre um problema de planejamento
        
        Args:
            prompt: objetivo/tarefa
            config: hiperparâmetros (C, simulations, etc)
        
        Returns:
            RecursionResult com melhor plano/ação
        """
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="llm_mcts",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config,
            memory_pool={"mcts_tree": None}
        )
        
        # Inicializar árvore MCTS
        root = MCTSNode(
            state_repr=prompt,  # Representação do estado
            parent=None,
            action_leading_here="",
            visits=0,
            value_sum=0.0,
            children={}
        )
        
        state.memory_pool["mcts_tree"] = root
        
        num_simulations = config.extra_params.get("num_simulations", 100)
        ucb_constant = config.extra_params.get("ucb_constant", 1.414)
        
        # ─────────────────────────────────────
        # MAIN MCTS LOOP
        # ─────────────────────────────────────
        
        for sim in range(num_simulations):
            
            # 1. SELECTION & EXPANSION
            node = self._select_and_expand(root, config)
            
            # 2. SIMULATION (Rollout)
            rollout_reward = self._simulate(node, config)
            
            # 3. BACKPROPAGATION
            self._backprop(node, rollout_reward)
            
            if (sim + 1) % 20 == 0:
                print(f"MCTS Sim {sim+1}/{num_simulations}")
        
        # ─────────────────────────────────────
        # BEST ACTION SELECTION
        # ─────────────────────────────────────
        
        best_action = self._select_best_action(root)
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        result = RecursionResult(
            final_answer=best_action,
            iterations_count=num_simulations,
            improvement_percent=0,
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=[],
            metadata={
                "technique": "llm_mcts",
                "num_simulations": num_simulations,
                "tree_depth": self._get_tree_depth(root),
                "tree_width": self._get_tree_width(root),
            }
        )
        
        return result
    
    def _select_and_expand(
        self,
        root: MCTSNode,
        config: RecursionConfig
    ) -> MCTSNode:
        """Descender na árvore ou expandir"""
        
        node = root
        ucb_const = config.extra_params.get("ucb_constant", 1.414)
        
        # Descender até folha
        while node.children:
            # Calcular UCB1 para cada filho
            best_child = None
            best_ucb = -float('inf')
            
            for child in node.children.values():
                avg_value = child.value_sum / (child.visits + 1e-6)
                exploitation = avg_value
                
                exploration = ucb_const * math.sqrt(
                    math.log(node.visits) / (child.visits + 1)
                )
                
                ucb = exploitation + exploration
                
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            
            node = best_child
        
        # Expandir este nó (gerar filhos)
        if node.visits > 0:  # Só expandir após visitar
            self._expand_node(node, config)
            
            # Se tem filhos, voltar o primeiro
            if node.children:
                return list(node.children.values())[0]
        
        return node
    
    def _expand_node(
        self,
        node: MCTSNode,
        config: RecursionConfig
    ):
        """Usar LLM para gerar ações possíveis (filhos)"""
        
        action_prompt = f"""
Estado atual: {node.state_repr}

Objetivo original: {config.extra_params.get('objective', '')}

Gere 3-5 ações possíveis que avançam em direção ao objetivo.

Formato:
1. [Ação]: [Descrição]
2. [Ação]: [Descrição]
...
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é um planejador estratégico.",
            user_prompt=action_prompt,
            temperature=0.8,
            max_tokens=500
        )
        
        # Parse ações
        actions = self._parse_actions(response)
        
        for action in actions:
            child = MCTSNode(
                state_repr=f"{node.state_repr} → {action}",
                parent=node,
                action_leading_here=action,
                visits=0,
                value_sum=0.0,
                children={}
            )
            node.children[action] = child
    
    def _simulate(
        self,
        node: MCTSNode,
        config: RecursionConfig
    ) -> float:
        """Rollout: LLM simula até terminal state"""
        
        current_state = node.state_repr
        max_steps = config.extra_params.get("max_rollout_steps", 5)
        
        for step in range(max_steps):
            # LLM pensa um passo adiante
            rollout_prompt = f"""
Estado: {current_state}
Objetivo: {config.extra_params.get('objective', '')}

Próximo passo? (máximo 1 parágrafo)
            """
            
            response = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt="Você é um executor eficiente.",
                user_prompt=rollout_prompt,
                temperature=0.7,
                max_tokens=200
            )
            
            current_state += f" → {response}"
            
            # Checar se atingiu objetivo
            is_terminal = self._is_terminal(current_state, config)
            if is_terminal:
                break
        
        # Avaliar quão bem chegou ao objetivo
        reward = self._evaluate_terminal_state(
            current_state,
            config
        )
        
        return reward
    
    def _backprop(
        self,
        node: MCTSNode,
        reward: float
    ):
        """Atualizar valor de todos nós no caminho"""
        
        current = node
        while current is not None:
            current.visits += 1
            current.value_sum += reward
            current = current.parent
    
    def _select_best_action(
        self,
        root: MCTSNode
    ) -> str:
        """Escolher ação com melhor valor médio"""
        
        best_action = None
        best_value = -float('inf')
        
        for action, child in root.children.items():
            avg_value = child.value_sum / (child.visits + 1)
            
            if avg_value > best_value:
                best_value = avg_value
                best_action = action
        
        return best_action if best_action else "Sem ação disponível"
    
    def _is_terminal(
        self,
        state_repr: str,
        config: RecursionConfig
    ) -> bool:
        """Verificar se chegou ao estado terminal"""
        
        check_prompt = f"""
Estado: {state_repr}
Objetivo: {config.extra_params.get('objective', '')}

Atingiu o objetivo? Responda SIM ou NÃO.
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Verificador.",
            user_prompt=check_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        return "SIM" in response.upper()
    
    def _evaluate_terminal_state(
        self,
        state_repr: str,
        config: RecursionConfig
    ) -> float:
        """Avaliar quão bem executou (0 a 1)"""
        
        eval_prompt = f"""
Estado final: {state_repr}
Objetivo: {config.extra_params.get('objective', '')}

Qual o score de sucesso (0-1)?
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Avaliador.",
            user_prompt=eval_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            return float(response.strip())
        except:
            return 0.5
```

---

## 📊 Estrutura de Nó MCTS

```python
class MCTSNode:
    """Um nó na árvore de busca MCTS"""
    
    # Estado
    state_repr: str                     # Representação do estado
    action_leading_here: str            # Ação que levou aqui
    
    # Estrutura
    parent: Optional[MCTSNode]          # Nó pai
    children: Dict[str, MCTSNode]       # Filhos por ação
    
    # Estatísticas MCTS
    visits: int                         # N(s,a)
    value_sum: float                    # W(s,a) - soma de rewards
    
    @property
    def average_value(self) -> float:
        """Q(s,a) / N(s,a)"""
        return self.value_sum / (self.visits + 1e-6)
```

---

## 📈 Configuração LLM-MCTS

```python
{
    "technique": "llm_mcts",
    "provider": "openai",
    "model": "gpt-4o",
    
    "extra_params": {
        # Planejamento
        "objective": "Navegar até a cozinha e pegar café",
        "max_rollout_steps": 5,
        
        # MCTS
        "num_simulations": 100,         # Simulações por decisão
        "ucb_constant": 1.414,          # Exploração vs Exploração
        "max_tree_depth": 10,
    },
    
    "max_iterations": 100,  # Simulações
    "max_tokens_total": 15000,
    "max_time_ms": 120000
}
```

---

## 📚 Referências

- AlphaGo (MonteCarlo Tree Search + Neural Networks)

**Próximo**: [07-MULTI-AGENT-DEBATE.md](./07-MULTI-AGENT-DEBATE.md)
