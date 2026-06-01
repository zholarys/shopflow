import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.auth import hash_password, verify_password, create_access_token, decode_token

# --- Unit тесты (без БД) ---

def test_hash_password():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)

def test_wrong_password():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)

def test_create_and_decode_token():
    token = create_access_token({"sub": "42", "email": "test@test.com"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "test@test.com"

def test_invalid_token():
    result = decode_token("not.a.valid.token")
    assert result is None

# --- Integration тест (только health, без БД) ---

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "shopflow-backend"}

@pytest.mark.asyncio
async def test_docs_available():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/docs")
    assert response.status_code == 200

def test_intentionally_broken():
    """Этот тест специально сломан — симулируем баг в коде"""
    result = 2 + 2
    assert result == 5, "Математика сломалась!"
