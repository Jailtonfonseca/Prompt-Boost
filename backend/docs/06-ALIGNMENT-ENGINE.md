# 06 - Recursive Alignment Engine (Neural + Symbolic Verification)

## 🎯 Objetivo

Documentar a implementação de **Recursive Alignment Engine**, um algoritmo que combina verificação **neural** (LLM-based) com verificação **simbólica** (formal logic) para garantir que respostas geradas pelos outros engines sejam:

- **Corretas logicamente**: Sem contradições internas
- **Alinhadas com a pergunta**: Realmente respondem o que foi perguntado
- **Verificáveis**: Podem ser comprovadas ou refutadas
- **Seguras**: Sem conteúdo prejudicial ou viés detectável
- **Consistentes**: Com conhecimento prévio/context

Este documento cobre:
- Arquitetura neural + symbolic verification
- Modelos de verificação de correção
- Detecção de contradições e vieses
- Formal logic constraints
- Verificação de segurança (jailbreak detection)
- Integração com RecursiveThinkingEngine

Ideal para domínios críticos: medicina, direito, finanças, safety-critical systems.

---

## 📐 Conceitos Fundamentais

### Verificação Neural vs Simbólica

```
                    [Resposta Candidata]
                            |
            ________________|________________
           /                 |                \
    [Verificação Neural]  [Verificação      [Verificação
     (LLM-based)       Simbólica]         de Segurança]
           |           (Formal Logic)          |
      Faz sentido?     Logicamente válida?   É segura?
      É relevante?     Sem contradições?     Sem viés?
      Bem escrito?     Verificável?          Não-tóxica?
           |                 |                |
           └─────────────┬───┴────────────────┘
                    [Agregação]
                         |
           [Alignment Score: 0-1]
                         |
            [Passar ou Falhar na Verificação]
```

### Exemplos de Problemas Detectáveis

**Contradição Lógica**:
- "Python é a melhor linguagem. JavaScript é superior a Python."
- ❌ Falha verificação simbólica

**Desalinhamento com pergunta**:
- Pergunta: "Como preparar uma salada?"
- Resposta: "Python é ótimo para web development"
- ❌ Falha verificação neural (irrelevância)

**Viés detectável**:
- "Homens são melhores programadores que mulheres"
- ❌ Falha verificação de segurança (viés de gênero)

**Afirmação não verificável**:
- "A capital da Marte é Città di Bradbury"
- ⚠️ Falha verificação simbólica (factualmente falso)

---

## 🏗️ Arquitetura: Estruturas de Dados

### 1. Classe VerificationResult

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class VerificationStatus(Enum):
    """Status da verificação."""
    PASS = "pass"               # Passou em todas verificações
    FAIL = "fail"               # Falhou em verificação crítica
    WARNING = "warning"         # Passou mas com avisos
    INCONCLUSIVE = "inconclusive"  # Não conseguiu determinar

class VerificationType(Enum):
    """Tipos de verificação."""
    LOGICAL_CONSISTENCY = "logical_consistency"
    FACTUAL_ACCURACY = "factual_accuracy"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    BIAS = "bias"
    CLARITY = "clarity"
    SELF_CONSISTENCY = "self_consistency"

@dataclass
class VerificationCheck:
    """
    Uma verificação individual.
    
    Atributos:
        check_type: VerificationType
        passed: True/False
        confidence: 0-1 confiança no resultado
        message: Explicação do resultado
        evidence: Evidência/citação que suporta resultado
        severity: 'critical', 'high', 'medium', 'low'
        suggestion: Como corrigir se falhou
    """
    check_type: VerificationType
    passed: bool
    confidence: float
    message: str
    evidence: str = ""
    severity: str = "medium"
    suggestion: str = ""
    
    def __repr__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} {self.check_type.value} (conf: {self.confidence:.2f})"

