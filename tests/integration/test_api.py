import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Smart Shortlister" in response.json()["name"]


@pytest.mark.asyncio
async def test_register_and_login(client):
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    reg = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "testpass123", "full_name": "Test User",
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    assert token

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email
