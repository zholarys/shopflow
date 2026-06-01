import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut, ProductCreate
from app.redis import get_redis

router = APIRouter(prefix="/api/products", tags=["products"])

CACHE_TTL = 60  # секунд

@router.get("/", response_model=list[ProductOut])
async def list_products(
    search: str | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    cache_key = f"products:{search}:{category}"

    # Пробуем взять из кэша
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

    # Если нет в кэше — идём в БД
    query = select(Product).where(Product.is_active == True)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.where(Product.category == category)
    result = await db.execute(query)
    products = result.scalars().all()

    # Сохраняем в кэш
    if redis:
        data = [ProductOut.model_validate(p).model_dump() for p in products]
        await redis.set(cache_key, json.dumps(data), ex=CACHE_TTL)
        return data

    return products

@router.get("/categories", response_model=list[str])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    cache_key = "categories"

    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

    result = await db.execute(select(Product.category).distinct())
    categories = [r for r in result.scalars().all() if r]

    if redis:
        await redis.set(cache_key, json.dumps(categories), ex=CACHE_TTL)

    return categories

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product
