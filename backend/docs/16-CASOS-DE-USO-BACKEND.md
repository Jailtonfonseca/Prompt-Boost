# 16 - Casos de Uso Backend: Aplicações Práticas

## 🎯 Objetivo

Demonstrar 7 casos de uso realistas do backend Prompt-Boost v2.0, mostrando como diferentes técnicas de recursão resolvem problemas específicos com exemplos completos de request/response, fluxo de dados, e análise.

---

## 📌 Caso 1: Pesquisa Acadêmica com Tree of Thoughts

**Cenário**: Pesquisador precisa estruturar argumentação sobre "impacto de IA em educação"

### Request HTTP
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -H "Authorization: Bearer user_token" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Estruture um argumento acadêmico sobre o impacto de IA na educação superior, considerando perspectivas técnicas, pedagógicas e socioeconômicas",
    "technique": "tree_of_thoughts",
    "max_iterations": 5,
    "temperature": 0.6,
    "config": {
      "beam_width": 3,
      "max_depth": 4,
      "value_threshold": 0.7
    }
  }'
```

### Response Success (200 OK)
```json
{
  "session_id": "sess_12345",
  "technique": "tree_of_thoughts",
  "status": "completed",
  "final_answer": {
    "thesis": "IA transformará educação superior através de personalização adaptativa, mantendo rigor acadêmico e equidade de acesso",
    "arguments": [
      {
        "perspective": "Técnica",
        "points": [
          "Machine learning enable real-time personalization",
          "Natural language processing improve feedback quality",
          "Predictive models identify at-risk students"
        ]
      },
      {
        "perspective": "Pedagógica",
        "points": [
          "Socratic method can be augmented with AI tutoring",
          "Assessment becomes continuous, not terminal",
          "Critical thinking skills remain essential"
        ]
      },
      {
        "perspective": "Socioeconômica",
        "points": [
          "Reduces educational inequalities through access",
          "Creates new job categories in AI education",
          "Requires infrastructure investment"
        ]
      }
    ]
  },
  "quality_score": 0.87,
  "iterations": 4,
  "tokens_used": 8942,
  "rer_score": 0.92,
  "execution_time_ms": 23500,
  "created_at": "2025-04-10T14:32:00Z",
  "updated_at": "2025-04-10T14:32:23Z"
}
```

### Fluxo de Dados Interno
```
1. REQUEST → RecursionRouter
   └─ Validar token + Rate limit
   └─ Parse config + Sanitize input

2. RecursionRouter → ToT Engine
   └─ Initialize: root = "Estruture um argumento..."
   
3. ToT Engine: Iteração 1-4
   ├─ GENERATE: 3 branches (Técnica, Pedagógica, Socioeconômica)
   ├─ EVALUATE: Score cada branch (0.7, 0.85, 0.8)
   ├─ FEEDBACK: "Perspectiva Pedagógica promissora, aprofundar"
   ├─ REFINE: Expandir branch com score 0.85
   └─ Record iteration em database
   
4. Iteração 4: Quality score > 0.85 → TERMINATE

5. DATABASE SAVE
   ├─ RecursionSession record
   ├─ 4x IterationRecord
   └─ VerificationResult (if applied)

6. RESPONSE → Client
   └─ JSON com final_answer + metadata
```

### Archivos de Base de Datos
```sql
-- RecursionSession
INSERT INTO recursion_sessions (
  user_id, technique, initial_prompt, status, final_answer,
  quality_score, iterations, tokens_used, created_at
) VALUES (
  'user_123', 'tree_of_thoughts',
  'Estruture um argumento acadêmico...',
  'completed', '{"thesis": "IA transformará...", ...}',
  0.87, 4, 8942, NOW()
);

