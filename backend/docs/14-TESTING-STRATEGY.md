# 14 - Testing Strategy: Unit, Integration & E2E

## 🎯 Objetivo

Documentar estratégia de **testes completa** incluindo unit tests, integration tests, E2E tests, e load testing.

---

## 🧪 Unit Tests (pytest)

```python
# tests/unit/test_self_refine_engine.py
import pytest
from app.engines.self_refine import SelfRefineEngine
from app.models import RecursionConfig

@pytest.fixture
def config():
    return RecursionConfig(
        initial_prompt="Test prompt",
        max_iterations=3,
        temperature=0.7
    )

@pytest.fixture
def engine(config, mocker):
    # Mock LLM provider
    mock_provider = mocker.Mock()
    mock_provider.call.return_value = "Generated response"
    return SelfRefineEngine(config, mock_provider)

def test_generate_candidates(engine):
    """Testa geração de candidatos."""
    candidates = engine._generate_candidates("parent thought")
    assert len(candidates) > 0
    assert all('content' in c for c in candidates)

def test_execute_returns_result(engine, mocker):
    """Testa execução completa."""
    result = engine.execute()
    assert result.final_answer is not None
    assert 0 <= result.quality_score <= 1.0
    assert result.tokens_used > 0

def test_episodic_memory_stores_patterns(engine):
    """Testa armazenamento em memória episódica."""
    engine.memory_pool.add_successful_pattern("pattern1", 0.9)
    assert "pattern1" in engine.memory_pool.successful_patterns
```

---

## 🔗 Integration Tests

```python
# tests/integration/test_recursion_session.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, RecursionSession

@pytest.fixture
def db_session():
    """In-memory SQLite para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_and_retrieve_session(db_session):
    """Testa criação e recuperação de sessão."""
    user = User(email="test@example.com", api_key="test-key")
    db_session.add(user)
    db_session.commit()
    
    session = RecursionSession(
        user_id=user.id,
        initial_prompt="Test",
        technique="self_refine"
    )
    db_session.add(session)
    db_session.commit()
    
    retrieved = db_session.query(RecursionSession).filter(
        RecursionSession.id == session.id
    ).first()
    
    assert retrieved.initial_prompt == "Test"

def test_provider_fallback(mocker):
    """Testa fallback de providers."""
    mock_openai = mocker.Mock()
    mock_openai.call.side_effect = Exception("API Error")
    
    mock_claude = mocker.Mock()
    mock_claude.call.return_value = "Claude response"
    
    manager = ProviderManager()
    manager.register_provider(openai_config, mock_openai)
    manager.register_provider(claude_config, mock_claude)
    
    result = manager.call_with_fallback("test prompt")
    assert result == "Claude response"
```

---

## 🌐 E2E Tests (Playwright)

```python
# tests/e2e/test_recursion_flow.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.e2e
def test_complete_recursion_flow():
    """Testa fluxo completo: UI → API → Engine → Result."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navegar para aplicação
        page.goto("http://localhost:3000")
        
        # Preencher formulário
        page.fill('input[name="prompt"]', "Resolver problema X")
        page.select_option('select[name="technique"]', "tree_of_thoughts")
        
        # Submeter
        page.click('button[type="submit"]')
        
        # Aguardar resultado
        page.wait_for_selector('.result', timeout=30000)
        
        # Validar resultado
        result = page.text_content('.result')
        assert "solução" in result.lower() or "resposta" in result.lower()
        
        browser.close()

@pytest.mark.e2e
def test_websocket_streaming():
    """Testa streaming via WebSocket."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto("http://localhost:3000")
        
        # Abrir WebSocket
        page.on("websocket", lambda ws: print(f"WebSocket: {ws.url}"))
        
        page.click('button[type="submit"]')
        
        # Verificar se há updates
        page.wait_for_selector('.iteration-update', timeout=20000)
        updates = page.query_selector_all('.iteration-update')
        assert len(updates) > 0
        
        browser.close()
```

---

## 📊 Load Testing (Locust)

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class RecursionUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Login antes de testes."""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.api_key = response.json()["api_key"]
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    @task(3)
    def execute_recursion(self):
        """Executar recursão."""
        self.client.post(
            "/recursion/execute",
            json={
                "prompt": "Test query",
                "technique": "self_refine",
                "max_iterations": 3
            },
            headers=self.headers
        )
    
    @task(1)
    def check_stats(self):
        """Verificar stats."""
        self.client.get("/stats", headers=self.headers)
```

Rodando:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

---

## ✅ Checklist

- [ ] Implementar unit tests para todos os engines
- [ ] Fixtures pytest para models e providers
- [ ] Tests de integração com database
- [ ] Tests de fallback e error handling
- [ ] E2E tests com Playwright
- [ ] Load tests com Locust
- [ ] Coverage > 80%
- [ ] CI/CD pipeline executando testes
- [ ] Performance benchmarks
- [ ] Stress testing

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
