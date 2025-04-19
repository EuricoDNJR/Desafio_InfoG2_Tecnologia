import os
from decimal import Decimal
from typing import Optional

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from firebase_admin import auth

from ...dependencies import get_db, get_token_header
from ...db.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
)
from ...utils.helper import firebase, logging
from ...db.crud import order as crud

dotenv.load_dotenv()

TEST = os.getenv("TEST")

router = APIRouter()


@router.post(
    "/", response_model=OrderResponse, dependencies=[Depends(get_token_header)]
)
def create_order(order_data: OrderCreateRequest, db: Session = Depends(get_db)):
    """
    Cria um novo pedido com múltiplos produtos.
    E.g:

        {
            "client_id": 1,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2
                },
                {
                    "product_id": 2,
                    "quantity": 1
                }
            ]
        }

    """
    try:
        logging.info(f"Creating order for client {order_data.client_id}")
        order = crud.create_order(db=db, order_data=order_data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Pedido criado com sucesso",
                "order_id": order.id,
            },
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Erro ao criar pedido: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao criar pedido")