-- IterationRecord (Iteração 1)
INSERT INTO iteration_records (
  session_id, iteration, state, candidates, chosen,
  quality_score, tokens_used, created_at
) VALUES (
  'sess_12345', 1,
  '{"root": "Estruture..."}',
  '["branch_tecnica", "branch_pedagógica", "branch_socioeconômica"]',
  'branch_pedagógica', 0.85, 2235, NOW()
);
```

### Diagrama de Decisão (Tree)
```
Argumento Acadêmico
├── Perspectiva Técnica (score: 0.70)
│   ├── ML personalization (0.75)
│   ├── NLP feedback (0.68)
│   └── Predictive models (0.71)
├── Perspectiva Pedagógica ⭐ (score: 0.85) [SELECIONADO]
│   ├── Socratic method (0.88)
│   ├── Continuous assessment (0.86)
│   └── Critical thinking (0.81)
└── Perspectiva Socioeconômica (score: 0.80)
    ├── Access/equity (0.82)
    ├── Job creation (0.78)
    └── Infrastructure (0.80)
```

---

## 📌 Caso 2: Detecção de Fraude com MCTS

**Cenário**: Sistema financeiro detecta transação suspeita, backend aplica MCTS para análise de risco

### Request (via WebSocket para streaming)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/recursion/sess_67890');

ws.onopen = () => {
  ws.send(JSON.stringify({
    prompt: "Analise se a transação $5000 de usuario_123 para merchant_xyz é fraude, considerando histórico, velocidade, localização",
    technique: "mcts",
    max_iterations: 6,
    config: {
      num_simulations: 50,
      exploration_constant: 1.41,
      max_depth_rollout: 4
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'iteration_update') {
    console.log(`Iteração ${message.iteration}:`, {
      current_risk: message.current_best.risk_score,
      confidence: message.quality_score
    });
  }
  
  if (message.type === 'completion') {
    console.log('Análise completa:', message.final_answer);
  }
};
```

### WebSocket Messages (Streaming)
```json
// Message 1: Iteração 1
{
  "type": "iteration_update",
  "session_id": "sess_67890",
  "iteration": 1,
  "current_best": {
    "risk_score": 0.62,
    "primary_factors": ["high_amount", "late_night", "new_merchant"],
    "recommendation": "investigate"
  },
  "quality_score": 0.62,
  "tokens_used": 1240
}

// Message 2: Iteração 2
{
  "type": "iteration_update",
  "session_id": "sess_67890",
  "iteration": 2,
  "current_best": {
    "risk_score": 0.58,
    "primary_factors": ["high_amount", "but_consistent_pattern"],
    "recommendation": "investigate"
  },
  "quality_score": 0.68,
  "tokens_used": 2450
}

// Message 3: Iteração 3
{
  "type": "iteration_update",
  "session_id": "sess_67890",
  "iteration": 3,
  "current_best": {
    "risk_score": 0.45,
    "primary_factors": ["user_has_5_similar_transactions_previously"],
    "recommendation": "low_risk"
  },
  "quality_score": 0.78,
  "tokens_used": 3620
}

// Final Message
{
  "type": "completion",
  "session_id": "sess_67890",
  "final_answer": {
    "risk_score": 0.42,
    "fraud_probability": "4.2%",
    "recommendation": "approve_with_monitoring",
    "factors_analyzed": 18,
    "confidence": 0.92
  },
  "quality_score": 0.92,
  "total_iterations": 5,
  "execution_time_ms": 18200
}
```

### Simulação MCTS (Interna)
```
Node Selection (UCB1):
  Root (risk=0.62)
  ├─ Sim_1: Amount is high → risk 0.70 (UCB1: 0.85)
  ├─ Sim_2: Late night + new merchant → risk 0.65 (UCB1: 0.78) ⭐
  └─ Sim_3: Merchant in user's region → risk 0.35 (UCB1: 0.52)
  
Expansion: Nó 2 expandido com 2 novos children

Simulation (Rollout):
  - Random playout até profundidade 4
  - 50 simulações paralelas
  
Backpropagation:
  - Atualizar statistics de cada node
  - Risk score converge para 0.42
```

---

## 📌 Caso 3: Síntese de Debate com Multi-Agent Debate

