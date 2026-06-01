from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.user import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, paid, shipped, done
    total = Column(Float, nullable=False)
    items = Column(JSON, nullable=False)         # [{product_id, name, qty, price}]
    payment_id = Column(String, nullable=True)   # mock payment reference
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="orders")
