# 03 - Tree of Thoughts (ToT) e Graph of Thoughts (GoT) Engines

## 🎯 Objetivo

Documentar a implementação de dois dos algoritmos mais poderosos para raciocínio recursivo:
- **Tree of Thoughts (ToT)**: Explora soluções como uma árvore, onde cada nó é um pensamento intermediário
- **Graph of Thoughts (GoT)**: Extensão de ToT que permite conexões arbitrárias entre pensamentos (DAG)

Ambos utilizam **pontuação de nós**, **poda por beam search**, e **backtracking inteligente** para encontrar a melhor sequência de raciocínio. Este documento fornece:
- Algoritmos completos com pseudocode
- Estruturas de dados para nós e grafos
- Estratégias de busca (BFS, DFS, beam search, best-first)
- Exemplos práticos com trace de execução
- Integração com o `RecursiveThinkingEngine`

---

## 📐 Conceitos Fundamentais

### Tree of Thoughts (ToT)

Tree of Thoughts é uma estratégia de busca onde:
1. **Nó raiz**: O prompt inicial (questão)
2. **Nós internos**: Pensamentos intermediários (raciocínios parciais)
3. **Nós folha**: Soluções candidatas (respostas finais)
4. **Arestas**: Transições lógicas entre pensamentos

```
                    [Q: Resolver 5 + 3 * 2]
                           (raiz)
                             |
               ______________|______________
              /              |              \
         [5+6=11]      [5 + (3*2)]     [Erro: ordem]
        (errado)       (intermediário)   (inválido)
           |                 |                |
           X            [5+6=11]          X
                        (resposta)
```

**Características principais:**
- Exploração sistemática de múltiplos caminhos
- Pontuação de nós para guiar a busca
- Poda para limitar explosão combinatória
- Backtracking quando um caminho falha

### Graph of Thoughts (GoT)

Graph of Thoughts estende ToT permitindo:
- **Múltiplos pais por nó**: Um pensamento pode derivar de múltiplas fontes
- **Conexões arbitrárias**: Não apenas árvore, mas DAG (Directed Acyclic Graph)
- **Fusão de caminhos**: Combinar resultados de diferentes branches

```
                    [Q: Análise SWOT]
                           |
            _______________|_______________
           /               |               \
      [Forças]         [Fraquezas]    [Oportunidades]
         |                |               /
         |                |              /
         |________________|_____________/
                    |
            [Síntese integrada]
                (resposta)
```

**Vantagens sobre ToT:**
- Reutilização de pensamentos derivados
- Fusão eficiente de análises paralelas
- Melhor representação de problemas com múltiplas perspectivas

---

## 🏗️ Arquitetura: Nós e Estruturas de Dados

### 1. Classe Node (Nó de Pensamento)

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ThoughtNode:
    """
    Representa um nó único na árvore/grafo de pensamentos.
    
    Atributos:
        node_id: Identificador único (hash do conteúdo + timestamp)
        content: Texto do pensamento intermediário
        depth: Profundidade na árvore (0 = raiz)
        parent_ids: IDs dos nós pais (ToT: 1, GoT: múltiplos)
        children_ids: IDs dos nós filhos
        score: Pontuação heurística do nó (0-1)
        confidence: Confiança na qualidade do pensamento (0-1)
        is_solution: True se é uma solução completa
        reasoning: Explicação de como chegou neste nó
        tokens_used: Tokens gastos para gerar este nó
        metadata: Informações adicionais (estratégia usada, feedback, etc)
    """
    node_id: str
    content: str
    depth: int
    parent_ids: List[str] = field(default_factory=list)
    children_ids: List[str] = field(default_factory=list)
    score: float = 0.0
    confidence: float = 0.0
    is_solution: bool = False
    reasoning: str = ""
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash(self.node_id)
    
    def __lt__(self, other):
        """Comparação para ordenação por score (maior primeiro)"""
        return self.score > other.score  # Reverse: score maior = prioridade maior
```

### 2. Classe TreeOfThoughts (Estrutura da Árvore)

```python
from collections import defaultdict, deque
import heapq
from copy import deepcopy