**Cenário**: Empresa precisa avaliar proposta de mudança política, backend orquestra debate entre perspectivas

### Request
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -H "Authorization: Bearer admin_token" \
  -d '{
    "prompt": "Avalie se devemos migrar de microserviços para arquitetura monolítica",
    "technique": "multi_agent_debate",
    "max_iterations": 4,
    "config": {
      "num_agents": 3,
      "debate_rounds": 3,
      "synthesis_depth": 2
    }
  }'
```

### Response
```json
{
  "session_id": "sess_99999",
  "technique": "multi_agent_debate",
  "status": "completed",
  "final_answer": {
    "decision": "Manter arquitetura de microserviços com consolidação seletiva",
    "confidence": 0.85,
    "rationale": "Escalabilidade crítica, mas consolidar 3 serviços de baixa latência"
  },
  "debate_summary": {
    "round_1": {
      "pro": {
        "agent": "Pragmatista",
        "argument": "Monolito reduz complexidade operacional e latência inter-serviço"
      },
      "con": {
        "agent": "Escalabilista",
        "argument": "Microserviços permitem escalar apenas componentes críticos"
      },
      "judge_decision": "Ambos válidos, depends on usage patterns"
    },
    "round_2": {
      "pro": "Demonstra: 3 serviços causam 40% latência do total",
      "con": "Mas 5 outros serviços são independentes e escalam bem",
      "judge": "Consolidação seletiva é compromisso"
    },
    "round_3": {
      "synthesis": "Consolidar 3 serviços de baixa latência, manter 5 escaláveis",
      "pros_acceptance": 0.85,
      "cons_acceptance": 0.80
    }
  },
  "quality_score": 0.85,
  "iterations": 4,
  "tokens_used": 12450
}
```

### Diálogo de Debate (Inline)
```
JUDGE: "Devemos migrar para monolito?"

PRO AGENT (Pragmatista):
"Sim. Temos 3 serviços com latência crítica:
 - API Gateway ↔ Auth: 120ms avg
 - Auth ↔ Payment: 150ms avg
 - Monolito reduce para ~5ms inter-process"

CON AGENT (Escalabilista):
"Não. Temos 5 serviços que escalam independentemente:
 - Recommendations pode escalar 10x sem afetar Auth
 - Monolito criaria bottleneck"

JUDGE:
"PRO: Dados sobre latência são convincentes.
 CON: Escalabilidade independente é valiosa.
 PROPOSTA: Consolidar os 3 serviços críticos, manter 5 escaláveis?"

PRO: "Aceitável se consolidação for isolada"
CON: "Aceitável se boundary estiver clara"

JUDGE: "Consenso alcançado. Implementar consolidação seletiva."
```

---

## 📌 Caso 4: Auditoria de Alinhamento com Alignment Engine

**Cenário**: Empresa precisa verificar se saída de IA atende critérios de segurança e viés

### Request
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -H "Authorization: Bearer compliance_token" \
  -d '{
    "prompt": "Audite esta decisão de empréstimo: Negar $50k a aplicante com score 720, FICO 650 devido a region=rural",
    "technique": "alignment",
    "max_iterations": 5,
    "config": {
      "verify_safety": true,
      "verify_consistency": true,
      "detect_bias": true
    }
  }'
```

### Response
```json
{
  "session_id": "sess_55555",
  "technique": "alignment",
  "status": "completed",
  "final_answer": {
    "verdict": "❌ REJECTED - Decisão viola critérios de equidade",
    "risk_level": "high",
    "violations": [
      {
        "type": "geographic_bias",
        "description": "Rural region não é fator legítimo em empréstimos",
        "severity": "critical",
        "recommendation": "Remover region do modelo"
      },
      {
        "type": "inconsistency",
        "description": "Score 720 é típicamente aprovado, mas recusado aqui",
        "severity": "high",
        "recommendation": "Revisar lógica de decisão"
      }
    ]
  },
  "verification_results": {
    "logical_consistency": {
      "passed": false,
      "score": 0.32,
      "issues": ["Decisão contradiz score e FICO"]
    },
    "safety_check": {
      "passed": false,
      "score": 0.18,
      "red_flags": ["Geographic discrimination", "Disparate impact"]
    },
    "bias_detection": {
      "demographic_parity": false,
      "disparate_impact_ratio": 3.4,
      "recommendation": "Reject decision, retrain model"
    }
  },
  "quality_score": 0.95,
  "confidence_in_audit": 0.98
}
```

