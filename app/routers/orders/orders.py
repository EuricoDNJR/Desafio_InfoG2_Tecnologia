import os
from decimal import Decimal
from typing import Optional
from datetime import datetime
import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from firebase_admin import auth

from ...dependencies import get_db, get_token_header, get_current_user_with_role
from ...db.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    PaginatedOrderResponse,
    OrderUpdateRequest,
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


@router.get(
    "/",
    response_model=PaginatedOrderResponse,
    dependencies=[Depends(get_token_header)],
)
def list_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    section: Optional[str] = Query(None),
    order_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
):
    """
    List orders with pagination and filters.

    E.g:

            {
                "page": 1,
                "limit": 10,
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-12-31T23:59:59",
                "section": "A",
                "order_id": 1,
                "status": "pendente",
                "client_id": 1,
            }

    """
    try:
        skip = (page - 1) * limit
        orders = crud.get_orders(
            db=db,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            section=section,
            order_id=order_id,
            status=status,
            client_id=client_id,
        )

        return {"page": page, "limit": limit, "orders": orders}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar pedidos")


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    dependencies=[Depends(get_token_header)],
)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de um pedido específico.
    """
    try:
        logging.info(f"Fetching order {order_id}")
        order = crud.get_order_by_id(db, order_id)
        return order

    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(f"Erro ao buscar pedido {order_id}: {e}")
        raise HTTPException(status_code=400, detail="Erro ao buscar pedido")


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    dependencies=[Depends(get_token_header)],
)
async def update_order(
    order_id: int, data: OrderUpdateRequest, db: Session = Depends(get_db)
):
    """
    Atualiza informações de um pedido, incluindo itens, cliente e status.

    E.g:

            {
                "client_id": 1,
                "status": "concluido",
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
        updated_order = crud.update_order(db, order_id, data)
        return updated_order
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Erro ao atualizar pedido: {e}")
        raise HTTPException(status_code=400, detail="Erro ao atualizar pedido")


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user_with_role("admin"))],  # Role "admin"
)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    """
    Exclui um pedido específico.
    """
    try:
        logging.info(f"Deleting order with ID {order_id}")
        deleted_order = crud.delete_order(db=db, order_id=order_id)
        if not deleted_order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        return

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logging.error(f"Erro ao excluir pedido: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao excluir pedido")
