from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.product import Product
from app.db.models.order import Order, OrderItem
from app.db.schemas.orders import OrderCreateRequest, OrderItemResponse, OrderResponse
from datetime import datetime, timezone


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
