import os
from decimal import Decimal
from typing import Optional

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from firebase_admin import auth

from ...dependencies import get_db, get_token_header
from ...db.schemas.products import (
    ProductCreateSchema,
    ProductListResponse,
    ProductListPaginatedResponse,
)
from ...utils.helper import firebase, logging
from ...db.crud import product as crud

dotenv.load_dotenv()

TEST = os.getenv("TEST")

router = APIRouter()


@router.post("/", dependencies=[Depends(get_token_header)])
async def create_product(
    product_data: ProductCreateSchema,
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Create a new product.
    E.g:

        {
            "description": "Produto A",
            "price": 99.99,
            "barcode": "1234567890123",
            "section": "Seção A",
            "stock": 100,
            "expiration_date": "31-12-2025",
            "images": ["image1.jpg", "image2.jpg"]
        }

    """
    description = product_data.description
    price = product_data.price
    barcode = product_data.barcode
    section = product_data.section
    stock = product_data.stock
    expiration_date = product_data.expiration_date
    images = product_data.images

    try:
        logging.info("Decoding firebase JWT token")
        decoded_token = auth.verify_id_token(jwt_token)

        logging.info(f"Inserting product into database")
        product = crud.create_product(
            db=db,
            created_by=decoded_token["uid"],
            description=description,
            price=price,
            barcode=barcode,
            section=section,
            stock=stock,
            expiration_date=expiration_date,
            images=images,
        )

        return JSONResponse(
            status_code=200,
            content={"message": "Produto criado com sucesso", "id": product.id},
        )

    except Exception as e:
        logging.error(f"Error creating product: {e}")
        raise HTTPException(status_code=400, detail="Erro ao criar o produto")


@router.get(
    "/",
    response_model=ProductListPaginatedResponse,
    dependencies=[Depends(get_token_header)],
)
async def list_products(
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    section: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
):
    """
    List products with pagination and filters.
    E.g:

        {
            "page": 1,
            "limit": 10,
            "section": "Seção A",
            "available": true,
            "min_price": 50.00,
            "max_price": 100.00
        }

    """
    try:
        logging.info("Decoding firebase JWT token")
        decoded_token = {"uid": jwt_token}

        if TEST != "ON":
            decoded_token = auth.verify_id_token(jwt_token)
        elif jwt_token != "test":
            raise auth.InvalidIdTokenError("Invalid JWT token")

        skip = (page - 1) * limit

        logging.info("Fetching products from database")
        products = crud.get_products(
            db=db,
            skip=skip,
            limit=limit,
            section=section,
            available=available,
            min_price=min_price,
            max_price=max_price,
        )

        return {
            "page": page,
            "limit": limit,
            "products": products,
        }

    except Exception as e:
        logging.error(f"Error listing products: {e}")
        raise HTTPException(status_code=400, detail="Erro ao listar produtos")