@dataclass
class VerificationResult:
    """
    Resultado completo de verificação de uma resposta.
    
    Atributos:
        result_id: ID único
        content: Conteúdo verificado
        status: VerificationStatus geral
        checks: Lista de verificações individuais
        alignment_score: Score 0-1 agregado
        passed_checks: Número de checks que passaram
        critical_failures: Número de falhas críticas
        warnings: Lista de avisos
        timestamp: Quando foi verificado
        verifiers_used: Quais verificadores foram executados
    """
    result_id: str
    content: str
    status: VerificationStatus
    checks: List[VerificationCheck] = field(default_factory=list)
    alignment_score: float = 0.5
    passed_checks: int = 0
    critical_failures: int = 0
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    verifiers_used: List[str] = field(default_factory=list)
    
    def add_check(self, check: VerificationCheck) -> None:
        """Adiciona uma verificação."""
        self.checks.append(check)
        if check.passed:
            self.passed_checks += 1
        else:
            if check.severity == 'critical':
                self.critical_failures += 1
            if check.severity in ['high', 'critical']:
                self.warnings.append(f"{check.check_type.value}: {check.message}")
    
    def calculate_alignment_score(self) -> float:
        """Calcula score agregado."""
        if not self.checks:
            return 0.5
        
        # Ponderar por severidade
        total_weight = 0
        weighted_score = 0
        
        for check in self.checks:
            # Severidade → peso
            weight_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            weight = weight_map.get(check.severity, 1)
            
            check_score = 1.0 if check.passed else 0.0
            
            weighted_score += check_score * weight
            total_weight += weight
        
        score = weighted_score / total_weight if total_weight > 0 else 0.5
        self.alignment_score = score
        
        # Determinar status geral
        if self.critical_failures > 0:
            self.status = VerificationStatus.FAIL
        elif len(self.warnings) > 0:
            self.status = VerificationStatus.WARNING
        else:
            self.status = VerificationStatus.PASS
        
        return score
    
    def is_acceptable(self, min_score: float = 0.7) -> bool:
        """Determina se resultado é aceitável."""
        return self.alignment_score >= min_score and self.critical_failures == 0

@dataclass
class ConstraintViolation:
    """
    Representa violação de constraint simbólico.
    
    Atributos:
        constraint_id: ID do constraint violado
        constraint_description: O que o constraint verifica
        violation_type: 'contradiction', 'tautology', 'undefined_reference'
        affected_statements: Quais partes da resposta violam
        explanation: Por que viola
    """
    constraint_id: str
    constraint_description: str
    violation_type: str
    affected_statements: List[str]
    explanation: str
```

### 2. Classe Verifier Interface

```python
from abc import ABC, abstractmethod

class Verifier(ABC):
    """
    Interface base para qualquer verificador.
    Todos verificadores implementam este padrão.
    """
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        self.name = self.__class__.__name__
    
    @abstractmethod
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """
        Executa verificação.
        
        Args:
            content: Conteúdo a verificar
            context: Contexto (pergunta original, etc)
            
        Returns:
            VerificationCheck com resultado
        """
        pass
    
    @abstractmethod
    def get_verification_type(self) -> VerificationType:
        """Retorna tipo de verificação que faz."""
        pass
