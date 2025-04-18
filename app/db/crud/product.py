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
