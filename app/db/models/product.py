from sqlalchemy import Column, Integer, String, Float, Date, Text
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base


from sqlalchemy import Column, Integer, String, Float, Date, ARRAY
from sqlalchemy.orm import validates
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_by = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, unique=True, nullable=False)
    section = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    expiration_date = Column(Date, nullable=True)
    images = Column(ARRAY(String), default=[])

    @validates("price")
    def validate_price(self, key, value):
        if value < 0:
            raise ValueError("O preço deve ser um valor positivo")
        return value

    @validates("stock")
    def validate_stock(self, key, value):
        if value < 0:
            raise ValueError("O estoque deve ser um valor positivo")
        return value
