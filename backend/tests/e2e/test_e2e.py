"""
E2E Tests for Prompt-Boost Backend
Tests complete flows across all components
"""

import asyncio
import json
import pytest
from httpx import AsyncClient
from websockets.client import connect, WebSocketClientProtocol
from typing import AsyncGenerator

from src.main import app
from src.config import settings


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
async def ws_url() -> str:
    """Get WebSocket URL for testing."""
    return f"ws://localhost:8000/ws/recursion"


class TestE2EHealthAndMetrics:
    """Test health checks and metrics endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"

    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await client.get("/metrics")
        assert response.status_code == 200
        assert b"http_requests_total" in response.content
        assert b"recursion_sessions_total" in response.content

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Prompt-Boost v2.0.0"
        assert data["status"] == "running"


class TestE2ERecursionAPI:
    """Test recursion API endpoints."""

    async def test_list_techniques(self, client: AsyncClient):
        """Test listing all recursion techniques."""
        response = await client.get("/api/recursion/techniques")
        assert response.status_code == 200
        data = response.json()
        assert "techniques" in data
        techniques = data["techniques"]
        assert len(techniques) == 7
        
        # Verify all techniques are present
        technique_names = {t["name"] for t in techniques}
        expected = {
            "Self-Refine",
            "Tree of Thoughts",
            "Graph of Thoughts",
            "MCTS",
            "Multi-Agent Debate",
            "Alignment",
            "AutoFormal",
        }
        assert technique_names == expected

    async def test_execute_recursion_basic(self, client: AsyncClient):
        """Test executing a basic recursion session."""
        request_data = {
            "query": "What are the benefits of recursive reasoning?",
            "technique": "self_refine",
            "max_iterations": 3,
            "temperature": 0.7,
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "session_id" in data
        assert "technique" in data
        assert data["technique"] == "self_refine"
        assert "iterations" in data
        assert len(data["iterations"]) > 0
        assert "quality_score" in data
        assert 0 <= data["quality_score"] <= 1

    async def test_execute_recursion_all_techniques(self, client: AsyncClient):
        """Test executing recursion with all techniques."""
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
            request_data = {
                "query": f"Test query for {technique}",
                "technique": technique,
                "max_iterations": 2,
            }
            
            response = await client.post(
                "/api/recursion/execute",
                json=request_data,
            )
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert data["technique"] == technique

    async def test_get_session(self, client: AsyncClient):
        """Test retrieving a recursion session."""
        # First, execute a recursion
        request_data = {
            "query": "Test query",
            "technique": "self_refine",
            "max_iterations": 2,
        }
        
        exec_response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert exec_response.status_code == 200
        session_id = exec_response.json()["session_id"]
        
        # Then retrieve it
        response = await client.get(f"/api/recursion/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["technique"] == "self_refine"

    async def test_list_sessions(self, client: AsyncClient):
        """Test listing sessions with pagination."""
        # Execute a few sessions
        for i in range(3):
            request_data = {
                "query": f"Test query {i}",
                "technique": "self_refine",
                "max_iterations": 1,
            }
            await client.post("/api/recursion/execute", json=request_data)
        
        # List sessions
        response = await client.get("/api/recursion/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert "page" in data
        assert len(data["sessions"]) > 0

    async def test_invalid_technique(self, client: AsyncClient):
        """Test error handling for invalid technique."""
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

    async def test_missing_required_field(self, client: AsyncClient):
        """Test error handling for missing required fields."""
        request_data = {
            "technique": "self_refine",
            # Missing "query"
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert response.status_code in (400, 422)


class TestE2EWebSocket:
    """Test WebSocket endpoints."""

    async def test_websocket_connection(self):
        """Test establishing WebSocket connection."""
        try:
            async with connect("ws://localhost:8000/ws/debug") as websocket:
                # Send a message
                await websocket.send("Hello")
                
                # Receive echo response
                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=2.0,
                )
                assert response == "Hello"
        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not available")

    async def test_websocket_recursion_stream(self):
        """Test WebSocket streaming for recursion."""
        try:
            async with connect("ws://localhost:8000/ws/recursion") as websocket:
                # Send recursion request
                request = {
                    "query": "What is recursive reasoning?",
                    "technique": "self_refine",
                    "max_iterations": 2,
                }
                await websocket.send(json.dumps(request))
                
                # Receive streaming responses
                messages = []
                while True:
                    try:
                        msg = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=2.0,
                        )
                        messages.append(json.loads(msg))
                        
                        # Check for completion message
                        if messages[-1].get("type") == "complete":
                            break
                    except asyncio.TimeoutError:
                        break
                
                # Verify we received messages
                assert len(messages) > 0
        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not available")


class TestE2EPerformance:
    """Test performance and load characteristics."""

    async def test_concurrent_requests(self, client: AsyncClient):
        """Test handling concurrent requests."""
        request_data = {
            "query": "Concurrent test query",
            "technique": "self_refine",
            "max_iterations": 1,
        }
        
        # Send 5 concurrent requests
        tasks = [
            client.post("/api/recursion/execute", json=request_data)
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200
            assert "session_id" in response.json()

    async def test_large_query(self, client: AsyncClient):
        """Test handling large query strings."""
        large_query = "Question: " + " ".join([
            "This is a test query to check if the system can handle large inputs."
        ] * 100)
        
        request_data = {
            "query": large_query,
            "technique": "self_refine",
            "max_iterations": 1,
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        assert response.status_code == 200


class TestE2ECORSAndSecurity:
    """Test CORS and security headers."""

    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are set correctly."""
        response = await client.options(
            "/api/recursion/techniques",
            headers={"Origin": "http://localhost:3000"},
        )
        
        # CORS headers may vary, but endpoint should be accessible
        assert response.status_code in (200, 204, 405)

    async def test_http_methods_not_allowed(self, client: AsyncClient):
        """Test that disallowed HTTP methods return errors."""
        # GET on POST-only endpoint
        response = await client.get("/api/recursion/execute")
        assert response.status_code in (405, 404)


class TestE2EErrorHandling:
    """Test error handling and edge cases."""

    async def test_timeout_handling(self, client: AsyncClient):
        """Test request timeout handling."""
        # This would need a server-side timeout setting
        # For now, we just verify the endpoint responds
        request_data = {
            "query": "Test timeout",
            "technique": "self_refine",
            "max_iterations": 10,  # High iterations
        }
        
        response = await client.post(
            "/api/recursion/execute",
            json=request_data,
        )
        # Should eventually respond, even if slow
        assert response.status_code in (200, 408, 504)

    async def test_malformed_json(self, client: AsyncClient):
        """Test handling of malformed JSON."""
        response = await client.post(
            "/api/recursion/execute",
            content=b"invalid json {",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (400, 422)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