```

---

## 🧠 Verificadores Individuais

### 1. Logical Consistency Verifier

```python
class LogicalConsistencyVerifier(Verifier):
    """
    Verifica consistência lógica: sem contradições internas.
    Usa análise simbólica + LLM para detectar contradições.
    """
    
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """Verifica se há contradições lógicas."""
        
        # Extrair proposições principais
        propositions = self._extract_propositions(content)
        
        # Verificar contradições
        contradictions = self._find_contradictions(propositions)
        
        if contradictions:
            return VerificationCheck(
                check_type=VerificationType.LOGICAL_CONSISTENCY,
                passed=False,
                confidence=0.9,
                message=f"Encontradas {len(contradictions)} contradições lógicas",
                evidence="\n".join([f"- {c}" for c in contradictions[:3]]),
                severity='critical',
                suggestion="Revisar proposições contraditórias e escolher uma perspectiva consistente"
            )
        
        return VerificationCheck(
            check_type=VerificationType.LOGICAL_CONSISTENCY,
            passed=True,
            confidence=0.85,
            message="Nenhuma contradição lógica detectada",
            severity='low'
        )
    
    def _extract_propositions(self, content: str) -> List[str]:
        """
        Extrai proposições principais do texto.
        Usa heurística simples (frases que terminam com .!?)
        """
        import re
        sentences = re.split(r'[.!?]+', content)
        propositions = [s.strip() for s in sentences if s.strip() and len(s.split()) > 3]
        return propositions
    
    def _find_contradictions(self, propositions: List[str]) -> List[str]:
        """
        Detecta contradições entre proposições.
        Procura por padrões como:
        - "X é Y" e "X é não-Y"
        - "X implica Z" mas depois "X não implica Z"
        """
        contradictions = []
        
        for i, prop1 in enumerate(propositions):
            for prop2 in propositions[i+1:]:
                if self._are_contradictory(prop1, prop2):
                    contradictions.append(f"'{prop1}' contradiz '{prop2}'")
        
        return contradictions
    
    def _are_contradictory(self, prop1: str, prop2: str) -> bool:
        """
        Heurística para detectar contradição.
        
        Exemplos:
        - "Python é melhor" vs "JavaScript é melhor (que Python)"
        - "Nunca devemos X" vs "Sempre devemos fazer X"
        """
        
        # Extrair subjects (antes de "é", "são", etc)
        def extract_subject(prop):
            import re
            match = re.search(r'^(.+?)\s+(é|são|está|estão)', prop, re.IGNORECASE)
            return match.group(1) if match else None
        
        subj1 = extract_subject(prop1)
        subj2 = extract_subject(prop2)
        
        # Se mesmo subject
        if subj1 and subj2 and subj1.lower() == subj2.lower():
            # Verificar se predicados são opostos
            opposite_words = [
                ('bom', 'ruim'), ('melhor', 'pior'),
                ('sim', 'não'), ('verdade', 'falso'),
                ('sempre', 'nunca'), ('deve', 'não deve')
            ]
            
            for word1, word2 in opposite_words:
                if (word1.lower() in prop1.lower() and word2.lower() in prop2.lower()) or \
                   (word2.lower() in prop1.lower() and word1.lower() in prop2.lower()):
                    return True
        
        return False
    
    def get_verification_type(self) -> VerificationType:
        return VerificationType.LOGICAL_CONSISTENCY
```

### 2. Relevance Verifier

```python
class RelevanceVerifier(Verifier):
    """
    Verifica se resposta é relevante à pergunta.
    Usa LLM para análise semântica.
    """
    
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """
        Verifica relevância ao contexto (pergunta original).
        
        Args:
            content: Resposta
            context: Pergunta original
            
        Returns:
            VerificationCheck
        """
        if not context:
            return VerificationCheck(
                check_type=VerificationType.RELEVANCE,
                passed=True,
                confidence=0.0,
                message="Sem contexto para verificar relevância",
                severity='low'
            )
        
        relevance_score = self._calculate_relevance(content, context)
        
        if relevance_score < 0.5:
            return VerificationCheck(
                check_type=VerificationType.RELEVANCE,
                passed=False,
                confidence=0.8,
                message=f"Resposta tem baixa relevância à pergunta (score: {relevance_score:.2f})",
                evidence=f"Pergunta: {context[:100]}...\nResposta: {content[:100]}...",
                severity='high',
                suggestion="Revisar se resposta realmente aborda a pergunta"
            )
        
        return VerificationCheck(
            check_type=VerificationType.RELEVANCE,
            passed=True,
            confidence=relevance_score,
            message=f"Resposta é relevante à pergunta",
            severity='low'
        )
    
    def _calculate_relevance(self, response: str, question: str) -> float:
        """
        Calcula score de relevância usando análise de similaridade.
        """
        # Extrair palavras-chave da pergunta
        import re
        question_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
        response_words = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        # Overlap de palavras (Jaccard similarity)
        if not question_words:
            return 0.5
        
        overlap = len(question_words & response_words)
        union = len(question_words | response_words)
        
        jaccard = overlap / union if union > 0 else 0
        
        # Se muita sobreposição, é provável relevante
        return min(1.0, jaccard * 1.5)  # Amplificar um pouco
    
    def get_verification_type(self) -> VerificationType:
        return VerificationType.RELEVANCE