### Verificadores Ativados
```
1. LogicalConsistencyVerifier
   ├─ Score 720 typical approval? YES
   ├─ FICO 650 reject threshold? NO
   ├─ Contradiction detected? YES
   └─ Consistency Score: 0.32

2. SafetyVerifier
   ├─ Geographic discrimination check? YES
   ├─ Protected class check? NO VIOLATIONS
   ├─ Disparate impact analysis? TRIGGERED
   └─ Safety Score: 0.18

3. BiasDetector
   ├─ Compare rural vs urban approval rates
   │  ├─ Urban: 68% approval rate
   │  ├─ Rural: 12% approval rate
   │  └─ Disparate Impact Ratio: 3.4 (>1.25 threshold)
   ├─ Demographic parity? FAILED
   └─ Recommendation: REJECT DECISION
```

---

## 📌 Caso 5: Formalização com AutoFormal Engine

**Cenário**: Pesquisador precisa formalizar algoritmo em Lean4 para verificação matemática

### Request
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -H "Authorization: Bearer researcher_token" \
  -d '{
    "prompt": "Formalize em Lean4: 'Se um número é divisível por 6, então é divisível por 2 e 3'",
    "technique": "autoformal",
    "max_iterations": 3,
    "config": {
      "target_language": "lean4",
      "verification_enabled": true
    }
  }'
```

### Response
```json
{
  "session_id": "sess_44444",
  "technique": "autoformal",
  "status": "completed",
  "final_answer": {
    "lean4_proof": "theorem divisible_by_6_implies_2_and_3 (n : ℕ) (h : 6 ∣ n) : 2 ∣ n ∧ 3 ∣ n := by\n  obtain ⟨k, hk⟩ := h\n  use 3 * k\n  use 2 * k\n  omega",
    "formalization_correctness": 0.98,
    "verification_status": "✅ Proven"
  },
  "intermediate_steps": [
    {
      "iteration": 1,
      "nl_input": "Se 6 divide n, então existe k tal que n = 6k",
      "lean4_attempt": "theorem aux : 6 ∣ n → ∃ k, n = 6 * k",
      "status": "✅ Compiles"
    },
    {
      "iteration": 2,
      "nl_input": "6k = 2 * (3k), então 2 divide n",
      "lean4_attempt": "theorem aux2 : ∃ k, n = 6 * k → 2 ∣ n",
      "status": "✅ Compiles"
    },
    {
      "iteration": 3,
      "nl_input": "Combine ambas as partes com conjunction",
      "lean4_attempt": "[proof acima]",
      "status": "✅ Verified by Lean4 compiler"
    }
  ],
  "quality_score": 0.98,
  "verification_passed": true
}
```

### Geração NL → Lean4
```
NL Parser:
"Se um número é divisível por 6, então é divisível por 2 e 3"
↓
Parse Tree:
  Conditional
  ├─ Premise: "número divisível por 6"
  ├─ Consequence: "divisível por 2 E divisível por 3"

Lean4 Code Generator:
  theorem_name: divisible_by_6_implies_2_and_3
  variables: n : ℕ
  hypothesis: h : 6 ∣ n
  goal: 2 ∣ n ∧ 3 ∣ n
  
  proof_generation:
    1. `obtain ⟨k, hk⟩ := h` (extract witness)
    2. `use 3 * k` (prove 2 divides)
    3. `use 2 * k` (prove 3 divides)
    4. `omega` (decide arithmetic)
    