class TreeOfThoughts:
    """
    Estrutura que representa uma árvore de pensamentos.
    Gerencia nós, arestas, pontuação e busca.
    """
    
    def __init__(self, root_content: str, max_depth: int = 5, beam_width: int = 3):
        """
        Inicializa a árvore.
        
        Args:
            root_content: Conteúdo do nó raiz (prompt inicial)
            max_depth: Profundidade máxima da árvore
            beam_width: Número de nós mantidos em cada nível (beam search)
        """
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root_id = self._create_node(root_content, depth=0)
    
    def _create_node(
        self, 
        content: str, 
        depth: int, 
        parent_id: Optional[str] = None,
        reasoning: str = "",
        tokens_used: int = 0
    ) -> str:
        """
        Cria um novo nó na árvore.
        
        Args:
            content: Texto do pensamento
            depth: Profundidade do nó
            parent_id: ID do nó pai
            reasoning: Explicação da derivação
            tokens_used: Tokens utilizados
            
        Returns:
            node_id do nó criado
        """
        node_id = f"node_{depth}_{len(self.nodes)}"
        
        parent_ids = [parent_id] if parent_id else []
        node = ThoughtNode(
            node_id=node_id,
            content=content,
            depth=depth,
            parent_ids=parent_ids,
            reasoning=reasoning,
            tokens_used=tokens_used
        )
        
        self.nodes[node_id] = node
        
        # Adicionar à lista de filhos do pai
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children_ids.append(node_id)
        
        return node_id
    
    def add_children(
        self, 
        parent_id: str, 
        candidates: List[Dict[str, Any]],
        depth_increase: int = 1
    ) -> List[str]:
        """
        Adiciona múltiplos nós filhos a um nó pai.
        
        Args:
            parent_id: ID do nó pai
            candidates: Lista de candidatos com 'content', 'reasoning', 'tokens_used'
            depth_increase: Incremento de profundidade
            
        Returns:
            Lista de IDs dos nós filhos criados
        """
        if parent_id not in self.nodes:
            raise ValueError(f"Parent node {parent_id} not found")
        
        parent_node = self.nodes[parent_id]
        new_depth = parent_node.depth + depth_increase
        
        if new_depth > self.max_depth:
            return []
        
        child_ids = []
        for candidate in candidates:
            child_id = self._create_node(
                content=candidate.get('content', ''),
                depth=new_depth,
                parent_id=parent_id,
                reasoning=candidate.get('reasoning', ''),
                tokens_used=candidate.get('tokens_used', 0)
            )
            child_ids.append(child_id)
        
        return child_ids
    
    def score_node(
        self, 
        node_id: str, 
        heuristic_score: float,
        confidence: float
    ) -> None:
        """
        Atualiza a pontuação de um nó.
        
        Args:
            node_id: ID do nó
            heuristic_score: Pontuação heurística (0-1)
            confidence: Confiança (0-1)
        """
        if node_id in self.nodes:
            self.nodes[node_id].score = heuristic_score
            self.nodes[node_id].confidence = confidence
    
    def get_best_nodes_at_depth(self, depth: int, top_k: int = None) -> List[ThoughtNode]:
        """
        Retorna os K melhores nós em uma profundidade específica.
        Implementa beam search.
        
        Args:
            depth: Profundidade desejada
            top_k: Número de nós a retornar (default: beam_width)
            
        Returns:
            Lista dos melhores nós ordenados por score
        """
        k = top_k or self.beam_width
        
        nodes_at_depth = [
            node for node in self.nodes.values() 
            if node.depth == depth
        ]
        
        # Ordenar por score (maior primeiro) e retornar top K
        sorted_nodes = sorted(nodes_at_depth, key=lambda n: n.score, reverse=True)
        return sorted_nodes[:k]
    
    def mark_solution(self, node_id: str) -> None:
        """Marca um nó como solução completa."""
        if node_id in self.nodes:
            self.nodes[node_id].is_solution = True
    
    def get_solution_path(self, node_id: str) -> List[str]:
        """
        Retorna o caminho da raiz até um nó (para trace de reasoning).
        
        Args:
            node_id: ID do nó alvo
            
        Returns:
            Lista de node_ids do caminho (raiz → nó)
        """
        path = []
        current_id = node_id
        
        while current_id:
            path.append(current_id)
            current_node = self.nodes.get(current_id)
            if not current_node or not current_node.parent_ids:
                break
            current_id = current_node.parent_ids[0]  # ToT: um pai
        
        return list(reversed(path))
    
    def get_tree_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da árvore."""
        solutions = [n for n in self.nodes.values() if n.is_solution]
        total_tokens = sum(n.tokens_used for n in self.nodes.values())
        
        return {
            'total_nodes': len(self.nodes),
            'total_solutions': len(solutions),
            'max_actual_depth': max((n.depth for n in self.nodes.values()), default=0),
            'total_tokens_used': total_tokens,
            'average_score': sum(n.score for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        }
```

### 3. Classe GraphOfThoughts (Estrutura do Grafo)

```python
class GraphOfThoughts:
    """
    Estrutura que representa um grafo de pensamentos (DAG).
    Estende TreeOfThoughts permitindo múltiplos pais por nó.
    """
    
    def __init__(self, root_content: str, max_depth: int = 5, beam_width: int = 3):
        """Inicializa o grafo de pensamentos."""
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root_id = self._create_node(root_content, depth=0)
        self.topological_order: List[str] = []
    
    def _create_node(
        self, 
        content: str, 
        depth: int, 
        parent_ids: List[str] = None,
        reasoning: str = "",
        tokens_used: int = 0
    ) -> str:
        """Cria um novo nó (permite múltiplos pais)."""
        node_id = f"node_{depth}_{len(self.nodes)}"
        
        node = ThoughtNode(
            node_id=node_id,
            content=content,
            depth=depth,
            parent_ids=parent_ids or [],
            reasoning=reasoning,
            tokens_used=tokens_used
        )
        
        self.nodes[node_id] = node
        
        # Adicionar à lista de filhos dos pais
        for parent_id in (parent_ids or []):
            if parent_id in self.nodes:
                self.nodes[parent_id].children_ids.append(node_id)
        
        return node_id
    
    def add_child_with_multiple_parents(
        self,
        parent_ids: List[str],
        content: str,
        reasoning: str = "",
        tokens_used: int = 0
    ) -> str:
        """
        Cria um nó filho que depende de múltiplos pais.
        Essencial para GoT: fusão de caminhos.
        
        Args:
            parent_ids: IDs dos nós pais
            content: Conteúdo do novo nó
            reasoning: Explicação (ex: "Síntese de...")
            tokens_used: Tokens utilizados
            
        Returns:
            ID do novo nó
        """
        if not parent_ids:
            raise ValueError("Child node must have at least one parent")
        
        # Calcular profundidade como máxima dos pais + 1
        parent_depths = [self.nodes[pid].depth for pid in parent_ids if pid in self.nodes]
        if not parent_depths:
            raise ValueError("Invalid parent IDs")
        
        new_depth = max(parent_depths) + 1
        
        if new_depth > self.max_depth:
            return None
        
        child_id = self._create_node(
            content=content,
            depth=new_depth,
            parent_ids=parent_ids,
            reasoning=reasoning,
            tokens_used=tokens_used
        )
        
        return child_id
    
    def topological_sort(self) -> List[str]:
        """
        Retorna uma ordem topológica dos nós (útil para avaliar GoT).
        Implementa algoritmo de Kahn.
        """
        from collections import defaultdict
        
        # Calcular in-degree
        in_degree = defaultdict(int)
        for node_id in self.nodes:
            in_degree[node_id] = len(self.nodes[node_id].parent_ids)
        
        # Iniciar com nós que não têm pais (raiz)
        queue = deque([nid for nid in self.nodes if in_degree[nid] == 0])
        topo_order = []
        
        while queue:
            current = queue.popleft()
            topo_order.append(current)
            
            # Para cada filho, decrementar in-degree
            for child_id in self.nodes[current].children_ids:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)
        
        if len(topo_order) != len(self.nodes):
            raise ValueError("Ciclo detectado no grafo!")
        
        self.topological_order = topo_order
        return topo_order
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do grafo."""
        solutions = [n for n in self.nodes.values() if n.is_solution]
        total_tokens = sum(n.tokens_used for n in self.nodes.values())
        
        # Contar arestas
        edges = sum(len(n.parent_ids) for n in self.nodes.values())
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': edges,
            'total_solutions': len(solutions),
            'max_actual_depth': max((n.depth for n in self.nodes.values()), default=0),
            'total_tokens_used': total_tokens,
            'average_parents_per_node': edges / len(self.nodes) if self.nodes else 0
        }
