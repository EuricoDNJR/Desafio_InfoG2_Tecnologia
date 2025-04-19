from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.db.models.product import Product
from app.db.models.order import Order, OrderItem
from app.db.schemas.orders import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderUpdateRequest,
)
from datetime import datetime, timezone
from typing import Optional, List


def create_order(db: Session, order_data: OrderCreateRequest) -> OrderResponse:
    total_value = 0.0
    items_response = []

    # Verifica os produtos e calcula total
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Produto ID {item.product_id} não encontrado"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para o produto '{product.description}'",
            )

        total_value += product.price * item.quantity

    # Cria o pedido (base)
    order = Order(
        client_id=order_data.client_id,
        created_at=datetime.now(timezone.utc),
        status="pendente",
        total_value=total_value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Cria os itens e atualiza estoque
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        db_item = OrderItem(
            order_id=order.id, product_id=item.product_id, quantity=item.quantity
        )
        db.add(db_item)

        product.stock -= item.quantity

        # Adiciona à lista de resposta
        items_response.append(
            OrderItemResponse(
                product_id=product.id,
                quantity=item.quantity,
                price=product.price,
                description=product.description,
                section=product.section,
            )
        )

    db.commit()

    return OrderResponse(
        id=order.id,
        client_id=order.client_id,
        status=order.status,
        created_at=order.created_at,
        total_value=order.total_value,
        items=items_response,
    )


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    section: Optional[str] = None,
    order_id: Optional[int] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
) -> List[OrderResponse]:
    # Inicia a consulta base, carregando os itens e seus respectivos produtos com join
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    )
    # Filtros
    if order_id:
        query = query.filter(Order.id == order_id)

    if status:
        query = query.filter(Order.status == status)

    if client_id:
        query = query.filter(Order.client_id == client_id)

    if start_date:
        query = query.filter(Order.created_at >= start_date)

    if end_date:
        query = query.filter(Order.created_at <= end_date)

    if section:
        query = (
            query.join(Order.items)
            .join(OrderItem.product)
            .filter(Product.section == section)
        )

    # Aplica paginação e executa a query
    orders = query.offset(skip).limit(limit).all()

    # Monta a resposta formatada conforme o modelo OrderResponse
    results = []
    for order in orders:
        items = []
        for item in order.items:
            product = item.product
            items.append(
                OrderItemResponse(
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price,
                    description=product.description,
                    section=product.section,
                )
            )

        results.append(
            OrderResponse(
                id=order.id,
                client_id=order.client_id,
                status=order.status,
                created_at=order.created_at,
                total_value=order.total_value,
                items=items,
            )
        )

    return results


def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Busca os itens do pedido, já unindo com o produto para obter dados adicionais
    items = (
        db.query(OrderItem)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(OrderItem.order_id == order_id)
        .with_entities(
            OrderItem.product_id,
            OrderItem.quantity,
            Product.price,
            Product.description,
            Product.section,
        )
        .all()
    )

    # Estrutura os itens para se adequar ao schema de resposta
    order_dict = {
        "id": order.id,
        "client_id": order.client_id,
        "status": order.status,
        "created_at": order.created_at,
        "total_value": order.total_value,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
                "description": item.description,
                "section": item.section,
            }
            for item in items
        ],
    }

    return order_dict


def update_order(db: Session, order_id: int, data: OrderUpdateRequest):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Se houver itens para atualizar
    if data.items is not None:
        # Repor o estoque dos itens antigos
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
            db.delete(item)

        # Adicionar os novos itens
        total_value = 0
        for item in data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Produto {item.product_id} não encontrado"
                )
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para o produto {product.description}",
                )

            new_item = OrderItem(
                order_id=order.id, product_id=item.product_id, quantity=item.quantity
            )
            db.add(new_item)
            product.stock -= item.quantity
            total_value += product.price * item.quantity

        order.total_value = total_value

    # Atualiza client_id e status se forem fornecidos
    if data.client_id is not None:
        order.client_id = data.client_id

    if data.status is not None:
        order.status = data.status

    db.commit()
    db.refresh(order)

    # Recupera os dados atualizados com itens
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    return {
        "id": order.id,
        "client_id": order.client_id,
        "status": order.status,
        "created_at": order.created_at,
        "total_value": order.total_value,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.product.price,
                "description": item.product.description,
                "section": item.product.section,
            }
            for item in order_items
        ],
    }
