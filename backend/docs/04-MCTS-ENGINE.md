# 04 - Monte Carlo Tree Search (MCTS) Engine

## 🎯 Objetivo

Documentar a implementação de **Monte Carlo Tree Search (MCTS)**, um dos algoritmos mais sofisticados para raciocínio recursivo. MCTS combina:
- **Exploração balanceada** via fórmula UCB1 (Upper Confidence Bound)
- **Simulações aleatórias** para avaliar promessa de caminhos
- **Backpropagation** para atualizar estatísticas
- **Seleção adaptativa** que equilibra exploração vs exploração

Este documento fornece:
- Algoritmo MCTS completo com fórmula UCB1
- Implementação de rollout policy (simulação aleatória)
- Arquitetura de nós MCTS com estatísticas
- Estratégias de seleção, expansão e backup
- Exemplos práticos com trace de execução
- Integração com `RecursiveThinkingEngine`

---

## 📐 Conceitos Fundamentais

### O que é MCTS?

Monte Carlo Tree Search é um algoritmo de busca que usa **simulações aleatórias** para avaliar a qualidade de nós. Diferente de ToT que pondera nós com heurísticas, MCTS:

1. **Seleciona** nó promissor usando UCB1
2. **Expande** novo nó filho
3. **Simula** (rollout) um caminho aleatório a partir do novo nó
4. **Retorna** resultado da simulação
5. **Backpropaga** resultado acima na árvore

```
                    [Raiz: Pergunta]
                          |
                __________|__________
               /          |          \
           [1]Node    [2]Node    [3]Node
          (vis:5)    (vis:3)    (vis:2)
          (wins:3)   (wins:1)   (wins:0)
                        |
                   [Expande novo nó]
                        |
                   [Simula aleatório]
                        |
                   [Resultado: 1 ou 0]
                        |
                   [Backpropaga para cima]
```

### Fórmula UCB1

A seleção de qual nó explorar é guiada por **UCB1 (Upper Confidence Bound)**:

```
UCB1(v) = (Q(v) / N(v)) + C * sqrt(ln(N(parent)) / N(v))
          └─────┬─────┘   └──────────┬──────────┘
            exploitation          exploration
```

Onde:
- **Q(v)**: Soma de rewards obtidos do nó v
- **N(v)**: Número de visitas ao nó v
- **N(parent)**: Número de visitas ao nó pai
- **C**: Constante de exploração (tipicamente √2 ≈ 1.414)

---

## 🏗️ Arquitetura: Nós e Estruturas MCTS

### 1. Classe MCTSNode

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import math

@dataclass
class MCTSNode:
    """
    Nó específico para MCTS contendo estatísticas de visita e recompensa.
    
    Atributos:
        node_id: Identificador único
        content: Texto do pensamento
        parent_id: ID do nó pai
        children_ids: IDs dos filhos
        visits: Número de vezes que este nó foi visitado
        value: Soma acumulada de rewards (wins em range 0-1)
        depth: Profundidade na árvore
        tokens_used: Tokens gastos
        metadata: Informações adicionais
    """
    node_id: str
    content: str
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    visits: int = 0
    value: float = 0.0  # Q(v) na fórmula UCB1
    depth: int = 0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def average_value(self) -> float:
        """Retorna média de rewards = Q(v) / N(v)."""
        if self.visits == 0:
            return 0.0
        return self.value / self.visits
    
    def update(self, reward: float) -> None:
        """
        Atualiza o nó com um novo reward (backpropagation step).
        
        Args:
            reward: Valor entre 0-1 representando qualidade
        """
        self.visits += 1
        self.value += reward
    
    def ucb1_score(self, parent_visits: int, exploration_constant: float = math.sqrt(2)) -> float:
        """
        Calcula score UCB1 para seleção.
        
        Args:
            parent_visits: Número de visitas do nó pai
            exploration_constant: C na fórmula (padrão: √2)
            
        Returns:
            Score UCB1
        """
        if self.visits == 0:
            return float('inf')  # Nós não visitados têm prioridade máxima
        
        exploitation = self.value / self.visits
        exploration = exploration_constant * math.sqrt(math.log(parent_visits) / self.visits)
        
        return exploitation + exploration
    
    def is_fully_expanded(self, num_legal_moves: int) -> bool:
        """
        Verifica se todas as ações possíveis (filhos) foram expandidas.
        
        Args:
            num_legal_moves: Número total de movimentos possíveis
            
        Returns:
            True se len(children) == num_legal_moves
        """
        return len(self.children_ids) >= num_legal_moves
