# 05 - Multi-Agent Debate Engine

## 🎯 Objetivo

Documentar a implementação de **Multi-Agent Debate Engine**, um algoritmo onde múltiplos agentes LLM argumentam diferentes perspectivas sobre uma questão, e um juiz avalia e sintetiza suas posições. Este documento cobre:

- **Arquitetura de agentes**: Pro, Con, Judge roles
- **Protocolo de debate**: Rodadas, turnos, regras de fala
- **Estratégias argumentativas**: Geração de argumentos coerentes e contrapostos
- **Síntese de julgamento**: Como o judge integra múltiplas perspectivas
- **Controle de qualidade**: Evitar loops infinitos e argumentos circulares
- **Implementação com RecursiveThinkingEngine**

O debate é ideal para:
- Problemas com múltiplas perspectivas legítimas
- Decisões complexas que precisam pesar trade-offs
- Análise de riscos (pro risks vs con risks)
- Avaliação crítica (defender + atacar ideia)

---

## 📐 Conceitos Fundamentais

### O que é Multi-Agent Debate?

```
                    [Questão Central]
                           |
            _______________|_______________
           /               |               \
        [Pro Agent]  [Con Agent]      [Judge Agent]
           |               |               |
           └───────────┬───┴───────────────┘
                   [Debate Loop]
                       |
                Rodada 1: Pro faz argumento
                Rodada 2: Con refuta Pro
                Rodada 3: Pro contra-refuta Con
                Rodada 4: Judge sintetiza
                       |
              [Próximas rodadas se necessário]
                       |
                  [Resultado Final]
```

### Estrutura de Agentes

**Pro Agent**: Defende a posição afirmativa
- Gera argumentos favoráveis
- Responde objeções
- Fornece evidências

**Con Agent**: Oferece perspectiva crítica
- Gera contraargumentos
- Questiona premissas
- Aponta limitações

**Judge Agent**: Árbitro imparcial
- Avalia qualidade dos argumentos
- Identifica pontos consensuais
- Sintetiza conclusão
- Detecta falácias lógicas

---

## 🏗️ Arquitetura: Estruturas de Dados

### 1. Classe Argumento

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ArgumentType(Enum):
    """Tipos de argumentos no debate."""
    OPENING = "opening"           # Argumento inicial
    RESPONSE = "response"         # Resposta a contraargumento
    COUNTERARGUMENT = "counter"   # Refutação
    EVIDENCE = "evidence"         # Suporte factual
    CLARIFICATION = "clarify"     # Esclarecimento
    CONCESSION = "concede"        # Admissão de ponto válido

@dataclass
class Argument:
    """
    Representa um argumento único no debate.
    
    Atributos:
        argument_id: Identificador único
        agent_role: 'pro', 'con', ou 'judge'
        content: Texto do argumento
        arg_type: ArgumentType
        strength: Score 0-1 da força lógica
        clarity: Score 0-1 da clareza
        evidence_quality: Score 0-1 de suporte factual
        references: Lista de referências citadas
        targets: IDs dos argumentos que refuta/responde
        emotional_appeal: Score 0-1 (0=lógico puro, 1=muito emocional)
        fallacies: Lista de falácias lógicas detectadas
        conceded_points: Pontos reconhecidos como válidos do outro lado
        tokens_used: Tokens para gerar este argumento
        created_at: Timestamp
    """
    argument_id: str
    agent_role: str  # 'pro', 'con', ou 'judge'
    content: str
    arg_type: ArgumentType
    strength: float = 0.5
    clarity: float = 0.5
    evidence_quality: float = 0.0
    references: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)  # Refuta quais argumentos
    emotional_appeal: float = 0.0
    fallacies: List[str] = field(default_factory=list)
    conceded_points: List[str] = field(default_factory=list)
    tokens_used: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def overall_quality(self) -> float:
        """Calcula qualidade geral do argumento."""
        return (
            (self.strength * 0.4) +
            (self.clarity * 0.3) +
            (self.evidence_quality * 0.2) +
            ((1 - self.emotional_appeal) * 0.1)  # Penaliza apelo emocional demais
        )