```

---

## 🧠 Estratégias de Pontuação de Nós

### 1. Pontuação Heurística

```python
class NodeScoringStrategy:
    """
    Define estratégias para pontuar nós intermediários.
    Essencial para guiar a busca.
    """
    
    @staticmethod
    def score_by_length_quality(content: str, ideal_length: int = 200) -> float:
        """
        Heurística simples: conteúdo com comprimento próximo ao ideal.
        Evita respostas muito curtas (incompletas) ou muito longas (verbosas).
        
        Args:
            content: Texto do nó
            ideal_length: Comprimento ideal em palavras
            
        Returns:
            Score entre 0-1
        """
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Penalizar desvio do ideal
        deviation = abs(word_count - ideal_length)
        max_deviation = ideal_length * 2
        
        score = 1.0 - (deviation / max_deviation)
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def score_by_structure(content: str) -> float:
        """
        Heurística: conteúdo bem estruturado (parágrafos, pontuação).
        
        Args:
            content: Texto do nó
            
        Returns:
            Score entre 0-1
        """
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Bonificação por múltiplos parágrafos
        paragraph_bonus = min(1.0, len(non_empty_lines) / 3.0)
        
        # Bonificação por pontuação
        punct_count = sum(1 for c in content if c in '.!?;:')
        punct_bonus = min(1.0, punct_count / 5.0)
        
        return (paragraph_bonus * 0.6) + (punct_bonus * 0.4)
    
    @staticmethod
    def score_by_logical_progression(prev_content: str, current_content: str) -> float:
        """
        Heurística: o nó atual progride logicamente em relação ao anterior.
        Detecta palavras de transição e conexão lógica.
        
        Args:
            prev_content: Conteúdo do nó anterior
            current_content: Conteúdo do nó atual
            
        Returns:
            Score entre 0-1
        """
        transition_words = [
            'portanto', 'consequentemente', 'assim', 'logo',
            'para', 'além disso', 'logo após', 'finalmente',
            'conclusão', 'resultado', 'implicação', 'decorre'
        ]
        
        has_transition = any(
            word.lower() in current_content.lower() 
            for word in transition_words
        )
        
        transition_score = 0.7 if has_transition else 0.3
        
        # Verificar se há referência ao conteúdo anterior
        prev_words = set(prev_content.split()[:10])  # Primeiras 10 palavras
        curr_words = set(current_content.split()[:10])
        overlap = len(prev_words & curr_words)
        
        continuity_score = min(1.0, overlap / 3.0)
        
        return (transition_score * 0.4) + (continuity_score * 0.6)
    
    @staticmethod
    def score_combined(
        content: str,
        prev_content: str = None,
        ideal_length: int = 200,
        use_progression: bool = True
    ) -> float:
        """
        Combina múltiplas heurísticas para uma pontuação robusta.
        
        Args:
            content: Conteúdo do nó
            prev_content: Conteúdo do nó anterior (opcional)
            ideal_length: Comprimento ideal
            use_progression: Se True, considerar progressão lógica
            
        Returns:
            Score entre 0-1
        """
        length_score = NodeScoringStrategy.score_by_length_quality(content, ideal_length)
        structure_score = NodeScoringStrategy.score_by_structure(content)
        
        if use_progression and prev_content:
            prog_score = NodeScoringStrategy.score_by_logical_progression(prev_content, content)
            return (length_score * 0.3) + (structure_score * 0.3) + (prog_score * 0.4)
        else:
            return (length_score * 0.5) + (structure_score * 0.5)