```

### 2. Classe MCTS Tree

```python
class MCTSTree:
    """
    Estrutura que representa uma árvore MCTS.
    Gerencia nós, seleção UCB1, expansão e backpropagation.
    """
    
    def __init__(
        self,
        root_content: str,
        max_depth: int = 10,
        exploration_constant: float = math.sqrt(2),
        max_children: int = 5
    ):
        """
        Args:
            root_content: Conteúdo do nó raiz
            max_depth: Profundidade máxima
            exploration_constant: C para UCB1
            max_children: Número máximo de filhos por nó
        """
        self.max_depth = max_depth
        self.exploration_constant = exploration_constant
        self.max_children = max_children
        
        self.nodes: Dict[str, MCTSNode] = {}
        self.root_id = self._create_node(root_content, depth=0)
        
        # Histórico de simulações para análise
        self.simulation_history: List[Dict] = []
    
    def _create_node(
        self,
        content: str,
        depth: int,
        parent_id: Optional[str] = None
    ) -> str:
        """Cria e registra um novo nó."""
        node_id = f"mcts_node_{depth}_{len(self.nodes)}"
        
        node = MCTSNode(
            node_id=node_id,
            content=content,
            parent_id=parent_id,
            depth=depth
        )
        
        self.nodes[node_id] = node
        
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children_ids.append(node_id)
        
        return node_id
    
    def select(self) -> str:
        """
        Fase 1 - SELEÇÃO: Navega da raiz usando UCB1 até nó folha.
        
        Returns:
            node_id do nó selecionado (não totalmente expandido)
        """
        current_id = self.root_id
        
        while True:
            current = self.nodes[current_id]
            
            # Se nó não está totalmente expandido, retornar para expansão
            if not current.is_fully_expanded(self.max_children):
                return current_id
            
            # Se nó é folha e profundidade limite atingida, retornar
            if current.depth >= self.max_depth:
                return current_id
            
            # Selecionar melhor filho usando UCB1
            if not current.children_ids:
                return current_id
            
            best_child = max(
                current.children_ids,
                key=lambda child_id: self.nodes[child_id].ucb1_score(
                    parent_visits=current.visits,
                    exploration_constant=self.exploration_constant
                )
            )
            
            current_id = best_child
        
        return current_id
    
    def expand(self, node_id: str, new_children: List[Dict]) -> str:
        """
        Fase 2 - EXPANSÃO: Cria um novo nó filho do selecionado.
        
        Args:
            node_id: ID do nó a expandir
            new_children: Lista de candidatos (novo nó selecionado aleatoriamente)
            
        Returns:
            node_id do novo nó criado
        """
        parent = self.nodes[node_id]
        
        # Selecionar aleatoriamente qual candidato expandir
        import random
        selected_child = random.choice(new_children)
        
        new_node_id = self._create_node(
            content=selected_child.get('content', ''),
            depth=parent.depth + 1,
            parent_id=node_id
        )
        
        return new_node_id
    
    def backpropagate(self, node_id: str, reward: float) -> None:
        """
        Fase 4 - BACKPROPAGAÇÃO: Propaga reward para cima na árvore.
        
        Args:
            node_id: ID do nó inicial (folha)
            reward: Valor do reward (0-1)
        """
        current_id = node_id
        
        while current_id:
            current = self.nodes[current_id]
            current.update(reward)
            
            # Mover para pai
            current_id = current.parent_id
    
    def get_best_child(self) -> str:
        """
        Retorna o filho com maior valor médio (melhor performance).
        Usado ao final para selecionar melhor resultado.
        
        Returns:
            node_id do melhor filho da raiz
        """
        root = self.nodes[self.root_id]
        
        if not root.children_ids:
            return self.root_id
        
        # Selecionar por valor MÉDIO, não UCB1 (sem exploração)
        best_child = max(
            root.children_ids,
            key=lambda child_id: self.nodes[child_id].average_value
        )
        
        return best_child
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas da árvore."""
        all_visits = sum(n.visits for n in self.nodes.values())
        all_value = sum(n.value for n in self.nodes.values())
        
        return {
            'total_nodes': len(self.nodes),
            'total_visits': all_visits,
            'total_value': all_value,
            'average_node_visits': all_visits / len(self.nodes) if self.nodes else 0,
            'root_visits': self.nodes[self.root_id].visits,
            'root_value': self.nodes[self.root_id].value,
            'root_average': self.nodes[self.root_id].average_value
        }
```

---

## 🎲 Rollout Policy (Estratégia de Simulação)

A **rollout policy** define como simular um caminho aleatório a partir de um nó. Existem várias estratégias:

### 1. Random Rollout (Simulação Completamente Aleatória)

```python
class RandomRolloutPolicy:
    """
    Política de rollout que gera movimentos completamente aleatórios.
    Implementação básica mas rápida.
    """
    
    def __init__(self, llm_provider, max_rollout_depth: int = 5):
        self.llm_provider = llm_provider
        self.max_rollout_depth = max_rollout_depth
    
    def rollout(
        self,
        initial_content: str,
        original_question: str,
        depth: int = 0
    ) -> float:
        """
        Executa um rollout aleatório a partir de um conteúdo inicial.
        
        Args:
            initial_content: Pensamento atual
            original_question: Pergunta original (contexto)
            depth: Profundidade atual (para limitar recursão)
            
        Returns:
            Reward entre 0-1 representando qualidade do caminho
        """
        import random
        
        if depth >= self.max_rollout_depth:
            # Avaliar conteúdo final
            return self._evaluate_final(initial_content, original_question)
        
        # Gerar 3 próximos passos aleatórios
        next_steps = self._generate_random_steps(initial_content, original_question)
        
        if not next_steps:
            return self._evaluate_final(initial_content, original_question)
        
        # Selecionar aleatoriamente qual seguir
        selected_step = random.choice(next_steps)
        
        # Recursivamente continuar rollout
        return self.rollout(
            selected_step['content'],
            original_question,
            depth + 1
        )
    
    def _generate_random_steps(self, content: str, question: str) -> List[Dict]:
        """Gera próximos passos possíveis."""
        prompt = f"""