@dataclass
class DebateRound:
    """
    Representa uma rodada de debate.
    
    Atributos:
        round_number: Número sequencial da rodada
        arguments: Lista de argumentos nesta rodada (em ordem: pro, con, judge)
        topic: Tópico/questão debatida
        summary: Resumo dos pontos principais
        convergence_score: 0-1 indicando se agentes estão chegando a consenso
    """
    round_number: int
    arguments: List[Argument] = field(default_factory=list)
    topic: str = ""
    summary: str = ""
    convergence_score: float = 0.0
    
    def add_argument(self, argument: Argument) -> None:
        """Adiciona argumento à rodada."""
        self.arguments.append(argument)
    
    def get_agent_arguments(self, agent_role: str) -> List[Argument]:
        """Retorna argumentos de um agente específico."""
        return [a for a in self.arguments if a.agent_role == agent_role]

@dataclass
class DebateSession:
    """
    Gerencia uma sessão completa de debate.
    
    Atributos:
        session_id: ID único da sessão
        question: Pergunta central do debate
        rounds: Lista de rodadas completadas
        agents: Dict com configurações dos agentes
        max_rounds: Limite de rodadas
        convergence_threshold: Quando parar (convergência)
        total_tokens: Tokens totais usados
    """
    session_id: str
    question: str
    rounds: List[DebateRound] = field(default_factory=list)
    agents: Dict[str, Any] = field(default_factory=dict)  # pro, con, judge configs
    max_rounds: int = 4
    convergence_threshold: float = 0.75
    total_tokens: int = 0
    
    def add_round(self, round_data: DebateRound) -> None:
        """Adiciona uma rodada completada."""
        self.rounds.append(round_data)
    
    def get_current_round_number(self) -> int:
        """Retorna número da próxima rodada."""
        return len(self.rounds) + 1
    
    def get_all_arguments_by_role(self, role: str) -> List[Argument]:
        """Retorna todos argumentos de um agente."""
        all_args = []
        for round_data in self.rounds:
            all_args.extend(round_data.get_agent_arguments(role))
        return all_args
    
    def should_continue_debate(self) -> bool:
        """
        Determina se debate deve continuar.
        Para se: limite de rodadas atingido OU convergência suficiente
        """
        if len(self.rounds) >= self.max_rounds:
            return False
        
        if len(self.rounds) > 0:
            last_round = self.rounds[-1]
            if last_round.convergence_score >= self.convergence_threshold:
                return False
        
        return True
```

---

## 🎤 Implementação dos Agentes

### 1. Pro Agent

```python
class ProAgent:
    """
    Agente que defende a posição afirmativa no debate.
    """
    
    def __init__(self, llm_provider, model: str = "gpt-4"):
        self.llm_provider = llm_provider
        self.model = model
        self.role = "pro"
    
    def generate_opening_argument(self, question: str) -> Argument:
        """
        Gera argumento inicial defendendo a posição.
        
        Args:
            question: Pergunta central
            
        Returns:
            Argumento de abertura
        """
        prompt = f"""
Você está participando de um debate estruturado.
Sua posição é AFIRMATIVA (a favor da proposta).

QUESTÃO: {question}

Gere um argumento de abertura forte, claro e bem estruturado (3-4 parágrafos).
Inclua:
1. Tese principal clara
2. 2-3 razões de suporte
3. Uma evidência ou exemplo
4. Conclusão de fortalecimento

Mantenha tom profissional e lógico.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.6,
            max_tokens=800
        )
        
        return Argument(
            argument_id=f"pro_arg_{datetime.now().timestamp()}",
            agent_role=self.role,
            content=response,
            arg_type=ArgumentType.OPENING,
            strength=0.7,
            clarity=0.75,
            evidence_quality=0.5,
            tokens_used=len(response.split())
        )
    
    def generate_response(
        self,
        question: str,
        con_argument: Argument,
        previous_pro_args: List[Argument]
    ) -> Argument:
        """
        Gera resposta aos argumentos do Con.
        
        Args:
            question: Pergunta central
            con_argument: Argumento do Con a responder
            previous_pro_args: Argumentos anteriores do Pro (para consistência)
            
        Returns:
            Argumento de resposta
        """
        # Resumir argumentos anteriores para contexto
        pro_summary = "\n".join([
            f"- {arg.content[:200]}..." for arg in previous_pro_args[-2:]
        ])
        
        prompt = f"""
Você está em um debate estruturado defendendo a posição AFIRMATIVA.

QUESTÃO: {question}

SEU ARGUMENTO ANTERIOR:
{pro_summary}

ARGUMENTO DO OPONENTE (a refutar):
{con_argument.content}