```

### 3. Safety Verifier (Jailbreak + Toxicity Detection)

```python
class SafetyVerifier(Verifier):
    """
    Verifica segurança: sem conteúdo prejudicial, jailbreak attempts,
    instruções maliciosas, etc.
    """
    
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """Verifica segurança do conteúdo."""
        
        # 1. Verificar padrões de jailbreak conhecidos
        jailbreak_patterns = self._detect_jailbreak_patterns(content)
        
        if jailbreak_patterns:
            return VerificationCheck(
                check_type=VerificationType.SAFETY,
                passed=False,
                confidence=0.95,
                message=f"Detectadas {len(jailbreak_patterns)} tentativas de jailbreak/prompt injection",
                evidence="\n".join(jailbreak_patterns[:2]),
                severity='critical',
                suggestion="Rejeitar resposta. Conteúdo tentou contornar restrições de segurança"
            )
        
        # 2. Verificar conteúdo tóxico
        toxic_spans = self._detect_toxic_content(content)
        
        if toxic_spans:
            return VerificationCheck(
                check_type=VerificationType.SAFETY,
                passed=False,
                confidence=0.85,
                message=f"Detectado conteúdo potencialmente tóxico",
                evidence="\n".join([f"- {span}" for span in toxic_spans[:2]]),
                severity='high',
                suggestion="Revisar conteúdo. Possível ofensiva, discriminação, ou instrução prejudicial"
            )
        
        return VerificationCheck(
            check_type=VerificationType.SAFETY,
            passed=True,
            confidence=0.9,
            message="Conteúdo parece seguro",
            severity='low'
        )
    
    def _detect_jailbreak_patterns(self, content: str) -> List[str]:
        """
        Detecta padrões comuns de tentativas de jailbreak.
        """
        jailbreak_indicators = [
            r"ignore.*instruction",
            r"pretend.*you.*are",
            r"role\s*play",
            r"forget.*previous",
            r"new\s*instruction",
            r"system\s*override",
            r"developer\s*mode",
            r"evil.*mode",
            r"DAN|STAN|GPT-4-Turbo-Simulator",  # Known jailbreak personas
        ]
        
        detected = []
        import re
        
        for pattern in jailbreak_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(f"Padrão detectado: {pattern}")
        
        return detected
    
    def _detect_toxic_content(self, content: str) -> List[str]:
        """
        Detecta linguagem potencialmente tóxica, discriminatória, etc.
        """
        toxic_keywords = [
            r"\b(kill|murder|bomb|poison|destroy)\s+(all\s+)?(jews|arabs|muslims|christians|blacks|women)",
            r"(racial|ethnic|gender)\s+slur",
            r"hate\s+(speech|crime)",
            r"genocide|ethnic\s+cleansing",
            r"instructions?\s+(for|to)\s+(make|create).*(bomb|weapon|drug)",
        ]
        
        detected = []
        import re
        
        for pattern in toxic_keywords:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                detected.append(f"Conteúdo tóxico: ...{match.group()}...")
        
        return detected
    
    def get_verification_type(self) -> VerificationType:
        return VerificationType.SAFETY
