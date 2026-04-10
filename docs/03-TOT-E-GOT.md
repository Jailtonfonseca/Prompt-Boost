# 03 - Tree of Thoughts (ToT) & Graph of Thoughts (GoT)

## 🌳 Visão Geral

**Tree of Thoughts (ToT)** e **Graph of Thoughts (GoT)** são técnicas que exploram deliberadamente múltiplos caminhos de raciocínio, avaliando, podando e expandindo ramos de forma estruturada.

### Diferença Rápida
- **ToT**: Estrutura em árvore (cada nó tem um pai)
- **GoT**: Estrutura em grafo (nós podem ter múltiplos pais/filhos)

**Ganho típico**: +12 a +24 pontos percentuais em raciocínio lógico vs baseline (CoT)

---

## 🔄 Mecanismo de ToT

### Estágios do Loop

```
┌─────────────────────────────────────────────────────────┐
│                  TREE OF THOUGHTS LOOP                  │
│                                                          │
│  START: prompt original (root)                          │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────────────────────────┐               │
│  │ STAGE 1: GENERATE THOUGHTS          │               │
│  │ ─────────────────────────────────   │               │
│  │ Para cada nó expandível na árvore:  │               │
│  │   ├─ Gerar K variações              │               │
│  │   ├─ Cada uma é novo nó na árvore   │               │
│  │   └─ Adicionar à fila de expansão   │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ STAGE 2: EVALUATE THOUGHTS          │               │
│  │ ─────────────────────────────────   │               │
│  │ Para cada novo nó:                  │               │
│  │   ├─ Score: [0, 1]                  │               │
│  │   ├─ Heurística: promise score      │               │
│  │   ├─ Viabilidade lógica             │               │
│  │   └─ Progresso em relação ao objetivo
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ STAGE 3: PRUNING (PODA)             │               │
│  │ ─────────────────────────────────   │               │
│  │ Estratégias:                        │               │
│  │   ├─ Top-K: manter só Top-K nós    │               │
│  │   ├─ Threshold: remover score < X  │               │
│  │   ├─ Beam search: expandir Top-K   │               │
│  │   └─ Simulated annealing: remover   │               │
│  │       ruins probabilisticamente     │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ STAGE 4: BACKTRACKING (opcional)    │               │
│  │ ─────────────────────────────────   │               │
│  │ Se nó folha não leva a solução:     │               │
│  │   ├─ Voltar ao pai                  │               │
│  │   ├─ Explorar outro ramo            │               │
│  │   └─ DFS/BFS conforme heurística    │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│  ┌─────────────────────────────────────┐               │
│  │ CHECK TERMINATION:                  │               │
│  │   ├─ Solução encontrada? → return   │               │
│  │   ├─ Orçamento esgotado? → return   │               │
│  │   ├─ Árvore podada à morte? → return│               │
│  │   └─ Iterações máximas? → return    │               │
│  │                                      │               │
│  │   SENÃO: volta para STAGE 1          │               │
│  └────────────┬────────────────────────┘               │
│               │                                         │
│               ▼                                         │
│           RETURN best_path                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📐 Representação de Dados

### Estrutura de Nó

```python
class ThoughtNode:
    """Representa um pensamento (nó) na árvore"""
    
    # Identidade
    node_id: str                    # UUID único
    depth: int                      # Profundidade na árvore (0 = root)
    parent_id: Optional[str]        # ID do nó pai (None se root)
    
    # Conteúdo
    thought_text: str               # O pensamento/solução parcial
    context: str                    # Contexto que levou aqui
    
    # Avaliação
    score: float                    # [0, 1] qualidade do pensamento
    is_solution: bool               # Verdadeiro se resolve o problema
    
    # Metadata
    tokens_used: int                # Tokens para gerar este nó
    generation_time_ms: float       # Quanto tempo para gerar
    
    # Estado
    is_expanded: bool               # Já foi expandido?
    children_ids: List[str]         # IDs dos filhos
    is_pruned: bool                 # Foi podado?
```

### Estrutura de Árvore

```python
class ThoughtTree:
    """Representa a árvore de pensamentos completa"""
    
    root: ThoughtNode               # Nó raiz
    nodes: Dict[str, ThoughtNode]   # Todos nós por ID
    
    # Navegação
    current_frontier: List[str]     # Nós a expandir (fila)
    best_path: List[str]            # Caminho da raiz até melhor nó
    
    # Estatísticas
    total_depth: int                # Profundidade máxima
    total_width: int                # Máximo de filhos em qualquer nível
    nodes_generated: int            # Total de nós criados
    nodes_pruned: int               # Total podado
    
    def get_path_text(self, node_id: str) -> str:
        """Reconstruir caminho completo de root até nó"""
        path = []
        current = node_id
        while current:
            path.append(self.nodes[current].thought_text)
            current = self.nodes[current].parent_id
        return " → ".join(reversed(path))