Dado o seguinte contexto, gere 3 próximos passos DIFERENTES de raciocínio.

PERGUNTA: {question}
CONTEXTO ATUAL: {content}

Retorne apenas os 3 passos, um por linha.
"""
        
        response = self.llm_provider.call(prompt=prompt, temperature=0.8, max_tokens=300)
        
        steps = []
        for line in response.split('\n'):
            if line.strip():
                steps.append({'content': line.strip()})
        
        return steps
    
    def _evaluate_final(self, content: str, question: str) -> float:
        """
        Avalia a qualidade final de um pensamento.
        
        Returns:
            Score 0-1
        """
        evaluation_prompt = f"""
Avalie se o seguinte pensamento adequadamente responde a pergunta original.

PERGUNTA: {question}
RESPOSTA: {content}

Responda com um número entre 0 e 1 (ex: 0.75).
Retorne apenas o número.
"""
        
        response = self.llm_provider.call(
            prompt=evaluation_prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            return float(response.strip())
        except:
            return 0.5
```

### 2. Intelligent Rollout (Simulação Guiada)

```python
class IntelligentRolloutPolicy:
    """
    Rollout que usa heurísticas para guiar simulação,
    combinando aleatoriedade com inteligência.
    """
    
    def __init__(self, llm_provider, max_rollout_depth: int = 5):
        self.llm_provider = llm_provider
        self.max_rollout_depth = max_rollout_depth
    
    def rollout(
        self,
        initial_content: str,
        original_question: str,
        depth: int = 0,
        temperature: float = 0.7
    ) -> float:
        """Rollout com heurísticas de qualidade."""
        
        if depth >= self.max_rollout_depth:
            return self._evaluate_with_reasoning(initial_content, original_question)
        
        # Gerar próximos passos com scores
        candidates = self._generate_scored_steps(initial_content, original_question)
        
        if not candidates:
            return self._evaluate_with_reasoning(initial_content, original_question)
        
        # Seleção probabilística: maiores scores = maior chance
        import random
        weights = [c['score'] for c in candidates]
        selected = random.choices(candidates, weights=weights, k=1)[0]
        
        # Continuar rollout
        return self.rollout(
            selected['content'],
            original_question,
            depth + 1,
            temperature
        )
    
    def _generate_scored_steps(self, content: str, question: str) -> List[Dict]:
        """Gera próximos passos COM scores de qualidade."""
        prompt = f"""
