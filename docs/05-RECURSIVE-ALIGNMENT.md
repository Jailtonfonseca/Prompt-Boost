# 05 - Recursive Self-Alignment (NSRSA)

## 📖 Visão Geral

**Recursive Self-Alignment (NSRSA)** combina geração neural com verificação simbólica. Apenas raciocínios **formalmente validados** são usados para atualizar próximas iterações.

**Ganho típico**: >90% de validade formal em domínios restritos (matemática, código formal)

**Custo**: Computacionalmente pesado (verificadores simbólicos são lentílentos)

---

## 🔐 Arquitetura: Neural + Simbólico

```
┌──────────────────────────────────────────────┐
│    RECURSIVE SELF-ALIGNMENT LOOP             │
│                                              │
│  1. GENERATE (Neural)                        │
│     └─ LLM gera candidato                   │
│                                              │
│  2. VERIFY (Simbólico)                       │
│     ├─ Parse para lógica formal              │
│     ├─ Verificador (Lean4/Isabelle)          │
│     └─ Retorna: válido/inválido             │
│                                              │
│  3. FEEDBACK (Contraexemplo)                 │
│     └─ Se inválido, gerar contra-exemplo    │
│                                              │
│  4. REFINE (Atualizar com erro formal)       │
│     └─ LLM corrige com base em erro         │
│                                              │
│  5. LOOP                                     │
│     └─ Repetir até válido ou limite         │
└──────────────────────────────────────────────┘
```

---

## 🧠 Pseudocódigo NSRSA

```python
class RecursiveAlignmentEngine(RecursiveThinkingEngine):
    """Recursive Self-Alignment com verificação formal"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Execute NSRSA loop
        
        Args:
            prompt: problema a resolver formalmente
            config: configuração (verifier, etc)
        
        Returns:
            RecursionResult com prova formalmente válida
        """
        
        # Verificador simbólico (Lean4, Isabelle, etc)
        verifier = self._initialize_verifier(
            config.extra_params.get("verifier_type", "lean4"),
            config.extra_params.get("verifier_path", "")
        )
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="recursive_alignment",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config,
            memory_pool={"verification_log": []}
        )
        
        iteration = 0
        is_valid = False
        
        while not self._should_terminate(state, config):
            iteration += 1
            
            # ─────────────────────────────────────
            # STAGE 1: GENERATE (Neural)
            # ─────────────────────────────────────
            
            system_prompt = f"""
Você é um provador de teoremas formal.
Gere uma prova em linguagem formal {config.extra_params.get('target_language', 'Lean4')}.

Estrutura esperada:
- Declaração do teorema
- Definições necessárias
- Prova com passos lógicos
- QED
            """
            
            generated = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt=system_prompt,
                user_prompt=state.current_prompt,
                temperature=0.0,  # Determinístico para código
                max_tokens=2000
            )
            
            # ─────────────────────────────────────
            # STAGE 2: VERIFY (Simbólico)
            # ─────────────────────────────────────
            
            verification_result = verifier.verify(generated)
            
            is_valid = verification_result.is_valid
            error_message = verification_result.error_message
            error_line = verification_result.error_line
            
            state.memory_pool["verification_log"].append({
                "iteration": iteration,
                "is_valid": is_valid,
                "error": error_message
            })
            
            # ─────────────────────────────────────
            # STAGE 3: FEEDBACK (Contraexemplo)
            # ─────────────────────────────────────
            
            if not is_valid:
                feedback = f"""
ERRO DE VERIFICAÇÃO (linha {error_line}):
{error_message}

O código formal não passou na verificação.
Analise o erro e corrija a prova.
                """
            else:
                feedback = "✓ Prova formalmente válida! Completa."
            
            # ─────────────────────────────────────
            # STAGE 4: REFINE (se inválido)
            # ─────────────────────────────────────
            
            if is_valid:
                # Prova encontrada!
                refined = generated
                break
            
            else:
                # Corrigir erro
                refine_prompt = f"""
Prova anterior:
{generated}

Erro encontrado:
{feedback}

Corrija e gere nova versão da prova.
                """
                
                refined = call_model(
                    provider=config.provider,
                    model=config.model,
                    system_prompt=system_prompt,
                    user_prompt=refine_prompt,
                    temperature=0.0,
                    max_tokens=2000
                )
            
            # ─────────────────────────────────────
            # STORE ITERATION
            # ─────────────────────────────────────
            
            iteration_record = IterationRecord(
                iteration_number=iteration,
                timestamp=datetime.now(),
                generated_candidates=[generated, refined],
                evaluation_scores=[
                    1.0 if is_valid else 0.0,
                    0.0  # Será atualizado próxima iteração
                ],
                selected_best=refined,
                feedback_from_critic=feedback,
                refined_prompt=refined,
                tokens_this_iteration=count_tokens(generated + refined),
                duration_ms=verification_result.verify_time_ms,
                extra_data={
                    "is_valid": is_valid,
                    "error_line": error_line,
                    "verification_time_ms": verification_result.verify_time_ms,
                }
            )
            
            state.all_iterations.append(iteration_record)
            state.current_prompt = refined
            state.iteration = iteration
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        result = RecursionResult(
            final_answer=refined if is_valid else "PROVA NÃO ENCONTRADA",
            iterations_count=iteration,
            improvement_percent=0,  # N/A
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=state.all_iterations,
            metadata={
                "technique": "recursive_alignment",
                "is_formally_valid": is_valid,
                "verifier_type": config.extra_params.get("verifier_type"),
                "verification_log": state.memory_pool["verification_log"],
            }
        )
        
        return result
    
    def _initialize_verifier(
        self,
        verifier_type: str,
        verifier_path: str
    ) -> FormalVerifier:
        """Inicializar verificador simbólico"""
        
        if verifier_type == "lean4":
            return Lean4Verifier(verifier_path)
        elif verifier_type == "isabelle":
            return IsabelleVerifier(verifier_path)
        elif verifier_type == "coq":
            return CoqVerifier(verifier_path)
        else:
            raise ValueError(f"Verifier desconhecido: {verifier_type}")
    
    def _should_terminate(
        self,
        state: RecursionState,
        config: RecursionConfig
    ) -> bool:
        """Terminar quando válido ou limite atingido"""
        
        # Parou porque encontrou prova válida
        if state.all_iterations and \
           state.all_iterations[-1].extra_data.get("is_valid"):
            return True
        
        # Limite de iterações
        if state.iteration >= config.max_iterations:
            return True
        
        # Limite de tokens
        if state.tokens_used >= config.max_tokens_total:
            return True
        
        return False
```

