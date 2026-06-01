from pydantic import BaseModel

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    category: str | None
    image_url: str | None

    model_config = {"from_attributes": True}

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    category: str | None = None
    image_url: str | None = None