```

---

## 🧠 Pseudocódigo Completo de ToT

```python
class TreeOfThoughtsEngine(RecursiveThinkingEngine):
    """Implementação de Tree of Thoughts"""
    
    def run(
        self, 
        prompt: str, 
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Executa ToT sobre um prompt
        
        Args:
            prompt: pergunta/tarefa a resolver
            config: configuração (k, num_generate, etc)
        
        Returns:
            RecursionResult com melhor solução
        """
        
        # Inicializar árvore
        tree = ThoughtTree()
        root = ThoughtNode(
            node_id="root",
            depth=0,
            parent_id=None,
            thought_text=prompt,
            context="",
            score=0.5,  # Inicial
            is_solution=False
        )
        tree.root = root
        tree.nodes["root"] = root
        tree.current_frontier = ["root"]
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="tot",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config
        )
        
        # Loop principal
        iteration = 0
        while not self._should_terminate(state, tree):
            iteration += 1
            
            # ─────────────────────────────────────
            # STAGE 1: GENERATE THOUGHTS
            # ─────────────────────────────────────
            
            # Pegar próximo nó a expandir (BFS ou DFS)
            node_id = tree.current_frontier.pop(0)
            current_node = tree.nodes[node_id]
            
            # Gerar K variações deste nó
            generated_thoughts = self._generate_thoughts(
                current_node,
                tree,
                config,
                k=config.extra_params.get("k_candidates", 3)
            )
            
            # Criar nós filhos
            for i, thought in enumerate(generated_thoughts):
                child_id = f"{node_id}_child_{i}"
                child_node = ThoughtNode(
                    node_id=child_id,
                    depth=current_node.depth + 1,
                    parent_id=node_id,
                    thought_text=thought,
                    context=current_node.thought_text
                )
                tree.nodes[child_id] = child_node
                current_node.children_ids.append(child_id)
            
            # ─────────────────────────────────────
            # STAGE 2: EVALUATE THOUGHTS
            # ─────────────────────────────────────
            
            for child_id in current_node.children_ids:
                child = tree.nodes[child_id]
                
                # Avaliar qualidade (0 a 1)
                child.score = self._evaluate_thought(
                    child,
                    tree,
                    config
                )
                
                # Verificar se é solução final
                child.is_solution = self._is_solution(
                    child,
                    config
                )
                
                # Se é solução, guardar
                if child.is_solution:
                    if not tree.best_path or \
                       child.score > tree.nodes[tree.best_path[-1]].score:
                        tree.best_path = tree.get_path_to_node(child_id)
            
            # ─────────────────────────────────────
            # STAGE 3: PRUNING (PODA)
            # ─────────────────────────────────────
            
            # Aplicar estratégia de poda
            tree.current_frontier = self._prune_frontier(
                tree,
                config,
                strategy=config.extra_params.get("prune_strategy", "top_k")
            )
            
            # ─────────────────────────────────────
            # STAGE 4: BACKTRACKING (opcional)
            # ─────────────────────────────────────
            
            if not tree.current_frontier:
                # Fila vazia - tentar backtracking
                tree.current_frontier = self._backtrack(tree, config)
                
                if not tree.current_frontier:
                    # Nenhum nó para explorar - terminar
                    break
            
            # ─────────────────────────────────────
            # ARMAZENAR ITERAÇÃO
            # ─────────────────────────────────────
            
            iteration_record = IterationRecord(
                iteration_number=iteration,
                timestamp=datetime.now(),
                generated_candidates=generated_thoughts,
                evaluation_scores=[
                    tree.nodes[cid].score 
                    for cid in current_node.children_ids
                ],
                selected_best=current_node.children_ids[0],  # Top-1
                feedback_from_critic="",  # ToT não usa crítica
                refined_prompt=prompt,
                tokens_this_iteration=config.max_tokens_per_iteration,
                duration_ms=0,
                extra_data={
                    "tree_depth": tree.total_depth,
                    "tree_width": tree.total_width,
                    "nodes_count": len(tree.nodes),
                    "best_path": tree.best_path
                }
            )
            
            state.all_iterations.append(iteration_record)
            state.iteration = iteration
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        best_node_id = tree.best_path[-1] if tree.best_path else "root"
        best_node = tree.nodes[best_node_id]
        
        result = RecursionResult(
            final_answer=best_node.thought_text,
            iterations_count=iteration,
            improvement_percent=0,  # Calcular depois
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=state.all_iterations,
            metadata={
                "technique": "tot",
                "tree_depth": tree.total_depth,
                "tree_width": tree.total_width,
                "nodes_generated": tree.nodes_generated,
                "nodes_pruned": tree.nodes_pruned,
                "best_path_depth": len(tree.best_path),
                "best_score": best_node.score,
                "full_tree": tree  # Para visualização
            }
        )
        
        return result
    
    # ════════════════════════════════════════════════════════
    # FUNÇÕES AUXILIARES
    # ════════════════════════════════════════════════════════
    
    def _generate_thoughts(
        self,
        parent_node: ThoughtNode,
        tree: ThoughtTree,
        config: RecursionConfig,
        k: int
    ) -> List[str]:
        """Gerar K pensamentos filhos"""
        
        system_prompt = f"""
Você é um pensador estratégico. Dado um contexto e um pensamento anterior,
gere {k} pensamentos alternativos que avançam a solução.

Formato: [Pensamento 1]
[Pensamento 2]
...
        """
        
        user_prompt = f"""
Contexto original: {config.extra_params.get('original_problem', '')}
Pensamento anterior: {parent_node.thought_text}

Gere {k} pensamentos distintos que levem a novas perspectivas.
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens_per_iteration
        )
        
        # Parse resposta em K pensamentos
        thoughts = response.split("\n\n")[:k]
        return thoughts
    
    def _evaluate_thought(
        self,
        node: ThoughtNode,
        tree: ThoughtTree,
        config: RecursionConfig
    ) -> float:
        """Avaliar qualidade de um pensamento (0 a 1)"""
        
        evaluation_prompt = f"""
Avalie este pensamento em uma escala de 0 a 1:

Pensamento: {node.thought_text}

Problema original: {config.extra_params.get('original_problem', '')}

Responda APENAS com um número entre 0 e 1.
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é um crítico de qualidade de raciocínio.",
            user_prompt=evaluation_prompt,
            temperature=0.0,  # Determinístico
            max_tokens=10
        )
        
        try:
            score = float(response.strip())
            return max(0.0, min(1.0, score))  # Clamp [0, 1]
        except:
            return 0.5  # Default
    
    def _is_solution(
        self,
        node: ThoughtNode,
        config: RecursionConfig
    ) -> bool:
        """Verificar se é solução final"""
        
        check_prompt = f"""
