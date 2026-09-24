"""API regression tests with isolated SQLite data, no live external services."""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_db
from app.models.user import Base, User
from app.models.product import Product
from app.services.auth import create_access_token

@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    async with sessions() as db:
        db.add_all([
            User(id=1, email="one@example.com", hashed_password="unused", is_active=True),
            User(id=2, email="two@example.com", hashed_password="unused", is_active=True),
            User(id=3, email="disabled@example.com", hashed_password="unused", is_active=False),
            Product(id=1, name="Demo", price=10, stock=5, is_active=True),
        ])
        await db.commit()
    async def database():
        async with sessions() as db:
            try:
                yield db
                await db.commit()
            except Exception:
                await db.rollback()
                raise
    app.dependency_overrides[get_db] = database
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()

def headers(user_id):
    return {"Authorization": "Bearer " + create_access_token({"sub": str(user_id)})}

@pytest.mark.asyncio
async def test_order_requires_login(client):
    assert (await client.get("/api/orders/")).status_code == 401
    response = await client.post("/api/orders/", json={"items": [{"product_id": 1, "quantity": 1}]})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_orders_are_owned_by_authenticated_user(client):
    response = await client.post("/api/orders/", headers=headers(2),
                                 json={"items": [{"product_id": 1, "quantity": 2}]})
    assert response.status_code == 201
    assert response.json()["total"] == 20
    assert (await client.get("/api/orders/", headers=headers(1))).json() == []
    own = (await client.get("/api/orders/", headers=headers(2))).json()
    assert [order["id"] for order in own] == [response.json()["id"]]

@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [0, -1])
async def test_quantity_must_be_positive(client, quantity):
    response = await client.post("/api/orders/", headers=headers(1),
                                 json={"items": [{"product_id": 1, "quantity": quantity}]})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_empty_order_rejected(client):
    assert (await client.post("/api/orders/", headers=headers(1), json={"items": []})).status_code == 422

@pytest.mark.asyncio
async def test_duplicate_items_cannot_exceed_stock(client):
    response = await client.post("/api/orders/", headers=headers(1), json={"items": [
        {"product_id": 1, "quantity": 3}, {"product_id": 1, "quantity": 3}]})
    assert response.status_code == 400

@pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [3, 999, "invalid"])
async def test_disabled_missing_and_invalid_user_rejected(client, user_id):
    assert (await client.get("/api/orders/", headers=headers(user_id))).status_code == 401

@pytest.mark.asyncio
async def test_product_creation_requires_admin(client):
    response = await client.post("/api/products/", headers=headers(1),
                                 json={"name": "New", "price": 1, "stock": 1})
    assert response.status_code == 403