Gere uma resposta que:
1. Reconheça a objeção de forma justa
2. Identifique premissas questionáveis no argumento do oponente
3. Defenda sua posição com novo raciocínio
4. Ofereça evidência ou exemplo específico

Use lógica clara. Evite apelo emocional.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.6,
            max_tokens=800
        )
        
        return Argument(
            argument_id=f"pro_arg_{datetime.now().timestamp()}",
            agent_role=self.role,
            content=response,
            arg_type=ArgumentType.RESPONSE,
            strength=0.65,
            clarity=0.7,
            evidence_quality=0.4,
            targets=[con_argument.argument_id],
            tokens_used=len(response.split())
        )
    
    def identify_con_weaknesses(self, con_argument: Argument) -> List[str]:
        """
        Identifica pontos fracos no argumento do Con.
        
        Args:
            con_argument: Argumento a analisar
            
        Returns:
            Lista de pontos fracos identificados
        """
        prompt = f"""
Analise o seguinte argumento e identifique 3-5 pontos fracos ou falácias lógicas.

ARGUMENTO:
{con_argument.content}

Retorne lista de:
1. Falácia lógica ou ponto fraco
2. Breve explicação por que é fraco
3. Como poderia ser respondido

Formato:
- Fraqueza 1: [descrição] | Resposta: [como refutar]
- Fraqueza 2: ...
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.5,
            max_tokens=500
        )
        
        weaknesses = []
        for line in response.split('\n'):
            if line.startswith('-'):
                weaknesses.append(line.strip())
        
        return weaknesses
```

### 2. Con Agent

```python
class ConAgent:
    """
    Agente que oferece perspectiva crítica/negativa no debate.
    """
    
    def __init__(self, llm_provider, model: str = "gpt-4"):
        self.llm_provider = llm_provider
        self.model = model
        self.role = "con"
    
    def generate_opening_argument(self, question: str) -> Argument:
        """
        Gera argumento inicial contra a posição.
        
        Args:
            question: Pergunta central
            
        Returns:
            Argumento de abertura
        """
        prompt = f"""
Você está participando de um debate estruturado.
Sua posição é CRÍTICA/NEGATIVA (contra a proposta).

QUESTÃO: {question}

Gere um argumento de abertura forte, questionando a posição afirmativa.
Inclua:
1. Tese de oposição clara
2. 2-3 objeções principais
3. Um exemplo ou cenário problemático
4. Conclusão

Mantenha tom profissional e lógico. Não seja meramente contraditório.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.6,
            max_tokens=800
        )
        
        return Argument(
            argument_id=f"con_arg_{datetime.now().timestamp()}",
            agent_role=self.role,
            content=response,
            arg_type=ArgumentType.OPENING,
            strength=0.7,
            clarity=0.75,
            evidence_quality=0.5,
            tokens_used=len(response.split())
        )
    
    def refute_argument(
        self,
        question: str,
        pro_argument: Argument,
        previous_con_args: List[Argument]
    ) -> Argument:
        """
        Gera refutação do argumento do Pro.
        
        Args:
            question: Pergunta central
            pro_argument: Argumento do Pro a refutar
            previous_con_args: Argumentos anteriores do Con
            
        Returns:
            Argumento de refutação
        """
        prompt = f"""
Você está debatendo contra a posição AFIRMATIVA.

QUESTÃO: {question}

ARGUMENTO DO OPONENTE (a refutar):
{pro_argument.content}

Gere uma refutação que:
1. Identifique pressupostos não comprovados
2. Aponte consequências negativas não consideradas
3. Ofereça cenário alternativo que questiona a tese
4. Mantenha tom respeitoso mas crítico

Refute com lógica, não com emoção.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.6,
            max_tokens=800
        )
        
        return Argument(
            argument_id=f"con_arg_{datetime.now().timestamp()}",
            agent_role=self.role,
            content=response,
            arg_type=ArgumentType.COUNTERARGUMENT,
            strength=0.65,
            clarity=0.7,
            evidence_quality=0.4,
            targets=[pro_argument.argument_id],
            tokens_used=len(response.split())
        )
    
    def identify_risk_factors(self, pro_proposal: str) -> List[Dict[str, str]]:
        """
        Identifica riscos e problemas potenciais.
        
        Args:
            pro_proposal: Descrição da proposta do Pro
            
        Returns:
            Lista de riscos identificados
        """
        prompt = f"""