```

### 2. Pontuação por LLM

```python
class LLMNodeEvaluator:
    """
    Usa o LLM para avaliar a qualidade de um nó intermediário.
    Permite feedback detalhado e refinado.
    """
    
    def __init__(self, llm_provider):
        """
        Args:
            llm_provider: Instância de um provider LLM (ex: OpenAI)
        """
        self.llm_provider = llm_provider
    
    def evaluate_node_quality(
        self,
        node_content: str,
        original_question: str,
        evaluation_criteria: str = None
    ) -> Dict[str, Any]:
        """
        Usa prompt de avaliação para fazer LLM avaliar qualidade.
        
        Args:
            node_content: Conteúdo do nó a avaliar
            original_question: Pergunta original
            evaluation_criteria: Critérios específicos (ex: "clareza, precisão, completude")
            
        Returns:
            Dict com 'score' (0-1), 'feedback', 'strengths', 'weaknesses'
        """
        if not evaluation_criteria:
            evaluation_criteria = "clareza, precisão, completude, relevância"
        
        evaluation_prompt = f"""
Avalie o seguinte pensamento intermediário em relação à pergunta original.

PERGUNTA ORIGINAL:
{original_question}

PENSAMENTO INTERMEDIÁRIO:
{node_content}

CRITÉRIOS DE AVALIAÇÃO:
{evaluation_criteria}

Responda em JSON com:
{{
    "score": (número 0-1),
    "feedback": "avaliação geral",
    "strengths": ["ponto forte 1", "ponto forte 2"],
    "weaknesses": ["ponto fraco 1", "ponto fraco 2"],
    "suggestions": "como melhorar"
}}
"""
        
        response = self.llm_provider.call(
            prompt=evaluation_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse JSON response
        import json
        try:
            result = json.loads(response)
            return result
        except:
            return {
                'score': 0.5,
                'feedback': response,
                'strengths': [],
                'weaknesses': [],
                'suggestions': ''
            }
    
    def generate_refined_version(
        self,
        node_content: str,
        feedback: str,
        original_question: str
    ) -> str:
        """
        Usa feedback para gerar versão refinada do nó.
        
        Args:
            node_content: Conteúdo original
            feedback: Feedback de avaliação
            original_question: Pergunta original
            
        Returns:
            Conteúdo refinado
        """
        refinement_prompt = f"""
Melhore o seguinte pensamento intermediário considerando o feedback.

PERGUNTA ORIGINAL:
{original_question}

PENSAMENTO ORIGINAL:
{node_content}

FEEDBACK PARA MELHORIA:
{feedback}

Gere uma versão melhorada que incorpore o feedback mantendo coerência com a pergunta original.
"""
        
        refined = self.llm_provider.call(
            prompt=refinement_prompt,
            temperature=0.5,
            max_tokens=500
        )
        
        return refined
```

---

## 🔍 Estratégias de Busca

### 1. Beam Search

```python
class BeamSearchStrategy:
    """
    Implementa Beam Search para exploração de ToT/GoT.
    Limita explosão combinatória mantendo K melhores caminhos.
    """
    
    def __init__(self, tree: TreeOfThoughts, beam_width: int = 3):
        """
        Args:
            tree: Instância de TreeOfThoughts
            beam_width: Número de nós a manter por nível
        """
        self.tree = tree
        self.beam_width = beam_width
        self.search_history = []
    
    def search(
        self,
        initial_prompt: str,
        generate_candidates_fn,
        evaluate_candidates_fn,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Executa beam search na árvore de pensamentos.
        
        Args:
            initial_prompt: Prompt inicial
            generate_candidates_fn: Função que gera candidatos a partir de um nó
            evaluate_candidates_fn: Função que avalia candidatos
            max_iterations: Máximo de iterações
            
        Returns:
            Dict com 'best_solution', 'path', 'iterations', 'tree_stats'
        """
        current_depth = 0
        current_best_nodes = [self.tree.root_id]
        
        for iteration in range(max_iterations):
            if current_depth >= self.tree.max_depth:
                break
            
            next_best_nodes = []
            
            # Para cada nó no beam atual
            for node_id in current_best_nodes:
                node = self.tree.nodes[node_id]
                
                # Gerar candidatos (children)
                candidates = generate_candidates_fn(node.content)
                
                # Adicionar à árvore
                child_ids = self.tree.add_children(
                    node_id,
                    candidates
                )
                
                # Avaliar cada candidato
                for child_id in child_ids:
                    child = self.tree.nodes[child_id]
                    score, confidence = evaluate_candidates_fn(child.content)
                    self.tree.score_node(child_id, score, confidence)
                    
                    # Se é solução, marcar
                    if score > 0.9:
                        self.tree.mark_solution(child_id)
                
                next_best_nodes.extend(child_ids)
            
            # Beam search: manter K melhores
            next_best_nodes.sort(
                key=lambda nid: self.tree.nodes[nid].score,
                reverse=True
            )
            current_best_nodes = next_best_nodes[:self.beam_width]
            
            self.search_history.append({
                'iteration': iteration,
                'depth': current_depth,
                'beam_nodes': current_best_nodes,
                'best_score': self.tree.nodes[current_best_nodes[0]].score if current_best_nodes else 0
            })
            
            current_depth += 1
        
        # Encontrar melhor solução
        best_solution_id = None
        best_score = 0
        
        for node_id, node in self.tree.nodes.items():
            if node.is_solution and node.score > best_score:
                best_score = node.score
                best_solution_id = node_id
        
        if not best_solution_id:
            # Se não achou solução marcada, retornar melhor nó
            best_solution_id = max(self.tree.nodes, key=lambda nid: self.tree.nodes[nid].score)
        
        return {
            'best_solution_id': best_solution_id,
            'best_solution_content': self.tree.nodes[best_solution_id].content,
            'best_score': self.tree.nodes[best_solution_id].score,
            'path': self.tree.get_solution_path(best_solution_id),
            'iterations': len(self.search_history),
            'tree_stats': self.tree.get_tree_stats()
        }
```

### 2. Best-First Search

```python
class BestFirstSearchStrategy:
    """
    Implementa Best-First Search para exploração mais agressiva de nós promissores.
    """
    
    def __init__(self, tree: TreeOfThoughts):
        self.tree = tree
        self.search_history = []
        self.visited = set()
    
    def search(
        self,
        generate_candidates_fn,
        evaluate_candidates_fn,
        max_nodes: int = 100,
        max_depth_limit: int = 10
    ) -> Dict[str, Any]:
        """
        Executa Best-First Search usando priority queue.
        
        Args:
            generate_candidates_fn: Função que gera candidatos
            evaluate_candidates_fn: Função que avalia
            max_nodes: Máximo de nós a explorar
            max_depth_limit: Profundidade máxima
            
        Returns:
            Dict com melhor solução encontrada
        """
        # Priority queue: (negativo_score, node_id)
        pq = [(-self.tree.nodes[self.tree.root_id].score, self.tree.root_id)]
        nodes_explored = 0
        
        while pq and nodes_explored < max_nodes:
            _, node_id = heapq.heappop(pq)
            
            if node_id in self.visited:
                continue
            
            self.visited.add(node_id)
            node = self.tree.nodes[node_id]
            nodes_explored += 1
            
            # Verificar limite de profundidade
            if node.depth >= max_depth_limit:
                continue
            
            # Gerar e avaliar candidatos
            candidates = generate_candidates_fn(node.content)
            child_ids = self.tree.add_children(node_id, candidates)
            
            for child_id in child_ids:
                child = self.tree.nodes[child_id]
                score, confidence = evaluate_candidates_fn(child.content)
                self.tree.score_node(child_id, score, confidence)
                
                if score > 0.9:
                    self.tree.mark_solution(child_id)
                
                # Adicionar à priority queue
                heapq.heappush(pq, (-score, child_id))
        
        # Encontrar melhor
        best_solution_id = max(
            self.tree.nodes,
            key=lambda nid: self.tree.nodes[nid].score
        )
        
        return {
            'best_solution_id': best_solution_id,
            'best_solution_content': self.tree.nodes[best_solution_id].content,
            'best_score': self.tree.nodes[best_solution_id].score,
            'nodes_explored': nodes_explored,
            'path': self.tree.get_solution_path(best_solution_id),
            'tree_stats': self.tree.get_tree_stats()
        }
```

---

## 🚀 ToT Engine - Implementação Completa

```python
from typing import List, Tuple

class TreeOfThoughtsEngine(RecursiveThinkingEngine):
    """
    Implementa Tree of Thoughts como extensão de RecursiveThinkingEngine.
    
    Algoritmo:
    1. GENERATE: Gera múltiplos caminhos de raciocínio (candidatos por nó)
    2. EVALUATE: Pontua cada nó com heurística + LLM
    3. FEEDBACK: Avalia qualidade dos caminhos
    4. REFINE: Proda caminhos fracos, expande promissores (beam search)
    5. TERMINATE: Verifica se solução satisfatória foi encontrada
    """
    
    def __init__(self, config: RecursionConfig, llm_provider, searcher: BeamSearchStrategy = None):
        super().__init__(config)
        self.llm_provider = llm_provider
        self.tree = TreeOfThoughts(
            root_content=config.initial_prompt,
            max_depth=config.max_iterations,
            beam_width=getattr(config, 'beam_width', 3)
        )
        self.searcher = searcher or BeamSearchStrategy(self.tree, beam_width=3)
        self.evaluator = LLMNodeEvaluator(llm_provider)
        self.scorer = NodeScoringStrategy()
    
    def _generate_candidates(self, parent_thought: str, num_candidates: int = 3) -> List[Dict]:
        """
        Gera múltiplos próximos passos a partir de um pensamento intermediário.
        
        Args:
            parent_thought: Conteúdo do nó pai
            num_candidates: Número de candidatos a gerar
            
        Returns:
            Lista de candidatos com 'content', 'reasoning', 'tokens_used'
        """
        prompt = f"""
Você está participando de um processo de raciocínio Tree of Thoughts.
Dado o seguinte pensamento intermediário, gere {num_candidates} próximas linhas de raciocínio DIFERENTES e CRIATIVAS.

PERGUNTA ORIGINAL:
{self.config.initial_prompt}

PENSAMENTO INTERMEDIÁRIO ATUAL:
{parent_thought}

Gere {num_candidates} continuações diferentes. Para cada uma:
1. Próximo passo do raciocínio (novo parágrafo)
2. Justificativa breve

Formato:
CANDIDATO 1: [raciocínio]
CANDIDATO 2: [raciocínio]
...
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        candidates = []
        for line in response.split('\n'):
            if line.startswith('CANDIDATO'):
                content = line.split(':', 1)[1].strip() if ':' in line else ''
                candidates.append({
                    'content': content,
                    'reasoning': f'Generated via ToT expansion',
                    'tokens_used': len(content.split())
                })
        
        return candidates[:num_candidates]
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Tuple[str, float]]:
        """
        Avalia qualidade de cada candidato.
        Usa heurísticas + LLM evaluation.
        
        Args:
            candidates: Lista de candidatos
            
        Returns:
            Lista de (candidate_id, score) tuples
        """
        results = []
        
        for candidate in candidates:
            content = candidate.get('content', '')
            
            # Heurística rápida
            heuristic_score = self.scorer.score_combined(
                content,
                prev_content=self.current_state.current_prompt if self.current_state else None
            )
            
            # Avaliação por LLM
            llm_eval = self.evaluator.evaluate_node_quality(
                content,
                self.config.initial_prompt
            )
            
            # Combinar scores
            final_score = (heuristic_score * 0.4) + (llm_eval.get('score', 0.5) * 0.6)
            
            results.append((candidate.get('id', content[:50]), final_score))
        
        return results
    
    def _generate_feedback(self, iteration: int, candidates: List) -> str:
        """Feedback sobre qualidade dos pensamentos gerados."""
        scores = [c.get('score', 0) for c in candidates]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return f"Iteração {iteration}: Score médio = {avg_score:.2f}"
    
    def _refine_prompt(self, feedback: str, current_prompt: str) -> str:
        """
        Refina o próximo passo baseado em feedback.
        No ToT, isso significa expandir caminhos promissores.
        """
        return current_prompt  # ToT não refina prompt, refina estrutura da árvore
    
    def execute(self) -> RecursionResult:
        """
        Executa o algoritmo Tree of Thoughts completo.
        
        Returns:
            RecursionResult com resultado final
        """
        iteration = 0
        start_time = datetime.now()
        
        try:
            # Executar beam search
            search_result = self.searcher.search(
                initial_prompt=self.config.initial_prompt,
                generate_candidates_fn=self._generate_candidates,
                evaluate_candidates_fn=self._evaluate_candidates,
                max_iterations=self.config.max_iterations
            )
            
            # Retornar resultado
            return RecursionResult(
                final_answer=search_result['best_solution_content'],
                iterations_count=search_result['iterations'],
                tokens_total=self._calculate_tokens_used(),
                quality_score=search_result['best_score'],
                rer_score=self._calculate_rer(search_result['best_score']),
                metadata={
                    'tree_stats': search_result['tree_stats'],
                    'path': search_result['path'],
                    'technique': 'tree_of_thoughts'
                }
            )
        
        except Exception as e:
            raise e
    
    def _calculate_tokens_used(self) -> int:
        """Soma tokens de todos os nós."""
        return sum(node.tokens_used for node in self.tree.nodes.values())
    
    def _calculate_rer(self, final_quality: float) -> float:
        """Calcula RER = Quality / (Tokens / 1000)."""
        tokens = self._calculate_tokens_used()
        if tokens == 0:
            return 0
        return (final_quality * 100) / (tokens / 1000)
```

---

## 🌐 GoT Engine - Implementação Completa

```python
class GraphOfThoughtsEngine(RecursiveThinkingEngine):
    """
    Implementa Graph of Thoughts permitindo múltiplos pais por nó.
    Ideal para problemas com múltiplas perspectivas que precisam ser sintetizadas.
    
    Exemplo: Análise SWOT, síntese multi-perspectiva, problemas com múltiplos ângulos
    """
    
    def __init__(self, config: RecursionConfig, llm_provider):
        super().__init__(config)
        self.llm_provider = llm_provider
        self.graph = GraphOfThoughts(
            root_content=config.initial_prompt,
            max_depth=config.max_iterations,
            beam_width=getattr(config, 'beam_width', 3)
        )
        self.evaluator = LLMNodeEvaluator(llm_provider)
    
    def _generate_candidates(self, parent_thought: str, num_candidates: int = 3) -> List[Dict]:
        """Similar ao ToT, mas pode gerar candidatos de múltiplos ângulos."""
        # Implementação similar ao TreeOfThoughtsEngine
        pass
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Tuple[str, float]]:
        """Avaliação similar ao ToT."""
        pass
    
    def execute_with_fusion(
        self,
        branches: List[str],
        fusion_strategy: str = 'synthesis'
    ) -> RecursionResult:
        """
        Executa GoT com estratégia de fusão de branches.
        
        Args:
            branches: Lista de perspectivas/branches (ex: ['Forças', 'Fraquezas', 'Oportunidades'])
            fusion_strategy: 'synthesis', 'voting', ou 'weighted_average'
            
        Returns:
            RecursionResult com síntese final
        """
        branch_node_ids = []
        
        # Fase 1: Explorar cada branch independentemente
        for branch in branches:
            # Criar sub-nó para cada perspectiva
            branch_prompt = f"{self.config.initial_prompt}\n\nFoco em: {branch}"
            branch_id = self.graph._create_node(
                content=f"Análise focada em: {branch}",
                depth=1,
                parent_ids=[self.graph.root_id]
            )
            branch_node_ids.append(branch_id)
        
        # Fase 2: Expandir cada branch
        for branch_id in branch_node_ids:
            # Gerar candidatos para este branch
            branch_node = self.graph.nodes[branch_id]
            candidates = self._generate_candidates(branch_node.content)
            
            # Adicionar filhos
            for candidate in candidates:
                child_id = self.graph.add_child_with_multiple_parents(
                    parent_ids=[branch_id],
                    content=candidate.get('content', ''),
                    reasoning=candidate.get('reasoning', '')
                )
        
        # Fase 3: Fusão - criar nó que sintetiza todos os branches
        if fusion_strategy == 'synthesis':
            fusion_content = self._synthesize_branches(branch_node_ids)
        
        final_node_id = self.graph.add_child_with_multiple_parents(
            parent_ids=branch_node_ids,
            content=fusion_content,
            reasoning=f"Síntese via {fusion_strategy}"
        )
        
        return RecursionResult(
            final_answer=self.graph.nodes[final_node_id].content,
            iterations_count=len(self.graph.nodes),
            tokens_total=sum(n.tokens_used for n in self.graph.nodes.values()),
            quality_score=self.graph.nodes[final_node_id].score,
            rer_score=0.0,
            metadata={
                'graph_stats': self.graph.get_graph_stats(),
                'branches': branches,
                'fusion_strategy': fusion_strategy,
                'technique': 'graph_of_thoughts'
            }
        )
    
    def _synthesize_branches(self, branch_node_ids: List[str]) -> str:
        """
        Sintetiza resultados de múltiplos branches em uma resposta final.
        
        Args:
            branch_node_ids: IDs dos nós principais de cada branch
            
        Returns:
            Texto sintetizado
        """
        branch_contents = [
            self.graph.nodes[nid].content for nid in branch_node_ids
        ]
        
        synthesis_prompt = f"""
Sintetize os seguintes pontos de vista sobre a pergunta original:

PERGUNTA: {self.config.initial_prompt}

PERSPECTIVA 1: {branch_contents[0]}
PERSPECTIVA 2: {branch_contents[1]}
PERSPECTIVA 3: {branch_contents[2]}

Crie uma síntese integrada que combine as melhores insights de cada perspectiva.
"""
        
        synthesis = self.llm_provider.call(
            prompt=synthesis_prompt,
            temperature=0.5,
            max_tokens=1000
        )
        
        return synthesis