---

## 🔧 Verificadores Simbólicos

### Lean4 (Recomendado)

```python
class Lean4Verifier(FormalVerifier):
    """Verificador usando Lean4"""
    
    def __init__(self, lean_path: str = "lean"):
        self.lean_exec = lean_path
    
    def verify(self, proof_code: str) -> VerificationResult:
        """Verificar prova em Lean4"""
        
        # Escrever código em arquivo temporário
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".lean",
            delete=False
        ) as f:
            f.write(proof_code)
            temp_file = f.name
        
        try:
            # Executar verificador
            result = subprocess.run(
                [self.lean_exec, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse resultado
            if result.returncode == 0:
                return VerificationResult(
                    is_valid=True,
                    error_message=None,
                    error_line=None,
                    verify_time_ms=0
                )
            else:
                # Parse erro
                error_msg = result.stderr
                error_line = self._extract_line_number(error_msg)
                
                return VerificationResult(
                    is_valid=False,
                    error_message=error_msg,
                    error_line=error_line,
                    verify_time_ms=result.returncode * 100  # Dummy
                )
        
        finally:
            os.remove(temp_file)
```

---

## 📊 Configuração NSRSA

```python
{
    "technique": "recursive_alignment",
    "provider": "openai",
    "model": "gpt-4o",  # Modelos com raciocínio
    
    "extra_params": {
        # Verificador
        "verifier_type": "lean4",          # "lean4", "isabelle", "coq"
        "verifier_path": "/usr/bin/lean",
        "target_language": "Lean4",
        
        # Estratégia
        "formal_feedback": True,            # Incluir erros formais
        "timeout_per_verification_ms": 30000,
    },
    
    "max_iterations": 10,    # Mais iterações para convergir a prova
    "max_tokens_total": 20000,
    "max_time_ms": 600000    # 10 minutos para provas complexas
}
```

---

## 📈 Métricas

| Métrica | Definição | Alvo |
|---------|-----------|------|
| **Proof Completion Rate** | % de provas completadas | >70% |
| **Avg Iterations to Proof** | Iterações médias | <5 |
| **Formal Validity** | % de provas formalmente válidas | 100% |
| **Token Efficiency** | Tokens/linha de Lean | Minimizar |

---

## 📚 Referências

- Brown et al., "Recursive Reasoning with Formal Verification" (2025)
- Lean 4 Docs: https://lean-lang.org/

**Próximo**: [06-LLM-MCTS.md](./06-LLM-MCTS.md)