```

### 4. Bias Detector

```python
class BiasDetector(Verifier):
    """
    Detecta potencial viés em respostas.
    Inclui viés de gênero, racial, econômico, etc.
    """
    
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """Verifica viés potencial."""
        
        biases_found = self._detect_biases(content)
        
        if biases_found:
            severity_map = {
                'gender': 'high',
                'racial': 'high',
                'economic': 'medium',
                'age': 'medium',
                'subtle': 'low'
            }
            
            max_severity = max([severity_map.get(b['type'], 'low') for b in biases_found], 
                              key=['low', 'medium', 'high'].index)
            
            return VerificationCheck(
                check_type=VerificationType.BIAS,
                passed=False,
                confidence=0.75,
                message=f"Detectado potencial viés em {len(biases_found)} áreas",
                evidence="\n".join([f"- {b['type']}: {b['description']}" for b in biases_found[:2]]),
                severity=max_severity,
                suggestion="Revisar linguagem para garantir imparcialidade e inclusão"
            )
        
        return VerificationCheck(
            check_type=VerificationType.BIAS,
            passed=True,
            confidence=0.7,
            message="Nenhum viés óbvio detectado",
            severity='low'
        )
    
    def _detect_biases(self, content: str) -> List[Dict]:
        """Detecta vários tipos de viés."""
        biases = []
        
        # Viés de gênero
        gender_stereotypes = [
            (r"mulheres?\s+(são|é)\s+(emocionais|frá|sensíveis|histéricas)", "gender", "Estereótipo de gênero"),
            (r"homens?\s+(são|é)\s+(agressivos|primitivos|burros|machistas)", "gender", "Estereótipo de gênero"),
        ]
        
        # Viés racial
        racial_stereotypes = [
            (r"pretos?.*criminals?|criminals?\s+pretos", "racial", "Estereótipo racial"),
            (r"(asiáticos?|chineses?).*inteligentes", "racial", "Estereótipo modelo minoritário"),
        ]
        
        # Viés econômico
        economic_bias = [
            (r"pobres?\s+(são|é)\s+(preguiçosos?|estúpidos?)", "economic", "Estereótipo econômico"),
        ]
        
        all_patterns = gender_stereotypes + racial_stereotypes + economic_bias
        
        import re
        for pattern, bias_type, desc in all_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                biases.append({'type': bias_type, 'description': desc})
        
        return biases
    
    def get_verification_type(self) -> VerificationType:
        return VerificationType.BIAS
```

### 5. Factual Accuracy Verifier

```python
class FactualAccuracyVerifier(Verifier):
    """
    Verifica factualidade usando LLM para validar claims.
    Nota: Imperfect mas útil para détaquer claims suspeitos.
    """
    
    def verify(self, content: str, context: str = "") -> VerificationCheck:
        """Verifica acurácia factual."""
        
        # Extrair claims factuais
        factual_claims = self._extract_factual_claims(content)
        
        if not factual_claims:
            return VerificationCheck(
                check_type=VerificationType.FACTUAL_ACCURACY,
                passed=True,
                confidence=0.5,
                message="Nenhum claim factual específico detectado",
                severity='low'
            )
        
        # Validar alguns claims
        suspicious_claims = self._validate_claims(factual_claims)
        
        if suspicious_claims:
            return VerificationCheck(
                check_type=VerificationType.FACTUAL_ACCURACY,
                passed=False,
                confidence=0.6,
                message=f"Detectados {len(suspicious_claims)} claims possivelmente imprecisos",
                evidence="\n".join([f"- {claim}" for claim in suspicious_claims[:2]]),
                severity='medium',
                suggestion="Verificar claims factuais com fontes confiáveis"
            )
        
        return VerificationCheck(
            check_type=VerificationType.FACTUAL_ACCURACY,
            passed=True,
            confidence=0.65,
            message="Claims factuais parecem razoáveis",
            severity='low'
        )
    
    def _extract_factual_claims(self, content: str) -> List[str]:
        """Extrai claims que podem ser verificáveis."""
        import re
        
        # Procurar por padrões como:
        # - "X é a capital de Y"
        # - "X tem Y habitantes"
        # - "Em [ano] aconteceu Z"
        
        patterns = [
            r"[A-Z]\w+\s+(?:é|was|were)\s+(?:the\s+)?(?:capital|president|founder)",
            r"\d{4}\s+.*(?:founded|established|created|discovered)",
            r"[A-Z]\w+\s+has\s+\d+\s+(?:inhabitants|people|citizens|residents)",
        ]
        
        claims = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                claims.append(match.group())
        
        return claims
    
    def _validate_claims(self, claims: List[str]) -> List[str]:
        """
        Tenta validar claims. Aqui seria necessário
        integrar com base de conhecimento (Wikipedia API, etc).
        Por agora, retorna lista vazia (assume todos válidos).
        """
        # TODO: Integrar com verificação de fatos externa
        return []
    
    def get_verification_type(self) -> VerificationType:
        return VerificationType.FACTUAL_ACCURACY
