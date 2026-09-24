from pydantic import BaseModel, Field
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: list[OrderItem] = Field(min_length=1)

class OrderOut(BaseModel):
    id: int
    status: str
    total: float
    items: list
    payment_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
