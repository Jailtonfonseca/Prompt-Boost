# 08 - Autoformalização & Prova Formal

## 📖 Visão Geral

**Autoformalização** combina LLM com verificadores de prova formal (Lean4, Isabelle, Coq). O loop traduz raciocínio natural → formalismo → validação → correção.

**Ganho típico**: 60-85% em teoremas universitários (vs <10% em 2023)

**Melhor para**: Matemática, física formal, código garantido, criptografia

---

## 🔄 Arquitetura Autoformalização

```
┌────────────────────────────────────────────────┐
│         AUTOFORMALIZAÇÃO LOOP                  │
│                                                │
│  NL: "Prove que a soma de pares é par"        │
│         │                                      │
│         ▼                                      │
│  FORMALIZE                                    │
│  ├─ LLM traduz → Lean4:                       │
│  │  theorem sum_even : ∀ a b,                 │
│  │    even a → even b → even (a + b)         │
│  │                                            │
│  └─ Resultado: proof_0.lean                   │
│         │                                      │
│         ▼                                      │
│  VERIFY (Lean4 checker)                       │
│  ├─ Executar: lean proof_0.lean               │
│  └─ Resultado:                                │
│     ❌ error (line 5): "even" not defined    │
│         │                                      │
│         ▼                                      │
│  PROVIDE FEEDBACK                             │
│  └─ Error: "Need to import Even.Basic"       │
│         │                                      │
│         ▼                                      │
│  REFINE (LLM corrige)                         │
│  └─ LLM lê erro e gera prova_1.lean           │
│         │                                      │
│         ▼                                      │
│  Loop até:                                    │
│  └─ ✓ Verificado com sucesso!                │
└────────────────────────────────────────────────┘
```

---

## 🧠 Pseudocódigo Autoformalização