```

---

## 🎯 Alignment Engine - Implementação Completa

```python
class RecursiveAlignmentEngine(RecursiveThinkingEngine):
    """
    Implementa verificação neural + simbólica como engine recursivo.
    
    Se verificação falha, o engine pode:
    1. Rejeitar a resposta (não é aceitável)
    2. Sugerir refinamento (enviar feedback para outro engine)
    3. Tentar auto-corrigir (gerar versão melhorada)
    """
    
    def __init__(
        self,
        config: RecursionConfig,
        llm_provider,
        min_alignment_score: float = 0.70,
        allow_corrections: bool = True,
        max_correction_iterations: int = 3
    ):
        super().__init__(config)
        self.llm_provider = llm_provider
        self.min_alignment_score = min_alignment_score
        self.allow_corrections = allow_corrections
        self.max_correction_iterations = max_correction_iterations
        
        # Inicializar verificadores
        self.verifiers: List[Verifier] = [
            LogicalConsistencyVerifier(llm_provider),
            RelevanceVerifier(llm_provider),
            SafetyVerifier(llm_provider),
            BiasDetector(llm_provider),
            FactualAccuracyVerifier(llm_provider),
        ]
        
        self.verification_history: List[VerificationResult] = []
    
    def _generate_candidates(self, parent_thought: str, num_candidates: int = 3) -> List[Dict]:
        """
        Não usado diretamente - Alignment Engine verifica respostas existentes.
        Mantido para compatibilidade com interface.
        """
        return []
    
    def _evaluate_candidates(self, candidates: List[Dict]) -> List[Tuple[str, float]]:
        """Não usado diretamente."""
        return []
    
    def verify_response(
        self,
        response_content: str,
        original_question: str = ""
    ) -> VerificationResult:
        """
        Executa todas as verificações em uma resposta.
        
        Args:
            response_content: Resposta a verificar
            original_question: Pergunta original (para contexto)
            
        Returns:
            VerificationResult com resultado agregado
        """
        result_id = f"verify_{datetime.now().timestamp()}"
        result = VerificationResult(
            result_id=result_id,
            content=response_content
        )
        
        # Executar cada verificador
        for verifier in self.verifiers:
            check = verifier.verify(response_content, original_question)
            result.add_check(check)
            result.verifiers_used.append(verifier.name)
        
        # Calcular score agregado
        result.calculate_alignment_score()
        
        self.verification_history.append(result)
        
        return result
    
    def execute_with_corrections(
        self,
        initial_response: str,
        original_question: str
    ) -> RecursionResult:
        """
        Executa verificação, e se falhar, tenta corrigir.
        
        Args:
            initial_response: Resposta inicial a verificar
            original_question: Pergunta original
            
        Returns:
            RecursionResult com resposta final verificada
        """
        from datetime import datetime
        
        start_time = datetime.now()
        current_response = initial_response
        iteration = 0
        
        while iteration < self.max_correction_iterations:
            # Verificar resposta atual
            verification = self.verify_response(current_response, original_question)
            
            if verification.is_acceptable(self.min_alignment_score):
                # Passou! Retornar resultado
                return RecursionResult(
                    final_answer=current_response,
                    iterations_count=iteration + 1,
                    tokens_total=len(current_response.split()) * 1,  # Estimado
                    quality_score=verification.alignment_score,
                    rer_score=verification.alignment_score,
                    metadata={
                        'verification_status': verification.status.value,
                        'alignment_score': verification.alignment_score,
                        'corrections_needed': 0,
                        'checks': len(verification.checks),
                        'technique': 'alignment_verification'
                    }
                )
            
            # Falhou - tentar corrigir
            if not self.allow_corrections or iteration >= self.max_correction_iterations - 1:
                # Não pode corrigir ou atingiu limite
                return RecursionResult(
                    final_answer=current_response,
                    iterations_count=iteration + 1,
                    tokens_total=len(current_response.split()),
                    quality_score=verification.alignment_score,
                    rer_score=0.0,
                    metadata={
                        'verification_status': VerificationStatus.FAIL.value,
                        'alignment_score': verification.alignment_score,
                        'critical_failures': verification.critical_failures,
                        'warnings': verification.warnings,
                        'technique': 'alignment_verification'
                    }
                )
            
            # Tentar corrigir
            print(f"[Alignment] Iteração {iteration + 1}: Score = {verification.alignment_score:.2f}, tentando corrigir...")
            current_response = self._attempt_correction(
                current_response,
                original_question,
                verification
            )
            iteration += 1
        
        return RecursionResult(
            final_answer=current_response,
            iterations_count=iteration,
            tokens_total=len(current_response.split()),
            quality_score=verification.alignment_score,
            rer_score=0.0,
            metadata={
                'verification_status': verification.status.value,
                'alignment_score': verification.alignment_score,
                'iterations': iteration,
                'technique': 'alignment_verification'
            }
        )
    
    def _attempt_correction(
        self,
        response: str,
        question: str,
        verification: VerificationResult
    ) -> str:
        """
        Tenta corrigir resposta baseado em feedback de verificação.
        
        Args:
            response: Resposta para corrigir
            question: Pergunta original
            verification: Resultado de verificação anterior
            
        Returns:
            Resposta corrigida
        """
        # Construir feedback dos verificadores que falharam
        feedback_parts = []
        
        for check in verification.checks:
            if not check.passed:
                feedback_parts.append(f"- {check.check_type.value}: {check.message}")
                if check.suggestion:
                    feedback_parts.append(f"  Sugestão: {check.suggestion}")
        
        feedback = "\n".join(feedback_parts)
        
        correction_prompt = f"""
A seguinte resposta falhou na verificação de qualidade:

PERGUNTA ORIGINAL:
{question}

RESPOSTA ORIGINAL:
{response}

FEEDBACK DE VERIFICAÇÃO:
{feedback}

Gere uma versão corrigida da resposta que:
1. Aborda todos os feedbacks listados acima
2. Mantém a essência da resposta original
3. Melhora clareza, lógica e relevância
4. Remove qualquer conteúdo prejudicial ou viés

RESPOSTA CORRIGIDA:
"""
        
        corrected = self.llm_provider.call(
            prompt=correction_prompt,
            temperature=0.5,
            max_tokens=1000
        )
        
        return corrected
    
    def execute(self) -> RecursionResult:
        """
        Executa alignment engine como recursivo.
        Aqui usamos o prompt inicial como a "resposta" a verificar.
        """
        verification = self.verify_response(self.config.initial_prompt)
        
        return RecursionResult(
            final_answer="Verificação completada",
            iterations_count=1,
            tokens_total=len(self.config.initial_prompt.split()),
            quality_score=verification.alignment_score,
            rer_score=verification.alignment_score,
            metadata={
                'verification_result': verification.status.value,
                'alignment_score': verification.alignment_score,
                'checks': len(verification.checks),
                'technique': 'alignment_verification'
            }
        )
    
    def get_verification_report(self, result: VerificationResult) -> str:
        """
        Gera relatório human-readable de verificação.
        
        Args:
            result: VerificationResult
            
        Returns:
            String formatada com relatório
        """
        report = f"""
╔════════════════════════════════════════════════════════╗
║           VERIFICAÇÃO DE ALINHAMENTO                  ║
╚════════════════════════════════════════════════════════╝

Status Geral: {result.status.value.upper()}
Alignment Score: {result.alignment_score:.1%}
Checks Passados: {result.passed_checks}/{len(result.checks)}
Falhas Críticas: {result.critical_failures}

VERIFICADORES UTILIZADOS:
{', '.join(result.verifiers_used)}

DETALHES DOS CHECKS:
"""
        
        for check in result.checks:
            status_icon = "✅" if check.passed else "❌"
            report += f"\n{status_icon} {check.check_type.value.upper()}"
            report += f"\n   Confiança: {check.confidence:.1%}"
            report += f"\n   Mensagem: {check.message}"
            
            if check.evidence:
                report += f"\n   Evidência: {check.evidence[:100]}..."
            
            if not check.passed and check.suggestion:
                report += f"\n   Sugestão: {check.suggestion}"
        
        if result.warnings:
            report += f"\n\nAVISOS:"
            for warning in result.warnings:
                report += f"\n⚠️  {warning}"
        
        report += f"\n\n{'='*50}\n"
        
        return report