Faça uma análise de riscos e problemas da seguinte proposta:

PROPOSTA: {pro_proposal}

Identifique 4-6 riscos potenciais em diferentes categorias:
- Risco econômico
- Risco social
- Risco técnico/operacional
- Risco de implementação
- Risco de efeito colateral

Retorne em JSON:
{{
    "risks": [
        {{"category": "...", "risk": "...", "impact": "alto/médio/baixo"}},
        ...
    ]
}}
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.5,
            max_tokens=600
        )
        
        import json
        try:
            result = json.loads(response)
            return result.get('risks', [])
        except:
            return []
```

### 3. Judge Agent

```python
class JudgeAgent:
    """
    Agente árbitro que avalia argumentos e sintetiza conclusão.
    """
    
    def __init__(self, llm_provider, model: str = "gpt-4"):
        self.llm_provider = llm_provider
        self.model = model
        self.role = "judge"
    
    def evaluate_argument_quality(self, argument: Argument) -> Dict[str, Any]:
        """
        Avalia qualidade de um argumento.
        
        Args:
            argument: Argumento a avaliar
            
        Returns:
            Dict com scores de diferentes dimensões
        """
        prompt = f"""
Avalie objetivamente a qualidade do seguinte argumento em um debate:

ARGUMENTO:
{argument.content}

Avalie em escala 0-1:
1. Clareza: Quão claro e bem estruturado é?
2. Lógica: Há falácias lógicas? Argumentação é válida?
3. Suporte: Usa evidências? Cita fontes?
4. Relevância: Aborda a questão?
5. Impacto: Quão convincente é?

Detecte também:
- Falácias lógicas (lista)
- Premissas não comprovadas
- Generalizações indevidas

Retorne JSON:
{{
    "clarity": 0.0-1.0,
    "logic": 0.0-1.0,
    "support": 0.0-1.0,
    "relevance": 0.0-1.0,
    "impact": 0.0-1.0,
    "fallacies": ["falácia1", "falácia2"],
    "unproven_premises": ["premissa1"],
    "overall_score": 0.0-1.0
}}
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        import json
        try:
            result = json.loads(response)
            # Atualizar argument com scores
            argument.clarity = result.get('clarity', 0.5)
            argument.strength = result.get('logic', 0.5)
            argument.evidence_quality = result.get('support', 0.0)
            argument.fallacies = result.get('fallacies', [])
            return result
        except:
            return {'overall_score': 0.5}
    
    def synthesize_judgment(
        self,
        question: str,
        pro_arguments: List[Argument],
        con_arguments: List[Argument],
        round_num: int = 1
    ) -> Argument:
        """
        Sintetiza argumentos de ambos lados em um julgamento equilibrado.
        
        Args:
            question: Pergunta central
            pro_arguments: Argumentos do Pro (toda sessão)
            con_arguments: Argumentos do Con (toda sessão)
            round_num: Número da rodada
            
        Returns:
            Argumento de síntese/julgamento
        """
        # Resumir pontos principais
        pro_summary = "\n".join([
            f"- {arg.content[:150]}..." for arg in pro_arguments[-2:]
        ])
        con_summary = "\n".join([
            f"- {arg.content[:150]}..." for arg in con_arguments[-2:]
        ])
        
        prompt = f"""
Você é um árbitro neutro sintetizando um debate estruturado.

QUESTÃO: {question}

POSIÇÃO AFIRMATIVA (últimos argumentos):
{pro_summary}

POSIÇÃO CRÍTICA (últimos argumentos):
{con_summary}

Gere uma síntese equilibrada que:
1. Reconheça os pontos mais fortes de AMBOS os lados
2. Identifique consensos e áreas de concordância
3. Aponte as questões ainda em disputa
4. Ofereça uma perspectiva integradora se possível
5. Não tome partido, mas avalie a força dos argumentos

