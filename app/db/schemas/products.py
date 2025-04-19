from pydantic import BaseModel, ConfigDict, field_validator, field_serializer
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from datetime import date


class ProductCreateSchema(BaseModel):
    description: str
    price: Decimal
    barcode: str
    section: str
    stock: int = 0
    expiration_date: Optional[str] = None
    images: Optional[List[str]] = []

    @field_validator("expiration_date")
    @classmethod
    def validate_date(cls, v):
        if v is None:
            return None
        try:
            parsed_date = datetime.strptime(v, "%d-%m-%Y").date()
            return parsed_date
        except ValueError:
            raise ValueError("A data de validade deve estar no formato dd-mm-aaaa")

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    id: int
    description: str
    price: Decimal
    barcode: str
    section: str
    stock: int
    expiration_date: Optional[date] = None
    images: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)


class ProductListPaginatedResponse(BaseModel):
    page: int
    limit: int
    products: List[ProductListResponse]
