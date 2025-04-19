from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreateRequest(BaseModel):
    client_id: int
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    description: str
    section: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    client_id: int
    status: str
    created_at: datetime
    total_value: float
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