Este pensamento resolve o problema original?

Pensamento: {node.thought_text}
Problema: {config.extra_params.get('original_problem', '')}

Responda SIM ou NÃO.
        """
        
        response = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é um verificador.",
            user_prompt=check_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        return "SIM" in response.upper() or "YES" in response.upper()
    
    def _prune_frontier(
        self,
        tree: ThoughtTree,
        config: RecursionConfig,
        strategy: str = "top_k"
    ) -> List[str]:
        """Aplicar estratégia de poda"""
        
        if strategy == "top_k":
            # Manter apenas Top-K nós com maior score
            k = config.extra_params.get("beam_width", 3)
            
            # Obter todos nós não-podados não-expandidos
            candidates = [
                node_id for node_id, node in tree.nodes.items()
                if not node.is_pruned and not node.is_expanded
            ]
            
            # Ordenar por score
            candidates.sort(
                key=lambda nid: tree.nodes[nid].score,
                reverse=True
            )
            
            # Marcar podados
            for node_id in candidates[k:]:
                tree.nodes[node_id].is_pruned = True
            
            return candidates[:k]
        
        elif strategy == "threshold":
            threshold = config.extra_params.get("threshold", 0.5)
            return [
                node_id for node_id, node in tree.nodes.items()
                if node.score >= threshold and not node.is_expanded
            ]
        
        else:  # BFS padrão
            return tree.current_frontier
    
    def _backtrack(
        self,
        tree: ThoughtTree,
        config: RecursionConfig
    ) -> List[str]:
        """Tentar backtracking a nós anteriores"""
        
        # DFS para encontrar nós não-expandidos em depth menor
        unexpanded = [
            node_id for node_id, node in tree.nodes.items()
            if not node.is_expanded and not node.is_pruned
        ]
        
        if unexpanded:
            # Ordena por depth (mais rasos primeiro)
            unexpanded.sort(
                key=lambda nid: tree.nodes[nid].depth
            )
            return unexpanded
        
        return []
    
    def _should_terminate(
        self,
        state: RecursionState,
        tree: ThoughtTree
    ) -> bool:
        """Verificar se deve parar ToT"""
        
        # Critério 1: Solução encontrada
        if tree.best_path and tree.nodes[tree.best_path[-1]].is_solution:
            return True
        
        # Critério 2: Limite de iterações
        if state.iteration >= state.config.max_iterations:
            return True
        
        # Critério 3: Sem nós para explorar
        if not tree.current_frontier:
            return True
        
        # Critério 4: Limite de tokens
        if state.tokens_used >= state.config.max_tokens_total:
            return True
        
        return False
```

---

## 🔀 Graph of Thoughts (GoT) - Extensão

GoT generaliza ToT permitindo que nós tenham múltiplos pais (um nó pode ser alcançado por caminhos diferentes):

```python
class GraphOfThoughtsEngine(RecursiveThinkingEngine):
    """Implementação de Graph of Thoughts"""
    
    # Igual a ToT, mas:
    
    class ThoughtNode:
        parent_ids: List[str]       # Múltiplos pais possíveis!
        incoming_edges: List[Edge]  # Todas arestas de entrada
        outgoing_edges: List[Edge]  # Todas arestas de saída
    
    def _merge_paths(self, node_id1: str, node_id2: str) -> bool:
        """
        Se dois nós chegam ao mesmo conteúdo,
        mesclar em um nó no grafo (não em árvore)
        """
        content_hash_1 = hash(self.graph.nodes[node_id1].thought_text)
        content_hash_2 = hash(self.graph.nodes[node_id2].thought_text)
        
        if content_hash_1 == content_hash_2:
            # Mesclar arestas
            self.graph.nodes[node_id1].incoming_edges.extend(
                self.graph.nodes[node_id2].incoming_edges
            )
            # Remover node_id2 (redundante)
            del self.graph.nodes[node_id2]
            return True
        return False
```

---

## 📊 Parâmetros de Configuração para ToT

```python
{
    "technique": "tot",
    "provider": "openai",
    "model": "gpt-4o",
    
    # ToT específico
    "extra_params": {
        # Geração
        "k_candidates": 3,              # Quantos filhos por nó
        
        # Poda
        "prune_strategy": "top_k",      # "top_k", "threshold", "bfs"
        "beam_width": 5,                # Top-K a manter
        "threshold": 0.6,               # Score mínimo se threshold
        
        # Exploração
        "search_strategy": "dfs",       # "dfs", "bfs"
        "max_depth": 6,                 # Profundidade máxima
        
        # Original problem (para referência)
        "original_problem": "Resolva esta equação matemática: 2x + 5 = 13"
    },
    
    # Terminação
    "max_iterations": 10,               # Máximo de expansões
    "max_tokens_total": 15000,
    "max_time_ms": 180000
}
```

---

## 🎯 Quando Usar ToT vs CoT

| Situação | CoT (Baseline) | ToT | GoT |
|----------|---|---|---|
| Pergunta simples (fato) | ✅✅✅ | ❌ | ❌ |
| Pergunta linear (passo-a-passo) | ✅✅ | ✅ | ✅ |
| Decisão entre opções | ✅ | ✅✅✅ | ✅✅✅ |
| Prova matemática | ❌ | ✅✅✅ | ✅✅ |
| Planejamento multi-caminho | ❌ | ✅✅✅ | ✅✅✅ |
| Exploração criativa | ✅ | ✅✅ | ✅✅✅ |

---

## 📈 Métricas de Avaliação de ToT

| Métrica | Definição | Alvo |
|---------|-----------|------|
| **Success Rate** | % de problemas resolvidos | >90% |
| **Reasoning Depth** | Profundidade média da árvore | 3-5 níveis |
| **Token Efficiency** | Tokens/problema | ↓ minimizar |
| **Pruning Ratio** | (nós_gerados - nós_finais) / nós_gerados | >60% |
| **Path Coherence** | Quão lógico é o caminho final | Qualitativo |

---

## 🚀 Exemplo de Uso (Frontend)

```javascript
// Usuário seleciona ToT na UI
const config = {
    technique: "tot",
    provider: "openai",
    model: "gpt-4o",
    extra_params: {
        k_candidates: 3,
        beam_width: 5,
        prune_strategy: "top_k"
    }
};

// Fazer requisição
const response = await fetch("/api/improve-prompt-recursive", {
    method: "POST",
    body: JSON.stringify({
        prompt: "Prove que √2 é irracional",
        config: config
    })
});

// WebSocket stream
const ws = new WebSocket("ws://localhost:8000/ws/recursive");
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    
    // Atualizar UI com iteração
    // exibir árvore em tempo real
    // mostrar scores
};
```

---

## 📚 Referências

- Yao et al., "Tree of Thoughts: Deliberate Problem Solving with LLMs" (NeurIPS 2023)
- Long et al., "Graph of Thoughts" (2024)

**Próximo**: [04-SELF-REFINE-E-REFLEXION.md](./04-SELF-REFINE-E-REFLEXION.md)
