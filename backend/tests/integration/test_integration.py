"""
Integration Tests for Prompt-Boost Backend
Tests interactions between components
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.database import get_session, init_db
from src.models.session import RecursionSession
from src.models.user import User
from src.services.recursion_router import RecursionRouter


@pytest.fixture
async def client():
    """Create async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
async def db_session() -> AsyncSession:
    """Get database session."""
    async for session in get_session():
        yield session


class TestIntegrationRecursionRouter:
    """Test RecursionRouter integration."""

    @pytest.mark.asyncio
    async def test_router_selects_correct_engine(self, db_session: AsyncSession):
        """Test that RecursionRouter selects the correct engine."""
        router = RecursionRouter()
        
        techniques = [
            "self_refine",
            "tree_of_thoughts",
            "graph_of_thoughts",
            "mcts",
            "multi_agent_debate",
            "alignment",
            "autoformal",
        ]
        
        for technique in techniques:
            engine = router.get_engine(technique)
            assert engine is not None
            assert engine.name == technique

    @pytest.mark.asyncio
    async def test_router_executes_engine(self):
        """Test executing through router."""
        router = RecursionRouter()
        
        result = await router.execute(
            query="Test query",
            technique="self_refine",
            max_iterations=2,
        )
        
        assert result is not None
        assert "iterations" in result
        assert len(result["iterations"]) > 0


class TestIntegrationDatabase:
    """Test database integration."""

    @pytest.mark.asyncio
    async def test_session_creation_and_retrieval(self, db_session: AsyncSession):
        """Test creating and retrieving a RecursionSession."""
        # Create a session
        session = RecursionSession(
            user_id=1,
            technique="self_refine",
            query="Test query",
            status="completed",
            iterations=3,
            quality_score=0.85,
        )
        
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        
        # Retrieve it
        retrieved = await db_session.get(RecursionSession, session.id)
        assert retrieved is not None
        assert retrieved.technique == "self_refine"
        assert retrieved.query == "Test query"

    @pytest.mark.asyncio
    async def test_user_creation(self, db_session: AsyncSession):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Retrieve it
        retrieved = await db_session.get(User, user.id)
        assert retrieved is not None
        assert retrieved.email == "test@example.com"


class TestIntegrationAPIToDatabase:
    """Test API integration with database."""

    @pytest.mark.asyncio
    async def test_recursion_execution_saves_to_db(self, client: AsyncClient):
        """Test that executing recursion saves session to database."""
        request_data = {
            "query": "Integration test query",
            "technique": "self_refine",
            "max_iterations": 2,
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Retrieve the session from database via API
        response = await client.get(f"/api/recursion/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Integration test query"
        assert data["technique"] == "self_refine"


class TestIntegrationErrorPropagation:
    """Test error handling across components."""

    @pytest.mark.asyncio
    async def test_invalid_technique_error(self, client: AsyncClient):
        """Test invalid technique error propagates correctly."""
        request_data = {
            "query": "Test query",
            "technique": "invalid_technique",
            "max_iterations": 2,
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert response.status_code in (400, 422)
        data = response.json()
        assert "detail" in data or "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