```

---

## 📊 Exemplo Prático: Resolvendo Problema Matemático com ToT

```
PERGUNTA: "Qual é a melhor estratégia para organizar uma conferência com 500 pessoas?"

EXECUÇÃO:

Iteration 0:
├─ Root: "Organizar conferência com 500 pessoas"
└─ Score: 0.5 (inicial)

Iteration 1 (Gerar 3 candidatos):
├─ Candidato A: "Dividir por áreas temáticas com salas paralelas"
│  └─ Score: 0.72 (heurística: bem estruturado + palavras-chave)
├─ Candidato B: "Formato híbrido: presencial + online"
│  └─ Score: 0.68
└─ Candidato C: "Uma grande sessão plenária"
   └─ Score: 0.45

Beam Search: Mantém A e B (beam_width=2)

Iteration 2 (Expandir A e B):
├─ De A: "Salas temáticas com agendamento rotativo"
│  └─ Score: 0.81
├─ De A: "Salas temáticas com horários fixos"
│  └─ Score: 0.75
├─ De B: "Streaming em tempo real com interatividade"
│  └─ Score: 0.79
└─ De B: "Sessões gravadas + transmissão ao vivo"
   └─ Score: 0.72

Beam Search: Seleciona 2 melhores

... (continua até max_iterations ou encontrar score > 0.9)

