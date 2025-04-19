from typing import Optional

from sqlalchemy.orm import Session
from app.db.models.product import Product


def create_product(
    db: Session,
    created_by: str,
    description: str,
    price: float,
    barcode: str,
    section: str,
    stock: int,
    expiration_date=None,
    images: list[str] = [],
):
    new_product = Product(
        created_by=created_by,
        description=description,
        price=price,
        barcode=barcode,
        section=section,
        stock=stock,
        expiration_date=expiration_date,
        images=images,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    section: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available: Optional[bool] = None,
):
    query = db.query(Product)

    if section:
        query = query.filter(Product.section.ilike(f"%{section}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if available is True:
        query = query.filter(Product.stock > 0)
    elif available is False:
        query = query.filter(Product.stock <= 0)

    return query.offset(skip).limit(limit).all()