Formato: 4-5 parágrafos, tom neutro e analítico.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1000
        )
        
        return Argument(
            argument_id=f"judge_synthesis_{round_num}",
            agent_role=self.role,
            content=response,
            arg_type=ArgumentType.OPENING,  # Síntese
            tokens_used=len(response.split())
        )
    
    def calculate_convergence_score(
        self,
        pro_arguments: List[Argument],
        con_arguments: List[Argument]
    ) -> float:
        """
        Calcula quanto os argumentos estão convergindo (chegando a consenso).
        
        Args:
            pro_arguments: Argumentos do Pro
            con_arguments: Argumentos do Con
            
        Returns:
            Score 0-1 (1 = total concordância, 0 = total desacordo)
        """
        if not pro_arguments or not con_arguments:
            return 0.0
        
        prompt = f"""
Analise quanto os seguintes argumentos convergem/concordam.

ARGUMENTO A:
{pro_arguments[-1].content}

ARGUMENTO B:
{con_arguments[-1].content}

Retorne um score 0-1 indicando concordância:
- 0: Completo desacordo
- 0.5: Concorda em alguns pontos
- 1: Acordo completo

Retorne apenas o número.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.0,
            max_tokens=10
        )
        
        try:
            return float(response.strip())
        except:
            return 0.5
    
    def generate_final_verdict(
        self,
        question: str,
        all_pro_args: List[Argument],
        all_con_args: List[Argument]
    ) -> Dict[str, Any]:
        """
        Gera veredito final após todas as rodadas.
        
        Args:
            question: Pergunta debatida
            all_pro_args: Todos argumentos do Pro
            all_con_args: Todos argumentos do Con
            
        Returns:
            Dict com veredito estruturado
        """
        pro_summary = "\n".join([
            f"{i+1}. {arg.content[:200]}..." for i, arg in enumerate(all_pro_args)
        ])
        con_summary = "\n".join([
            f"{i+1}. {arg.content[:200]}..." for i, arg in enumerate(all_con_args)
        ])
        
        prompt = f"""
Você é árbitro final em um debate estruturado que foi completo.

QUESTÃO: {question}

ARGUMENTOS AFIRMATIVOS (resumidos):
{pro_summary}

ARGUMENTOS CRÍTICOS (resumidos):
{con_summary}

Fornça um veredito que inclua:
1. RESUMO EXECUTIVO: Qual era a questão, posições
2. FORÇA DOS ARGUMENTOS: Avaliação qualitativa de cada lado
3. PONTOS DE CONSENSO: O que ambos concordam
4. QUESTÕES RESIDUAIS: O que ainda discordam
5. RECOMENDAÇÃO: Qual caminho parece mais prudente/justificado?
6. CONFIANÇA: Score 0-1 em sua recomendação