RESULTADO FINAL:
Solução: "Salas temáticas com agendamento rotativo e streaming paralelo"
Score: 0.88
Tokens: 2450
RER: (0.88 * 100) / (2450 / 1000) = 35.9
```

---

## ✅ Checklist de Implementação

- [ ] Implementar classe `ThoughtNode` com atributos completos
- [ ] Criar `TreeOfThoughts` com métodos de adição e busca
- [ ] Implementar `GraphOfThoughts` com múltiplos pais
- [ ] Criar estratégias de pontuação (heurística + LLM)
- [ ] Implementar `BeamSearchStrategy` com poda
- [ ] Implementar `BestFirstSearchStrategy` com priority queue
- [ ] Criar `TreeOfThoughtsEngine` herdando de `RecursiveThinkingEngine`
- [ ] Criar `GraphOfThoughtsEngine` com fusão de branches
- [ ] Adicionar logging de raciocínio em cada iteração
- [ ] Implementar método `get_solution_path()` para trace
- [ ] Testes unitários para cada componente
- [ ] Testes de integração com LLM provider
- [ ] Benchmark comparando ToT vs GoT vs Self-Refine
- [ ] Documentação de casos de uso

---

## 🔗 Referências Cruzadas

- **00-ARQUITETURA-BACKEND.md**: RecursionRouter que despacha para ToT/GoT
- **01-ENGINES-IMPLEMENTACAO.md**: Base class RecursiveThinkingEngine e RecursionConfig
- **02-SELF-REFINE-ENGINE.md**: Estratégia alternativa de raciocínio
- **04-MCTS-ENGINE.md**: MCTS como evolução de beam search
- **10-WEBSOCKET-PROTOCOL.md**: Broadcasting de progresso durante Tree construction
- **13-API-REFERENCE.md**: POST /recursion/execute com `technique: 'tot'` ou `'got'`
- **14-TESTING-STRATEGY.md**: E2E tests para raciocínio multi-iteração

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
