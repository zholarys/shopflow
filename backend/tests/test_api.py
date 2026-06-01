import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.models.user import Base
from app.database import get_db
import os

TEST_DB_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")

@pytest_asyncio.fixture(scope="session")
async def setup_db():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_products_empty(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_register_and_login(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        reg = await ac.post("/api/auth/register", json={
            "email": "ci@test.com",
            "password": "testpass123",
            "full_name": "CI Test"
        })
        assert reg.status_code == 201

        login = await ac.post("/api/auth/login", json={
            "email": "ci@test.com",
            "password": "testpass123"
        })
        assert login.status_code == 200
        assert "access_token" in login.json()

@pytest.mark.asyncio
async def test_login_wrong_password(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "ci@test.com",
            "password": "wrongpassword"
        })
    assert response.status_code == 401