Gere 5 próximos passos possíveis de raciocínio e score cada um.

PERGUNTA: {question}
CONTEXTO: {content}

Para cada passo, fornece:
1. Passo: [texto]
2. Score: [0-1]

Formato:
Passo 1: [texto] | Score: 0.8
Passo 2: [texto] | Score: 0.6
...
"""
        
        response = self.llm_provider.call(prompt=prompt, temperature=0.5, max_tokens=400)
        
        candidates = []
        for line in response.split('\n'):
            if 'Score:' in line:
                try:
                    parts = line.split('|')
                    step_text = parts[0].split(':', 1)[1].strip()
                    score = float(parts[1].split(':')[1].strip())
                    candidates.append({'content': step_text, 'score': score})
                except:
                    pass
        
        return candidates
    
    def _evaluate_with_reasoning(self, content: str, question: str) -> float:
        """Avalia com raciocínio detalhado."""
        eval_prompt = f"""
Avalie se o pensamento abaixo responde bem à pergunta.
Considere: clareza, completude, correção lógica.

PERGUNTA: {question}
PENSAMENTO: {content}

Responda em JSON:
{{
    "score": 0.0-1.0,
    "reasoning": "explicação breve"
}}

Retorne apenas o JSON.
"""
        
        response = self.llm_provider.call(prompt=eval_prompt, temperature=0.0, max_tokens=200)
        
        import json
        try:
            result = json.loads(response)
            return result.get('score', 0.5)
        except:
            return 0.5
```

---

## 🎯 MCTS Engine - Implementação Completa

```python
from typing import Callable, Dict, Any, Tuple
import random
import math

class MCTSEngine(RecursiveThinkingEngine):
    """
    Implementa Monte Carlo Tree Search como RecursiveThinkingEngine.
    
    Ciclo MCTS (4 fases):
    1. SELECTION: Usa UCB1 para navegar até nó não expandido
    2. EXPANSION: Cria um novo nó filho
    3. SIMULATION: Rola aleatoriamente até terminal ou profundidade máxima
    4. BACKPROPAGATION: Propaga resultado para cima
    
    Repete N vezes (num_iterations) e retorna nó com melhor performance média.
    """
    
    def __init__(
        self,
        config: RecursionConfig,
        llm_provider,
        rollout_policy: str = 'intelligent',
        num_simulations: int = 100,
        exploration_constant: float = math.sqrt(2)
    ):
        """
        Args:
            config: RecursionConfig
            llm_provider: Provider LLM
            rollout_policy: 'random' ou 'intelligent'
            num_simulations: Número de simulações MCTS a rodar
            exploration_constant: C para fórmula UCB1
        """
        super().__init__(config)
        self.llm_provider = llm_provider
        
        self.tree = MCTSTree(
            root_content=config.initial_prompt,
            max_depth=config.max_iterations,
            exploration_constant=exploration_constant
        )
        
        # Selecionar rollout policy
        if rollout_policy == 'random':
            self.rollout_policy = RandomRolloutPolicy(llm_provider)
        else:
            self.rollout_policy = IntelligentRolloutPolicy(llm_provider)
        
        self.num_simulations = num_simulations
    
    def _generate_candidates(self, parent_thought: str, num_candidates: int = 5) -> List[Dict]:
        """
        Gera candidatos para expansão MCTS.
        
        Args:
            parent_thought: Conteúdo do nó pai
            num_candidates: Número de candidatos
            
        Returns:
            Lista de candidatos
        """
        prompt = f"""
Gere {num_candidates} DIFERENTES e CRIATIVAS continuações de raciocínio.

PERGUNTA: {self.config.initial_prompt}

CONTEXTO ATUAL:
{parent_thought}