```python
class AutoformalizationEngine(RecursiveThinkingEngine):
    """Autoformalização com verificação de prova"""
    
    def run(
        self,
        prompt: str,
        config: RecursionConfig
    ) -> RecursionResult:
        """
        Execute autoformalização
        
        Args:
            prompt: problema/teorema em linguagem natural
            config: configuração (target_language, etc)
        
        Returns:
            RecursionResult com prova formalizada e validada
        """
        
        target_language = config.extra_params.get(
            "target_language", 
            "lean4"
        )
        
        verifier = self._get_verifier(target_language)
        
        state = RecursionState(
            execution_id=uuid.uuid4(),
            technique="autoformal",
            original_prompt=prompt,
            current_prompt=prompt,
            config=config,
            memory_pool={"verification_log": []}
        )
        
        iteration = 0
        is_valid = False
        formal_proof = ""
        
        while not self._should_terminate(state, config):
            iteration += 1
            
            # ─────────────────────────────────────
            # STAGE 1: FORMALIZE (NL → Formal)
            # ─────────────────────────────────────
            
            system_prompt = f"""
Você é um especialista em conversão de prova para {target_language}.

Tarefa: Traduzir prova de linguagem natural para {target_language}.

Formato esperado:
- Imports necessários
- Definições
- Teorema com asserção
- Prova com tática apropriada

Regras:
- Use `sorry` para partes não resolvidas
- Imports vem no topo
- Use convenções de {target_language}
            """
            
            if iteration == 1:
                user_prompt = f"""
Teorema em linguagem natural:
{prompt}

Formalize em {target_language}:
                """
            else:
                # Iterações subsequentes com feedback
                error_info = state.memory_pool["verification_log"][-1]
                user_prompt = f"""
Prova anterior em {target_language}:
{formal_proof}

Erro encontrado:
{error_info.get('error_message', '')}

Linha problemática:
{formal_proof.split(chr(10))[error_info.get('error_line', 0)]}

Corrija a prova incorporando o feedback:
                """
            
            formal_proof = call_model(
                provider=config.provider,
                model=config.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,  # Determinístico
                max_tokens=2000
            )
            
            # ─────────────────────────────────────
            # STAGE 2: VERIFY (Formal verification)
            # ─────────────────────────────────────
            
            verify_result = verifier.verify(formal_proof)
            
            is_valid = verify_result.is_valid
            error_msg = verify_result.error_message
            error_line = verify_result.error_line
            verify_time = verify_result.verify_time_ms
            
            # Log
            state.memory_pool["verification_log"].append({
                "iteration": iteration,
                "is_valid": is_valid,
                "error_message": error_msg,
                "error_line": error_line,
                "verify_time_ms": verify_time
            })
            
            # ─────────────────────────────────────
            # STAGE 3: FEEDBACK & REFINEMENT
            # ─────────────────────────────────────
            
            if is_valid:
                feedback = "✓ Prova formalmente válida!"
                break
            else:
                feedback = f"""
ERRO VERIFICAÇÃO (linha {error_line}):
{error_msg}

Analise e corrija usando tática apropriada do {target_language}.
                """
            
            # ─────────────────────────────────────
            # STORE ITERATION
            # ─────────────────────────────────────
            
            iteration_record = IterationRecord(
                iteration_number=iteration,
                timestamp=datetime.now(),
                generated_candidates=[formal_proof],
                evaluation_scores=[1.0 if is_valid else 0.0],
                selected_best=formal_proof,
                feedback_from_critic=feedback,
                refined_prompt=formal_proof,
                tokens_this_iteration=count_tokens(formal_proof),
                duration_ms=verify_time,
                extra_data={
                    "is_valid": is_valid,
                    "error_line": error_line,
                    "language": target_language,
                }
            )
            
            state.all_iterations.append(iteration_record)
            state.iteration = iteration
        
        # ─────────────────────────────────────
        # AGGREGATE RESULT
        # ─────────────────────────────────────
        
        if is_valid:
            # Tentar simplificar prova
            simplified = self._try_simplify_proof(
                formal_proof,
                verifier,
                config
            )
            final_proof = simplified if simplified else formal_proof
        else:
            final_proof = formal_proof
        
        result = RecursionResult(
            final_answer=final_proof,
            iterations_count=iteration,
            improvement_percent=100.0 if is_valid else 0.0,
            tokens_total=state.tokens_used,
            time_total_ms=state.compute_time,
            all_iterations=state.all_iterations,
            metadata={
                "technique": "autoformal",
                "is_formally_valid": is_valid,
                "target_language": target_language,
                "verification_log": state.memory_pool["verification_log"],
            }
        )
        
        return result
    
    def _get_verifier(
        self,
        language: str
    ) -> FormalVerifier:
        """Get appropriate verifier"""
        
        verifiers = {
            "lean4": Lean4Verifier(),
            "lean3": Lean3Verifier(),
            "isabelle": IsabelleVerifier(),
            "coq": CoqVerifier(),
        }
        
        return verifiers.get(language, Lean4Verifier())
    
    def _try_simplify_proof(
        self,
        proof: str,
        verifier: FormalVerifier,
        config: RecursionConfig
    ) -> Optional[str]:
        """Tentar simplificar prova mantendo validade"""
        
        simplify_prompt = f"""
Prova {config.extra_params.get('target_language')}:
{proof}

Simplifique mantendo a validade.
Use tática mais elegante ou reduzir linhas.

Prova simplificada:
        """
        
        simplified = call_model(
            provider=config.provider,
            model=config.model,
            system_prompt="Você é otimizador de provas formais.",
            user_prompt=simplify_prompt,
            temperature=0.0,
            max_tokens=2000
        )
        
        # Verificar se simplificação é válida
        result = verifier.verify(simplified)
        
        if result.is_valid:
            return simplified
        else:
            return None
    
    def _should_terminate(
        self,
        state: RecursionState,
        config: RecursionConfig
    ) -> bool:
        """Parar quando válido ou limite atingido"""
        
        # Válido?
        if state.all_iterations and \
           state.all_iterations[-1].extra_data.get("is_valid"):
            return True
        
        # Limite iterações
        if state.iteration >= config.max_iterations:
            return True
        
        # Limite tokens
        if state.tokens_used >= config.max_tokens_total:
            return True
        
        return False
```

---

## 🔧 Verificadores Formais por Linguagem

### Lean4 (Recomendado para 2026)