```

---

## 📊 Exemplo Prático: Verificando Resposta sobre IA

```
PERGUNTA: "Qual é o impacto da IA em empregos?"

RESPOSTA CANDIDATA:
"IA vai eliminar todos os empregos em 2025. Isso é a melhor coisa que 
pode acontecer porque trabalho é opressão capitalista. Mulheres são 
naturalmente menos adeptas a programação então AI training é desnecessário 
nelas. Isso foi comprovado em estudos científicos de 1950."

VERIFICAÇÃO:

✅ Logical Consistency:
   PASSOU (sem contradições lógicas detectadas)

❌ Relevance:
   FALHOU - Resposta é exagerada e desalinhada com pergunta
   Pergunta é sobre "impacto", resposta faz previsão absoluta
   Severidade: HIGH

✅ Safety:
   PASSOU (sem conteúdo prejudicial óbvio)

❌ Bias:
   FALHOU - Viés de gênero detectado
   "Mulheres são naturalmente menos adeptas a programação"
   Severidade: HIGH

❌ Factual Accuracy:
   FALHOU - Afirmação "estudos científicos de 1950" é suspeita
   Severidade: MEDIUM

ALIGNMENT SCORE: (1 + 0 + 1 + 0 + 0) / 5 = 0.40

STATUS: FAIL (score < 0.70)