Gere {num_candidates} continuações originais que exploram diferentes ângulos.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.8,
            max_tokens=600
        )
        
        candidates = []
        for i, line in enumerate(response.split('\n')):
            if line.strip():
                candidates.append({
                    'content': line.strip(),
                    'reasoning': f'Generated via MCTS expansion',
                    'tokens_used': len(line.split())
                })
        
        return candidates[:num_candidates]
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Tuple[str, float]]:
        """Avalia candidatos (não usado diretamente em MCTS, mas mantido para compatibilidade)."""
        results = []
        for candidate in candidates:
            # MCTS avalia via simulações, não aqui
            results.append((candidate.get('id', ''), 0.5))
        return results
    
    def execute(self) -> RecursionResult:
        """
        Executa o algoritmo MCTS completo.
        
        Procedimento:
        1. Loop num_simulations vezes:
           a. SELECTION: Selecionar nó via UCB1
           b. EXPANSION: Expandir com novo nó
           c. SIMULATION: Rollout aleatório
           d. BACKPROPAGATION: Retornar reward para cima
        2. Retornar nó com melhor average_value
        
        Returns:
            RecursionResult
        """
        from datetime import datetime
        
        start_time = datetime.now()
        total_tokens = 0
        
        try:
            # Executar simulações MCTS
            for sim in range(self.num_simulations):
                # 1. SELECTION
                selected_node_id = self.tree.select()
                selected_node = self.tree.nodes[selected_node_id]
                
                # 2. EXPANSION
                if selected_node.depth < self.tree.max_depth:
                    candidates = self._generate_candidates(selected_node.content)
                    if candidates:
                        new_node_id = self.tree.expand(selected_node_id, candidates)
                    else:
                        new_node_id = selected_node_id
                else:
                    new_node_id = selected_node_id
                
                # 3. SIMULATION (Rollout)
                new_node = self.tree.nodes[new_node_id]
                reward = self.rollout_policy.rollout(
                    new_node.content,
                    self.config.initial_prompt
                )
                
                # 4. BACKPROPAGATION
                self.tree.backpropagate(new_node_id, reward)
                
                # Logging
                if (sim + 1) % 10 == 0:
                    stats = self.tree.get_statistics()
                    print(f"[MCTS Sim {sim+1}/{self.num_simulations}] Nodes: {stats['total_nodes']}, Root visits: {stats['root_visits']}, Avg reward: {stats['root_average']:.3f}")
            
            # Selecionar melhor resultado
            best_node_id = self.tree.get_best_child()
            best_node = self.tree.nodes[best_node_id]
            
            stats = self.tree.get_statistics()
            total_tokens = sum(n.tokens_used for n in self.tree.nodes.values())
            
            return RecursionResult(
                final_answer=best_node.content,
                iterations_count=len(self.tree.nodes),
                tokens_total=total_tokens,
                quality_score=best_node.average_value,
                rer_score=self._calculate_rer(best_node.average_value, total_tokens),
                metadata={
                    'mcts_stats': stats,
                    'best_node_visits': best_node.visits,
                    'best_node_value': best_node.value,
                    'technique': 'mcts',
                    'num_simulations': self.num_simulations,
                    'rollout_policy': self.rollout_policy.__class__.__name__
                }
            )
        
        except Exception as e:
            raise e
    
    def _calculate_rer(self, quality_score: float, tokens_used: int) -> float:
        """Calcula RER (Recursion Efficiency Ratio)."""
        if tokens_used == 0:
            return 0
        return (quality_score * 100) / (tokens_used / 1000)
```

---

## 📊 Exemplo Prático: Resolvendo com MCTS

```
PERGUNTA: "Qual é a melhor linguagem para aprender programação?"

MCTS SIMULATION TRACE:

Simulation 1:
├─ SELECT: Raiz (não expandida)
├─ EXPAND: Novo nó "Python: Sintaxe simples e comunidade grande"
├─ ROLLOUT:
│  ├─ Step 1: "Python útil para data science"
│  ├─ Step 2: "Bibliotecas como pandas são poderosas"
│  ├─ Step 3: "Conclusão: Python excelente para iniciantes"
│  └─ REWARD: 0.82 (resposta bem estruturada)
├─ BACKPROP:
│  ├─ Raiz: visits=1, value=0.82
│  └─ Novo nó: visits=1, value=0.82

