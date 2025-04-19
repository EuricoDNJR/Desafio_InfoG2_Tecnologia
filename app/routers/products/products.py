import os
from decimal import Decimal
from typing import Optional

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from firebase_admin import auth

from ...dependencies import get_db, get_token_header
from ...db.schemas.products import (
    ProductCreateSchema,
    ProductListPaginatedResponse,
    ProductUpdateRequest,
    ProductResponse,
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


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(get_token_header)],
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Get product by ID.
    """
    try:
        logging.info(f"Fetching product with ID {product_id} from database")

        product = crud.get_product_by_id(db=db, product_id=product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        return product

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logging.error(f"Error fetching product: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao buscar produto")


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(get_token_header)],
)
async def update_product(
    product_id: int,
    product_data: ProductUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Atualiza um produto específico.

    E.g:

        {
            "description": "eu mudei denovo",
            "price": 55.50,
            "barcode": "1111111111",
            "section": "mudada",
            "available": true,
            "expiration_date": "10/11/2027"
        }

    """
    try:
        logging.info(f"Updating product with ID {product_id}")
        product = crud.get_product_by_id(db=db, product_id=product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        updated_product = crud.update_product(
            db=db,
            product=product,
            description=product_data.description,
            price=product_data.price,
            section=product_data.section,
            available=product_data.available,
            expiration_date=product_data.expiration_date,
            barcode=product_data.barcode,
        )

        return updated_product

    except HTTPException as http_exc:
        raise http_exc

    except ValueError as ve:
        logging.error(f"Validation error: {ve}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        logging.error(f"Error updating product: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao atualizar produto")


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_token_header)],
)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Exclui um produto específico.
    """
    try:
        logging.info(f"Deleting product with ID {product_id}")
        deleted_product = crud.delete_product(db=db, product_id=product_id)
        if not deleted_product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        return

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logging.error(f"Error deleting product: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao excluir produto")