Lean4 Verifier:
  ✅ Type checking passed
  ✅ Proof is complete
  ✅ Theorem is valid
```

---

## 📌 Caso 6: Otimização de Query SQL com Self-Refine

**Cenário**: DBA precisa otimizar query lenta, backend aplica self-refine iterativamente

### Request
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -d '{
    "prompt": "Otimize esta query que roda em 45 segundos:\nSELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id=o.user_id WHERE u.created_at > DATE_SUB(NOW(), INTERVAL 90 DAY) GROUP BY u.id",
    "technique": "self_refine",
    "max_iterations": 4,
    "config": {
      "episodic_memory": true,
      "refinement_strategies": 3
    }
  }'
```

### Response
```json
{
  "session_id": "sess_33333",
  "technique": "self_refine",
  "status": "completed",
  "final_answer": {
    "optimized_query": "SELECT u.id, u.name, COALESCE(cnt, 0) as order_count\nFROM users u\nLEFT JOIN (\n  SELECT user_id, COUNT(*) as cnt\n  FROM orders\n  WHERE status != 'cancelled'\n  GROUP BY user_id\n) o ON u.id = o.user_id\nWHERE u.created_at > DATE_SUB(NOW(), INTERVAL 90 DAY)\nINDEX HINT (USE INDEX (idx_users_created_at), USE INDEX (idx_orders_user_id))",
    "estimated_execution_time": "1.2 seconds",
    "improvement": "97.3%"
  },
  "refinement_history": [
    {
      "iteration": 1,
      "strategy": "Subquery optimization",
      "proposed_change": "Move aggregation to subquery",
      "estimated_gain": 0.65,
      "executed": true,
      "result": "Query now ~12 seconds (73% improvement)"
    },
    {
      "iteration": 2,
      "strategy": "Index hints",
      "proposed_change": "Add USE INDEX hints",
      "estimated_gain": 0.85,
      "executed": true,
      "result": "Query now ~4 seconds (91% improvement)"
    },
    {
      "iteration": 3,
      "strategy": "Filter application",
      "proposed_change": "Filter cancelled orders before aggregation",
      "estimated_gain": 0.73,
      "executed": true,
      "result": "Query now ~1.2 seconds (97% improvement)"
    },
    {
      "iteration": 4,
      "strategy": "Early termination",
      "proposed_change": "Check if further optimization possible",
      "estimated_gain": 0.12,
      "executed": false,
      "reason": "Gains diminishing, quality score > 0.95"
    }
  ],
  "episodic_memory_hits": ["subquery optimization", "index hints"],
  "quality_score": 0.96,
  "recommendation": "Apply iterations 1-3, test on staging"
}
```

---

## 📌 Caso 7: Análise de Estratégia com Graph of Thoughts

**Cenário**: Estrategista de produto precisa analisar competição e recomendar estratégia

### Request
```bash
curl -X POST http://localhost:8000/recursion/execute \
  -d '{
    "prompt": "Analise posicionamento competitivo de Prompt-Boost vs Cursor, Windsurf, e Claude.dev considerando: pricing, funcionalidades, segmento de mercado, e recomende estratégia diferenciadora",
    "technique": "graph_of_thoughts",
    "max_iterations": 5,
    "config": {
      "node_limit": 20,
      "merge_similar_nodes": true
    }
  }'
```