Simulation 2:
├─ SELECT: Raiz (1 filho visitado)
├─ EXPAND: Novo nó "JavaScript: Web development focado"
├─ ROLLOUT:
│  ├─ Step 1: "JavaScript roda em navegadores"
│  ├─ Step 2: "Node.js permite backend"
│  ├─ Step 3: "Conclusão: bom para web"
│  └─ REWARD: 0.65 (menos completo para iniciantes)
├─ BACKPROP:
│  ├─ Raiz: visits=2, value=1.47
│  └─ Novo nó: visits=1, value=0.65

Simulation 3:
├─ SELECT: Raiz (seleciona melhor filho via UCB1)
│  UCB1(Python) = 0.82 + 1.414 * sqrt(ln(2)/1) = 0.82 + 1.34 = 2.16
│  UCB1(JS) = 0.65 + 1.414 * sqrt(ln(2)/1) = 0.65 + 1.34 = 1.99
│  → Seleciona Python (maior UCB1)
├─ EXPAND: Novo nó filho de Python
├─ ROLLOUT: ...
└─ BACKPROP: ...

... (continua até 100 simulações) ...

RESULTADO FINAL (após 100 simulações):
- Python node: visits=35, value=27.5, avg=0.786
- JavaScript node: visits=25, value=15.0, avg=0.600
- Java node: visits=20, value=13.2, avg=0.660
- Go node: visits=15, value=8.4, avg=0.560
- C++ node: visits=5, value=1.8, avg=0.360

MELHOR: Python (avg value = 0.786)
Resposta Final: "Python é a melhor linguagem para aprender..."
```

---

## 🔄 Comparação: MCTS vs ToT vs Self-Refine

```
┌────────────────┬──────────────┬──────────────┬───────────────┐
│ Aspecto        │ Self-Refine  │ ToT          │ MCTS          │
├────────────────┼──────────────┼──────────────┼───────────────┤
│ Estratégia     │ Iterativo    │ Beam search  │ Simulações    │
│ Avaliação      │ Heurística   │ Híbrida      │ Monte Carlo   │
│ Exploração     │ Linear       │ Determinístico│ Aleatória     │
│ Tempo          │ Rápido       │ Médio        │ Lento         │
│ Qualidade      │ Boa          │ Muito boa    │ Excelente     │
│ Melhor para    │ Refino       │ Decisão      │ Exploração    │
│ UCB1           │ Não          │ Não          │ Sim           │
│ Tokens         │ Médio        │ Alto         │ Muito alto    │
│ Escalabilidade │ Excelente    │ Boa          │ Limitada      │
└────────────────┴──────────────┴──────────────┴───────────────┘
```

---

## ✅ Checklist de Implementação

- [ ] Implementar classe `MCTSNode` com visits, value, UCB1
- [ ] Criar `MCTSTree` com operações select, expand, backpropagate
- [ ] Implementar `RandomRolloutPolicy` com geração aleatória
- [ ] Implementar `IntelligentRolloutPolicy` com heurísticas
- [ ] Criar `MCTSEngine` com ciclo completo MCTS
- [ ] Testar cada fase separadamente (select, expand, sim, backprop)
- [ ] Benchmark: MCTS vs ToT vs Self-Refine
- [ ] Otimizar UCB1 para diferentes dominios
- [ ] Implementar pruning de nós com visitação muito baixa
- [ ] Parallelizar simulações (múltiplas threads)
- [ ] Adicionar logging detalhado de raciocínio
- [ ] Documentar casos de uso ideais para MCTS
- [ ] Testes de stress com 1000+ simulações

---

## 🔗 Referências Cruzadas

- **00-ARQUITETURA-BACKEND.md**: RecursionRouter dispatcher
- **01-ENGINES-IMPLEMENTACAO.md**: Base class RecursiveThinkingEngine
- **02-SELF-REFINE-ENGINE.md**: Estratégia alternativa
- **03-TOT-GOT-ENGINES.md**: BeamSearch que MCTS aproveita
- **06-ALIGNMENT-ENGINE.md**: Verificação de resultados MCTS
- **10-WEBSOCKET-PROTOCOL.md**: Streaming de simulações MCTS
- **14-TESTING-STRATEGY.md**: Load testing com MCTS

---

**Documento criado**: 2025
**Versão**: 1.0
**Status**: Completo e pronto para implementação
