import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    items = []
    total = 0.0

    for item in data.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        items.append({
            "product_id": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "price": product.price,
        })
        total += product.price * item.quantity
        product.stock -= item.quantity

    order = Order(
        user_id=1,
        items=items,
        total=round(total, 2),
        status="paid",
        payment_id=f"mock_{uuid.uuid4().hex[:8]}",
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order

@router.get("/", response_model=list[OrderOut])
async def list_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()
