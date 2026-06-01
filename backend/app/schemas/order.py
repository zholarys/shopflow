from pydantic import BaseModel
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: list[OrderItem]

class OrderOut(BaseModel):
    id: int
    status: str
    total: float
    items: list
    payment_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