Retorne em JSON estruturado.
"""
        
        response = self.llm_provider.call(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        import json
        try:
            return json.loads(response)
        except:
            return {
                'summary': response,
                'confidence': 0.5
            }
```

---

## 🎭 Debate Engine - Implementação Completa

```python
class DebateEngine(RecursiveThinkingEngine):
    """
    Implementa debate multi-agente como RecursiveThinkingEngine.
    
    Procedimento:
    1. Inicializar agentes Pro, Con, Judge
    2. Pro gera argumento de abertura
    3. Con gera contraargumento
    4. Judge sintetiza (após rodada 1)
    5. Loop: Pro responde → Con refuta → Judge sintetiza (até max_rounds ou convergência)
    6. Retornar veredito final
    """
    
    def __init__(
        self,
        config: RecursionConfig,
        llm_provider,
        max_rounds: int = 4,
        convergence_threshold: float = 0.75
    ):
        super().__init__(config)
        self.llm_provider = llm_provider
        
        self.pro_agent = ProAgent(llm_provider)
        self.con_agent = ConAgent(llm_provider)
        self.judge_agent = JudgeAgent(llm_provider)
        
        self.session = DebateSession(
            session_id=f"debate_{datetime.now().timestamp()}",
            question=config.initial_prompt,
            max_rounds=max_rounds,
            convergence_threshold=convergence_threshold
        )
    
    def _generate_candidates(self, parent_thought: str, num_candidates: int = 3) -> List[Dict]:
        """Não usado em Debate (agentes geram próprios argumentos)."""
        return []
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Tuple[str, float]]:
        """Não usado em Debate (judge avalia argumentos)."""
        return []
    
    def execute(self) -> RecursionResult:
        """
        Executa o debate completo.
        
        Returns:
            RecursionResult com veredito final
        """
        from datetime import datetime
        
        start_time = datetime.now()
        
        try:
            # RODADA 1: Aberturas
            round1 = DebateRound(round_number=1, topic=self.config.initial_prompt)
            
            # Pro abre
            pro_opening = self.pro_agent.generate_opening_argument(self.config.initial_prompt)
            self.judge_agent.evaluate_argument_quality(pro_opening)
            round1.add_argument(pro_opening)
            
            # Con contrapõe
            con_opening = self.con_agent.generate_opening_argument(self.config.initial_prompt)
            self.judge_agent.evaluate_argument_quality(con_opening)
            round1.add_argument(con_opening)
            
            # Judge sintetiza rodada 1
            judge_synthesis1 = self.judge_agent.synthesize_judgment(
                self.config.initial_prompt,
                [pro_opening],
                [con_opening],
                round_num=1
            )
            round1.add_argument(judge_synthesis1)
            
            # Calcular convergência
            round1.convergence_score = self.judge_agent.calculate_convergence_score(
                [pro_opening],
                [con_opening]
            )
            
            self.session.add_round(round1)
            
            # RODADAS SUBSEQUENTES
            round_num = 2
            while self.session.should_continue_debate():
                round_data = DebateRound(round_number=round_num, topic=self.config.initial_prompt)
                
                # Pro responde
                pro_response = self.pro_agent.generate_response(
                    self.config.initial_prompt,
                    con_opening if round_num == 2 else self.session.get_all_arguments_by_role('con')[-1],
                    self.session.get_all_arguments_by_role('pro')
                )
                self.judge_agent.evaluate_argument_quality(pro_response)
                round_data.add_argument(pro_response)
                
                # Con refuta
                con_refutation = self.con_agent.refute_argument(
                    self.config.initial_prompt,
                    pro_response,
                    self.session.get_all_arguments_by_role('con')
                )
                self.judge_agent.evaluate_argument_quality(con_refutation)
                round_data.add_argument(con_refutation)
                
                # Judge sintetiza
                judge_synthesis = self.judge_agent.synthesize_judgment(
                    self.config.initial_prompt,
                    self.session.get_all_arguments_by_role('pro'),
                    self.session.get_all_arguments_by_role('con'),
                    round_num=round_num
                )
                round_data.add_argument(judge_synthesis)
                
                # Convergência
                round_data.convergence_score = self.judge_agent.calculate_convergence_score(
                    self.session.get_all_arguments_by_role('pro'),
                    self.session.get_all_arguments_by_role('con')
                )
                
                self.session.add_round(round_data)
                round_num += 1
            
            # VEREDITO FINAL
            final_verdict = self.judge_agent.generate_final_verdict(
                self.config.initial_prompt,
                self.session.get_all_arguments_by_role('pro'),
                self.session.get_all_arguments_by_role('con')
            )
            
            # Calcular tokens totais
            total_tokens = sum(
                arg.tokens_used 
                for round_data in self.session.rounds 
                for arg in round_data.arguments
            )
            
            # Extrair resposta final
            final_answer = final_verdict.get('recommendation', 'Debate concludido com consenso parcial')
            quality_score = final_verdict.get('confidence', 0.5)
            
            return RecursionResult(
                final_answer=final_answer,
                iterations_count=len(self.session.rounds),
                tokens_used=total_tokens,
                quality_score=quality_score,
                rer_score=(quality_score * 100) / (total_tokens / 1000) if total_tokens > 0 else 0,
                metadata={
                    'debate_rounds': len(self.session.rounds),
                    'final_verdict': final_verdict,
                    'pro_arguments': len(self.session.get_all_arguments_by_role('pro')),
                    'con_arguments': len(self.session.get_all_arguments_by_role('con')),
                    'technique': 'multi_agent_debate',
                    'convergence_trajectory': [r.convergence_score for r in self.session.rounds]
                }
            )
        
        except Exception as e:
            raise e
```

---

## 📊 Exemplo Prático: Debate sobre IA na Educação

```
QUESTÃO: "Instituições educacionais devem integrar IA como ferramenta principal de ensino?"

RODADA 1:

PRO ARGUMENTO (Abertura):
"A IA oferece personalização em larga escala que seria impossível com professores humanos.
Com IA, cada aluno recebe caminho de aprendizado otimizado para seu ritmo e estilo.
Estudos mostram que aprendizado personalizado melhora retenção em 35%.
IA também reduz carga administrativa, permitindo que professores se concentrem em mentoria."

Scores: Clarity=0.85, Logic=0.8, Support=0.6, Impact=0.75

CON ARGUMENTO (Abertura):
"A educação não é apenas transmissão de conhecimento; é formação de caráter e habilidades sociais.
IA não pode replicar o relacionamento humano essencial para motivação e orientação emocional.
Dependência excessiva de IA criaria geração sem habilidades críticas nem interação social.
Além disso, IA perpetua vieses nos dados de treinamento, prejudicando alunos de comunidades marginalizadas."

Scores: Clarity=0.8, Logic=0.75, Support=0.55, Impact=0.78

JUDGE SÍNTESE (Rodada 1):
"Ambos argumentos tocam em aspectos válidos. Pro enfatiza eficiência e personalização técnica.
Con ressalta importância de desenvolvimento humano integral.
Consenso emergente: IA como FERRAMENTA (não substituto) dentro de currículo balanceado parece prudente.
Ainda em disputa: Como integrar sem perder elementos humanísticos?"

Convergence Score: 0.45

---

RODADA 2:

PRO RESPONDE:
"Concordo que IA não substitui relação humano-humano. Mas meu argumento não era isso.
IA automatiza tarefas repetitivas (correção, revisão), liberando professor para MAIS interação significativa.
Professor passa menos tempo com burocracia, mais tempo orientando alunos emocionalmente.
Assim, IA MELHORA a qualidade do relacionamento humano, não diminui."

Scores: Clarity=0.88, Logic=0.82, Support=0.65, Impact=0.79

CON REFUTA:
"Reconheço ponto válido sobre redução de burocracia. Porém, implementação prática geralmente falha nisso.
Frequentemente, IA reduz investimento em professores porque 'máquinas já ensinam'.
Além disso, adolescentes já viciados em telas não precisam de MAIS interface digital.
Pesquisa recente (2024) mostra declínio em atenção e concentração entre alunos com muita IA."

Scores: Clarity=0.82, Logic=0.78, Support=0.7, Impact=0.76

JUDGE SÍNTESE (Rodada 2):
"Ponto importante emergindo: questão não é IA sim/não, mas COMO implementar responsavelmente.
Pro oferece visão otimista sobre libertação de tempo professoral.
Con oferece cautela realista sobre implementações falhadas e efeitos negativos não intencionais.
Novo consenso: Necessário regulação clara + experimentação controlada antes de escala nacional."

Convergence Score: 0.62

---

RODADA 3 (Abreviada)...

VEREDITO FINAL (do Judge):
{
  "summary": "Debate abordou integração de IA em educação",
  "strength_affirmative": "Eficiência técnica, personalização demonstrada, possível libertação administrativa",
  "strength_critical": "Preservação humanística, riscos psicológicos, histórico de implementações ruins",
  "consensus": "IA em educação é inevitável; questão é como governar responsavelmente",
  "residual_questions": [
    "Quanto IA vs curador humano?",
    "Como garantir equidade?",
    "Impacto psicológico a longo prazo?"
  ],
  "recommendation": "Integração piloto em 5 escolas com supervisão rigorosa, antes de política nacional",
  "confidence": 0.72
}
```

---

## ✅ Checklist de Implementação

- [ ] Implementar classe `Argument` com todas as dimensões de avaliação
- [ ] Criar `DebateRound` e `DebateSession` para organizar debate
- [ ] Implementar `ProAgent` com geração de argumentos coerentes
- [ ] Implementar `ConAgent` com análise de riscos e refutações
- [ ] Implementar `JudgeAgent` com avaliação objetiva e síntese
- [ ] Criar método `_evaluate_argument_quality()` com múltiplas dimensões
- [ ] Implementar `DebateEngine.execute()` com loop de rodadas
- [ ] Adicionar detecção de falácias lógicas
- [ ] Implementar cálculo de convergência score
- [ ] Gerar veredito final estruturado
- [ ] Testar debate com 5+ tópicos diferentes
- [ ] Benchmark qualidade de sínteses vs simplicidade
- [ ] Documentar melhores práticas para argumentação
- [ ] Implementar logging detalhado do debate

---

## 🔗 Referências Cruzadas

- **00-ARQUITETURA-BACKEND.md**: Debate como técnica no RecursionRouter
- **01-ENGINES-IMPLEMENTACAO.md**: Base RecursiveThinkingEngine
- **06-ALIGNMENT-ENGINE.md**: Verificação de consistência de argumentos
- **10-WEBSOCKET-PROTOCOL.md**: Streaming de rodadas de debate em tempo real
- **14-TESTING-STRATEGY.md**: E2E tests para qualidade de debate
- **16-CASOS-DE-USO-BACKEND.md**: Cenário de decisão com múltiplas perspectivas

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
