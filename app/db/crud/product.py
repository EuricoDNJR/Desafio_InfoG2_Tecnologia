from typing import Optional

from sqlalchemy.orm import Session
from datetime import datetime

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


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(
    db: Session,
    product,
    description: Optional[str] = None,
    price: Optional[float] = None,
    section: Optional[str] = None,
    available: Optional[bool] = None,
    expiration_date: Optional[str] = None,
    barcode: Optional[str] = None,
):
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if section is not None:
        product.section = section
    if available is not None:
        product.available = available
    if expiration_date is not None:
        try:
            product.expiration_date = datetime.strptime(
                expiration_date, "%d/%m/%Y"
            ).date()
        except ValueError:
            raise ValueError("Data de expiração inválida. Use o formato dd/mm/aaaa.")
    if barcode:
        product.barcode = barcode

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    db.delete(product)
    db.commit()
    return product
