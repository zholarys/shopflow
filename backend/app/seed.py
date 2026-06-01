import asyncio
from app.database import AsyncSessionLocal
from app.models.product import Product

products = [
    Product(name="iPhone 15", description="Apple iPhone 15 128GB", price=799.99, stock=10, category="phones", image_url="https://picsum.photos/seed/iphone/400/300"),
    Product(name="Samsung Galaxy S24", description="Samsung Galaxy S24 256GB", price=699.99, stock=15, category="phones", image_url="https://picsum.photos/seed/samsung/400/300"),
    Product(name="MacBook Pro 14", description="Apple M3 Pro, 18GB RAM", price=1999.99, stock=5, category="laptops", image_url="https://picsum.photos/seed/macbook/400/300"),
    Product(name="Dell XPS 15", description="Intel i7, 32GB RAM, RTX 4060", price=1499.99, stock=8, category="laptops", image_url="https://picsum.photos/seed/dell/400/300"),
    Product(name="Sony WH-1000XM5", description="Wireless noise-cancelling headphones", price=349.99, stock=20, category="audio", image_url="https://picsum.photos/seed/sony/400/300"),
    Product(name="AirPods Pro 2", description="Active noise cancellation, MagSafe", price=249.99, stock=25, category="audio", image_url="https://picsum.photos/seed/airpods/400/300"),
]

async def seed():
    async with AsyncSessionLocal() as db:
        for p in products:
            db.add(p)
        await db.commit()
    print(f"Seeded {len(products)} products")

asyncio.run(seed())
