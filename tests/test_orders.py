import pytest
from app.db.models.client import Client
from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.order import Order, OrderItem

from datetime import datetime, timezone


@pytest.fixture(scope="function")
def fake_jwt_token():
    return "test"


# @pytest.fixture(scope="function")
# def create_test_user(db):
#     user = db.query(User).filter_by(firebaseId="test").first()
#     if not user:
#         user = User(
#             name="Test User",
#             email="user@test.com",
#             firebaseId="test",
#             role="user",
#             firebaseIdWhoCreated="test",
#         )
#         db.add(user)
#         db.commit()
#     return user


@pytest.fixture(scope="function")
def create_test_client(db):
    client_obj = Client(
        name="Cliente Pedido",
        email="cliente.pedido@example.com",
        cpf="632.716.600-85",
        firebaseIdWhoCreated="test",
    )
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)
    return client_obj.id


@pytest.fixture(scope="function")
def create_test_client2(db):
    client_obj = Client(
        name="Cliente Pedido2",
        email="cliente.pedido2@example.com",
        cpf="062.774.120-78",
        firebaseIdWhoCreated="test",
    )
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)
    return client_obj.id


@pytest.fixture(scope="function")
def create_test_products(db):
    product1 = Product(
        created_by="test",
        description="Produto 1",
        price=10.0,
        barcode="1111111111",
        section="A",
        stock=10,
    )
    product2 = Product(
        created_by="test",
        description="Produto 2",
        price=20.0,
        barcode="2222222222",
        section="B",
        stock=5,
    )
    db.add_all([product1, product2])
    db.commit()
    db.refresh(product1)
    db.refresh(product2)
    return [product1, product2]


@pytest.fixture(scope="function")
def create_test_orders(db, create_test_client, create_test_products):
    """
    Cria pedidos de teste com itens para serem usados nos testes de listagem.
    """
    client_id = create_test_client  # Recebe o id do cliente
    products = create_test_products  # Lista de objetos Product

    # Criação de um pedido
    order = Order(
        client_id=client_id,  # Usa o id do cliente diretamente
        created_at=datetime.now(timezone.utc),
        status="pendente",
        total_value=sum([product.price * 2 for product in products]),
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Criando os itens do pedido
    for product in products:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
        )
        db.add(order_item)
        db.commit()

    db.refresh(order)  # Garantir que a relação esteja atualizada
    return [order]  # Retorna a lista de pedidos criados