```python
class Lean4Verifier(FormalVerifier):
    """Verificador Lean4 (com Lake package manager)"""
    
    def __init__(self, lake_path: str = "lake"):
        self.lake_cmd = lake_path
    
    def verify(self, proof_code: str) -> VerificationResult:
        """Verificar prova Lean4"""
        
        # Escrever em arquivo .lean temporário
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".lean",
            delete=False,
            dir="./tmp_proofs"
        ) as f:
            f.write(proof_code)
            proof_file = f.name
        
        try:
            # Executar Lean
            result = subprocess.run(
                [self.lake_cmd, "env", "lean", proof_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return VerificationResult(
                    is_valid=True,
                    error_message=None,
                    error_line=None,
                    verify_time_ms=0
                )
            else:
                # Parse erro
                stderr = result.stderr
                error_line = self._parse_error_line(stderr)
                
                return VerificationResult(
                    is_valid=False,
                    error_message=stderr,
                    error_line=error_line,
                    verify_time_ms=0
                )
        
        except subprocess.TimeoutExpired:
            return VerificationResult(
                is_valid=False,
                error_message="Verificação timeout (>30s)",
                error_line=None,
                verify_time_ms=30000
            )
        
        finally:
            os.remove(proof_file)
```

---

## 📊 Exemplos Lean4 → Prova

### Exemplo 1: Simples

```lean
-- Natural language:
-- "Prove that 2 + 2 = 4"

theorem two_plus_two : 2 + 2 = 4 := by
  norm_num
```

### Exemplo 2: Com estrutura

```lean
-- Natural language:
-- "If n is even, then n² is even"

theorem even_square (n : ℕ) (h : Even n) : Even (n ^ 2) := by
  obtain ⟨k, hk⟩ := h
  use 2 * k ^ 2
  rw [hk]
  ring
```

---

## 📊 Configuração Autoformalização

```python
{
    "technique": "autoformal",
    "provider": "openai",
    "model": "gpt-4o",
    
    "extra_params": {
        # Target
        "target_language": "lean4",     # "lean4", "lean3", "isabelle", "coq"
        "lake_path": "/usr/bin/lake",   # Caminho do Lake/Lean
        
        # Estratégia
        "allow_sorry": True,             # Permitir "sorry" em prova incompleta?
        "timeout_per_verification": 30000,  # ms
        "simplify_after_valid": True,    # Tentar simplificar?
    },
    
    "max_iterations": 15,   # Mais iterações para convergir prova
    "max_tokens_total": 25000,
    "max_time_ms": 600000   # 10 minutos
}
```

---

## 🎯 Casos de Uso

| Área | Aplicação | Taxa de Sucesso |
|------|-----------|-----------------|
| Matemática Pura | Teoremas álgebra/análise | 60-75% |
| Programação Formal | Verificação de código | 70-85% |
| Criptografia | Provas de segurança | 50-65% |
| Física Formal | Leis conservação | 55-70% |

---

## 📈 Métricas

| Métrica | Definição | Alvo 2026 |
|---------|-----------|-----------|
| **Proof Completion** | % de teoremas provados | >70% |
| **Iterations to Proof** | Média de iterações | <8 |
| **Formal Validity** | % válidas formalmente | 100% (se completas) |
| **Token Efficiency** | Tokens por linha de prova | Minimizar |
| **Latency** | Tempo até prova/falha | <5 min |

---

## 🚀 Fluxo Prático

```
Usuário: "Prove that ∀n, n > 0 → n + 1 > 1"

1. LLM formaliza em Lean4
2. Lean4 compila
3. Retorno: erro de sintaxe linha 3
4. LLM recebe feedback
5. Gera versão corrigida
6. Lean4 compila ✓
7. Retorno: sucesso!

Total: 2-3 iterações típicas
```

---

## 📚 Ferramentas Recomendadas

- **Lean4**: https://lean-lang.org/
- **Isabelle**: https://isabelle.in.tum.de/
- **Coq**: https://coq.inria.fr/

---

## 🎓 Referências

- Welleck et al., "Autoformalization with Large Language Models" (NeurIPS 2022)
- Thawani et al., "Improving Theorem Proving with LLMs via Autoformalizing" (2024)

**Próximo**: [10-METRICAS-E-BENCHMARKS.md](./10-METRICAS-E-BENCHMARKS.md)
