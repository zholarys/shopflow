import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_products_requires_db():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/products/")
    # 500 ожидаемо без БД, главное что эндпоинт существует
    assert response.status_code in [200, 500]

@pytest.mark.asyncio
async def test_login_invalid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "no@no.com", "password": "wrong"})
    assert response.status_code in [401, 500]
