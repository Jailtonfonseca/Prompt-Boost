import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "API is running"


@pytest.mark.asyncio
async def test_improve_prompt_missing_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/improve-prompt",
            json={"prompt": "Write a hello world program"}
        )
        assert response.status_code == 500
        assert "not configured" in response.json()["detail"]


@pytest.mark.asyncio
async def test_improve_prompt_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/improve-prompt",
            json={"prompt": ""}
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_share_prompt(client):
    response = await client.post(
        "/api/prompts",
        json={
            "original_prompt": "Test original",
            "improved_prompt": "Test improved"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "share_id" in data


@pytest.mark.asyncio
async def test_share_prompt_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/prompts",
            json={"original_prompt": "", "improved_prompt": ""}
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_prompt_not_found(client):
    response = await client.get("/api/prompts/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_gallery(client):
    response = await client.get("/api/gallery")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
