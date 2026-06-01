import asyncio
from app.database import engine
from app.models.user import Base as UserBase
from app.models.product import Product
from app.models.order import Order

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
    print("Tables created successfully")

asyncio.run(init())
