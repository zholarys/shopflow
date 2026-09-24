import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.dependencies import current_user
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderOut
from app.logger import get_logger

logger = get_logger("orders")

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db),
                       user: User = Depends(current_user)):
    items = []
    total = 0.0

    # Aggregate repeated products, and lock in a stable order to avoid overselling.
    quantities = {}
    for item in data.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
    for product_id, quantity in sorted(quantities.items()):
        result = await db.execute(select(Product).where(Product.id == product_id).with_for_update())
        product = result.scalar_one_or_none()
        if not product:
            logger.warning(f"Product not found: id={product_id}")
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        if product.stock < quantity:
            logger.warning(f"Not enough stock: product={product.name} stock={product.stock} requested={quantity}")
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        items.append({
            "product_id": product.id,
            "name": product.name,
            "quantity": quantity,
            "price": product.price,
        })
        total += product.price * quantity
        product.stock -= quantity

    order = Order(
        user_id=user.id,
        items=items,
        total=round(total, 2),
        status="paid",
        payment_id=f"mock_{uuid.uuid4().hex[:8]}",
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    
    logger.info(f"Order created: id={order.id} total={order.total} payment={order.payment_id}")
    return order

@router.get("/", response_model=list[OrderOut])
async def list_orders(db: AsyncSession = Depends(get_db),
                      user: User = Depends(current_user)):
    result = await db.execute(select(Order).where(Order.user_id == user.id))
    return result.scalars().all()