def test_create_order_success(
    client,
    db,
    fake_jwt_token,
    create_test_client,
    create_test_products,
):
    """
    Testa a criação bem-sucedida de um pedido com múltiplos produtos
    """
    payload = {
        "client_id": create_test_client,
        "items": [
            {"product_id": create_test_products[0].id, "quantity": 2},
            {"product_id": create_test_products[1].id, "quantity": 1},
        ],
    }

    response = client.post(
        "/orders/",
        json=payload,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 201
    assert "id" in response.json()

    # Verifica no banco
    order = db.query(Order).filter_by(id=response.json()["id"]).first()
    assert order is not None
    assert order.client_id == create_test_client
    assert len(order.items) == 2
    assert order.total_value == 10.0 * 2 + 20.0 * 1


def test_get_order_success(
    client,
    db,
    fake_jwt_token,
    create_test_client,
    create_test_products,
):
    """
    Testa a recuperação bem-sucedida de um pedido existente
    """
    # Cria o pedido
    order = Order(
        client_id=create_test_client,
        status="pendente",
        total_value=0.0,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Adiciona os itens ao pedido
    total = 0
    for product in create_test_products:
        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
        )
        db.add(item)
        total += product.price * 2
    order.total_value = total
    db.commit()

    # Chama o endpoint
    response = client.get(
        f"/orders/{order.id}",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == order.id
    assert data["client_id"] == create_test_client
    assert data["status"] == "pendente"
    assert data["total_value"] == pytest.approx(total)
    assert len(data["items"]) == len(create_test_products)

    for item in data["items"]:
        assert "product_id" in item
        assert "quantity" in item
        assert "price" in item
        assert "description" in item
        assert "section" in item


def test_get_order_not_found(client, fake_jwt_token):
    """
    Testa a tentativa de recuperar um pedido inexistente
    """
    response = client.get(
        "/orders/999999",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido não encontrado"


def test_list_orders_basic(client, fake_jwt_token, create_test_orders):
    """
    Testa a listagem de pedidos com paginação básica
    """

    # Realiza a requisição para listar os pedidos
    response = client.get(
        "/orders/?page=1&limit=10",
        headers={"jwt-token": fake_jwt_token},
    )

    # Verifica se o código de status da resposta é 200 (OK)
    assert response.status_code == 200

    # Obtém os dados da resposta
    data = response.json()

    # Verifica se os campos "orders", "page", e "limit" estão presentes na resposta
    assert "orders" in data
    assert "page" in data and data["page"] == 1
    assert "limit" in data and data["limit"] == 10

    # Verifica se a chave "orders" é uma lista
    assert isinstance(data["orders"], list)

    # Verifica se há pelo menos um pedido na resposta
    assert len(data["orders"]) >= 1

    # Verifica se os campos de cada pedido estão presentes e corretos
    for order in data["orders"]:
        assert "id" in order
        assert "status" in order
        assert "client_id" in order
        assert "created_at" in order  # Caso exista um campo de data de criação
        # Verificar outros campos relevantes do pedido, como items, etc.

    # Caso o `create_test_orders` tenha criado um pedido com um status específico ou cliente,
    # você pode verificar se esse pedido está na resposta.
    order_ids = [order["id"] for order in data["orders"]]
    assert (
        create_test_orders[0].id in order_ids
    )  # Verifica se o pedido criado está na lista


def test_list_orders_with_filters(client, fake_jwt_token, create_test_orders):
    """
    Testa a listagem de pedidos com filtros aplicados (status e client_id)
    """

    # Pegamos dados do pedido de teste criado
    test_order = create_test_orders[0]
    status = test_order.status
    client_id = test_order.client_id

    # Realiza a requisição para listar os pedidos com filtros
    response = client.get(
        f"/orders/?page=1&limit=10&status={status}&client_id={client_id}",
        headers={"jwt-token": fake_jwt_token},
    )

    # Verifica se o código de status da resposta é 200 (OK)
    assert response.status_code == 200

    # Obtém os dados da resposta
    data = response.json()

    # Verifica se os campos "orders", "page", e "limit" estão presentes na resposta
    assert "orders" in data
    assert "page" in data and data["page"] == 1
    assert "limit" in data and data["limit"] == 10

    # Verifica se a chave "orders" é uma lista
    assert isinstance(data["orders"], list)

    # Garante que todos os pedidos retornados têm o status e client_id filtrados
    for order in data["orders"]:
        assert order["status"] == status
        assert order["client_id"] == client_id
        assert "id" in order
        assert "created_at" in order  # Se esse campo existir


def test_update_order(
    client,
    fake_jwt_token,
    create_test_orders,
    create_test_products,
    create_test_client2,
):
    """
    Testa a atualização de um pedido existente
    """
    # Pedido e produtos existentes criados pelos fixtures
    order = create_test_orders[0]
    product_1 = create_test_products[0]
    product_2 = create_test_products[1]
    new_client = create_test_client2  # Cliente diferente do original

    payload = {
        "client_id": new_client,
        "status": "concluido",
        "items": [
            {"product_id": product_1.id, "quantity": 1},
            {"product_id": product_2.id, "quantity": 2},
        ],
    }

    response = client.put(
        f"/orders/{order.id}",
        json=payload,
        headers={"jwt-token": fake_jwt_token},
    )

    # Verifica se a atualização foi bem-sucedida
    assert response.status_code == 200
    data = response.json()

    # Verifica se os campos foram atualizados corretamente
    assert data["id"] == order.id
    assert data["client_id"] == new_client
    assert data["status"] == "concluido"
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 2

    # Verifica os dados dos itens retornados
    product_ids = [item["product_id"] for item in data["items"]]
    assert product_1.id in product_ids
    assert product_2.id in product_ids


def test_update_order_with_invalid_product(client, fake_jwt_token, create_test_orders):
    """
    Testa atualização de pedido com um produto inexistente
    """
    order = create_test_orders[0]

    payload = {
        "items": [{"product_id": 9999, "quantity": 1}]  # ID de produto que não existe
    }

    response = client.put(
        f"/orders/{order.id}",
        json=payload,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 404
    data = response.json()
    assert "Produto" in data["detail"]


def test_update_order_with_insufficient_stock(
    client, fake_jwt_token, create_test_orders, create_test_products
):
    """
    Testa atualização de pedido com quantidade além do estoque disponível
    """
    order = create_test_orders[0]
    product = create_test_products[0]

    payload = {
        "items": [
            {
                "product_id": product.id,
                "quantity": product.stock + 10,
            }  # Quantidade além do estoque
        ]
    }

    response = client.put(
        f"/orders/{order.id}",
        json=payload,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 400
    data = response.json()
    assert "Estoque insuficiente" in data["detail"]


def test_delete_order_success(client, db, create_test_orders):
    """
    Testa a exclusão de um pedido existente com permissão de admin
    """

    # Garante que o usuário admin "test" existe
    admin_user = db.query(User).filter_by(firebaseId="test").first()
    if not admin_user:
        admin_user = User(
            name="Test Admin",
            email="admin@test.com",
            firebaseId="test",
            role="admin",
            firebaseIdWhoCreated="test",
        )
        db.add(admin_user)
        db.commit()

    # Cria um pedido para deletar (usando fixture existente)
    order_to_delete = create_test_orders[0]

    # Realiza a exclusão
    response = client.delete(
        f"/orders/{order_to_delete.id}",
        headers={"jwt-token": "test"},  # JWT mockado com role admin
    )

    assert response.status_code == 204

    # Verifica se o pedido foi realmente excluído do banco
    deleted = db.query(Order).filter(Order.id == order_to_delete.id).first()
    assert deleted is None


def test_delete_order_not_found(client, db):
    """
    Testa a exclusão de um pedido que não existe
    """

    # Garante que o usuário admin "test" existe
    admin_user = db.query(User).filter_by(firebaseId="test").first()
    if not admin_user:
        admin_user = User(
            name="Test Admin",
            email="admin@test.com",
            firebaseId="test",
            role="admin",
            firebaseIdWhoCreated="test",
        )
        db.add(admin_user)
        db.commit()

    # ID de pedido inexistente
    nonexistent_id = 9999

    response = client.delete(
        f"/orders/{nonexistent_id}",
        headers={"jwt-token": "test"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido não encontrado"