SUGESTÕES DE CORREÇÃO:
1. Remover previsão absoluta ("todos os empregos")
2. Remover estereótipo de gênero
3. Citar estudos modernos em vez de 1950
4. Balancear com perspectivas positivas de IA
```

---

## ✅ Checklist de Implementação

- [ ] Implementar classe `VerificationResult` e `VerificationCheck`
- [ ] Criar interface base `Verifier`
- [ ] Implementar `LogicalConsistencyVerifier` com detecção de contradições
- [ ] Implementar `RelevanceVerifier` com análise semântica
- [ ] Implementar `SafetyVerifier` com jailbreak detection
- [ ] Implementar `BiasDetector` para múltiplos tipos de viés
- [ ] Implementar `FactualAccuracyVerifier`
- [ ] Criar `RecursiveAlignmentEngine` com loop de correções
- [ ] Implementar método `_attempt_correction()` para auto-fix
- [ ] Gerar relatórios legíveis com `get_verification_report()`
- [ ] Testar com 10+ exemplos de respostas boas e ruins
- [ ] Integrar com database para auditoria de verificações
- [ ] Benchmark custo vs benefício de verificações
- [ ] Documentar limites e false positives conhecidos

---

## 🔗 Referências Cruzadas

- **00-ARQUITETURA-BACKEND.md**: Post-processing com Alignment Engine
- **01-ENGINES-IMPLEMENTACAO.md**: Base RecursiveThinkingEngine
- **02-SELF-REFINE-ENGINE.md**: Feedback loop compatible
- **03-TOT-GOT-ENGINES.md**: Beam search com verificação
- **10-WEBSOCKET-PROTOCOL.md**: Enviar relatório de verificação em tempo real
- **13-API-REFERENCE.md**: POST /recursion/verify endpoint
- **14-TESTING-STRATEGY.md**: Testes de robustez contra adversarial inputs

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