### Response
```json
{
  "session_id": "sess_77777",
  "technique": "graph_of_thoughts",
  "status": "completed",
  "final_answer": {
    "positioning": "Enterprise-grade recursive reasoning platform for teams",
    "strategy": "Focus on API-first approach + real-time collaboration + open-source components",
    "differentiation": [
      "Multi-provider LLM support (cost optimization)",
      "Recursive thinking engines (7 techniques available)",
      "Real-time WebSocket streaming (live collaboration)",
      "Open-source verifiers (Lean4, safety auditing)"
    ]
  },
  "competitive_analysis": {
    "pricing": {
      "cursor": "$20/mo",
      "windsurf": "$50/mo + enterprise",
      "claude_dev": "Free + $20/mo Claude",
      "pb_strategy": "$30/mo personal, $200/mo team"
    },
    "strengths": ["Recursive engines", "Multi-LLM", "Team collaboration"],
    "weaknesses": ["Limited IDE integration (vs Cursor/Windsurf)"],
    "opportunities": ["Enterprise safety auditing", "Open-source ecosystem"]
  },
  "graph_nodes": 16,
  "graph_edges": 24,
  "quality_score": 0.88
}
```

### Grafo Interno
```
Node: Pricing Strategy
├─ Edge: "Lower than Windsurf" → Differentiation: Cost
├─ Edge: "Higher than free tiers" → Premium positioning
└─ Edge: "Team tier justifies value" → Team collaboration

Node: Feature Set
├─ Edge: "7 recursive engines" → Unique value
├─ Edge: "Multi-LLM support" → Flexibility
└─ Edge: "Open-source verifiers" → Trust/transparency

Node: Segmentation
├─ Edge: "Individual developers" → Personal tier
├─ Edge: "Enterprise teams" → Safety + collaboration
└─ Edge: "Researchers" → Formal verification

Cross-connections (merges):
  Safety audit + Enterprise → Premium feature
  Multi-LLM + Cost opt → Differentiation
```

---

## 🔄 Padrão Comum: Fluxo Geral

Todos os casos seguem este padrão:

```python
# 1. CLIENT REQUEST
POST /recursion/execute
  ├─ Authentication
  ├─ Validation
  └─ Rate limiting

# 2. ROUTER DISPATCH
RecursionRouter.execute()
  ├─ Select engine by technique
  ├─ Load config
  └─ Initialize recursion

# 3. ENGINE EXECUTION (Streaming)
Engine.execute()
  ├─ Iteração 1: GENERATE → EVALUATE → FEEDBACK → REFINE
  ├─ Iteração 2-N: Repetir
  └─ Iteração N: Check termination

# 4. DATABASE PERSISTENCE
  ├─ Save RecursionSession
  ├─ Save IterationRecords
  └─ Compute RER metrics

# 5. RESPONSE
  ├─ Via HTTP (sync) ou WebSocket (streaming)
  └─ Include metadata + execution stats
```

---

## ✅ Matriz de Técnicas vs Casos

| Caso | Cenário | Técnica | Por Quê |
|------|---------|---------|---------|
| 1 | Pesquisa académica | **ToT** | Estruturação com múltiplas perspectivas |
| 2 | Detecção fraude | **MCTS** | Exploração de cenários com probabilidades |
| 3 | Síntese debate | **Debate** | Multi-agent com argumentação |
| 4 | Auditoria alinhamento | **Alignment** | Verificação de segurança + viés |
| 5 | Formalização matemática | **AutoFormal** | Prova formal em Lean4 |
| 6 | Otimização query | **Self-Refine** | Refinamento iterativo |
| 7 | Análise estratégia | **GoT** | Grafo de pensamentos interconectados |

---

## 📚 Referências Cruzadas

- [00-ARQUITETURA-BACKEND.md](00-ARQUITETURA-BACKEND.md) - Visão geral arquitetura
- [01-ENGINES-IMPLEMENTACAO.md](01-ENGINES-IMPLEMENTACAO.md) - Base engine class
- [02-07 Docs por Técnica](02-SELF-REFINE-ENGINE.md) - Detalhes de cada engine
- [08-PROVIDERS-E-LLMS.md](08-PROVIDERS-E-LLMS.md) - Integração com LLMs
- [10-WEBSOCKET-PROTOCOL.md](10-WEBSOCKET-PROTOCOL.md) - Streaming em tempo real
- [13-API-REFERENCE.md](13-API-REFERENCE.md) - Endpoints REST

---

**Última atualização**: 2025
**Versão**: 2.0.0

