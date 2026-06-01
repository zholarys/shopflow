from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut, ProductCreate

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=list[ProductOut])
async def list_products(
    search: str | None = Query(None, description="Search by name"),
    category: str | None = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(Product.is_active == True)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.where(Product.category == category)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/categories", response_model=list[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product.category).distinct())
    return [r for r in result.scalars().all() if r]

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
