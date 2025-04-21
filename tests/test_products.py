import pytest
from app.db.models.user import User
from app.db.models.product import Product


@pytest.fixture(scope="function")
def fake_jwt_token():
    return "test"


@pytest.fixture(scope="function")
def valid_product_data():
    return {
        "description": "Produto Teste",
        "price": 19.90,
        "barcode": "1234567890123",
        "section": "Eletrônicos",
        "stock": 10,
        "expiration_date": "31-12-2025",
        "images": ["img1.jpg", "img2.jpg"],
    }


def test_create_product_success(client, valid_product_data, fake_jwt_token, db):
    """
    Testa a criação bem-sucedida de um produto
    """
    response = client.post(
        "/products/",
        json=valid_product_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Produto criado com sucesso"
    assert "id" in response.json()

    product_in_db = (
        db.query(Product)
        .filter(Product.barcode == valid_product_data["barcode"])
        .first()
    )
    assert product_in_db is not None
    assert product_in_db.description == valid_product_data["description"]


def test_get_product_success(client, fake_jwt_token, db):
    """
    Testa a recuperação bem-sucedida de um produto existente
    """

    product = Product(
        created_by="test",
        description="Notebook Gamer",
        price=4999.99,
        barcode="9876543210000",
        section="Informática",
        stock=5,
        expiration_date="2026-12-31",
        images=["notebook.jpg"],
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.get(
        f"/products/{product.id}",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product.id
    assert data["description"] == product.description
    assert data["barcode"] == product.barcode
    assert data["stock"] == product.stock


def test_get_product_not_found(client, fake_jwt_token):
    """
    Testa a recuperação de um produto inexistente
    """
    response = client.get("/products/999999", headers={"jwt-token": fake_jwt_token})
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"


def test_list_products_success(client, fake_jwt_token, db):
    """
    Testa a listagem de produtos com paginação e sem filtros
    """

    product1 = Product(
        created_by="test",
        description="Cadeira Gamer",
        price=899.90,
        barcode="000111222333",
        section="Móveis",
        stock=10,
        expiration_date=None,
        images=["cadeira.jpg"],
    )

    product2 = Product(
        created_by="test",
        description="Monitor 27''",
        price=1499.99,
        barcode="000111222444",
        section="Informática",
        stock=5,
        expiration_date=None,
        images=["monitor.jpg"],
    )

    db.add_all([product1, product2])
    db.commit()

    response = client.get(
        "/products/?page=1&limit=10",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["products"]) >= 2

    product_descriptions = [p["description"] for p in data["products"]]
    assert "Cadeira Gamer" in product_descriptions
    assert "Monitor 27''" in product_descriptions


def test_list_products_with_filters(client, fake_jwt_token, db):
    """
    Testa a listagem de produtos com filtros por seção e preço
    """

    product1 = Product(
        created_by="test",
        description="Produto A",
        price=50.00,
        barcode="1111111111",
        section="Seção Teste",
        stock=3,
        images=[],
    )
    product2 = Product(
        created_by="test",
        description="Produto B",
        price=200.00,
        barcode="2222222222",
        section="Outra Seção",
        stock=0,
        images=[],
    )

    db.add_all([product1, product2])
    db.commit()

    response = client.get(
        "/products/?section=Seção Teste&min_price=10&max_price=100&available=true",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["products"]) == 1
    assert data["products"][0]["description"] == "Produto A"


def test_update_product_success(client, fake_jwt_token, db):
    """
    Testa a atualização de um produto com dados válidos
    """

    product = Product(
        created_by="test",
        description="Produto Original",
        price=100.0,
        barcode="0000000000",
        section="Eletrônicos",
        stock=10,
        expiration_date=None,
        images=[],
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    update_data = {
        "description": "Produto Atualizado",
        "price": 199.99,
        "barcode": "1111111111",
        "section": "Atualizada",
        "available": True,
        "expiration_date": "10/11/2027",
    }

    response = client.put(
        f"/products/{product.id}",
        json=update_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Produto Atualizado"
    assert data["price"] == "199.99"
    assert data["barcode"] == "1111111111"
    assert data["section"] == "Atualizada"
    assert data["expiration_date"] == "2027-11-10"


def test_update_product_not_found(client, fake_jwt_token):
    """
    Testa tentativa de atualizar um produto inexistente
    """
    update_data = {
        "description": "Não importa",
        "price": 10.0,
        "expiration_date": "10/11/2030",
    }

    response = client.put(
        "/products/9999",
        json=update_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"


def test_delete_product_success(client, db):
    """
    Testa a exclusão de um produto existente com permissão de admin
    """

    # Cria o usuário admin de teste (caso ainda não exista)
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

    # Cria um produto para deletar
    product_obj = Product(
        created_by="test",
        description="Produto Deletável",
        price=49.99,
        barcode="9999999999",
        section="Teste",
        stock=10,
    )
    db.add(product_obj)
    db.commit()
    db.refresh(product_obj)

    # Realiza a exclusão
    response = client.delete(
        f"/products/{product_obj.id}",
        headers={"jwt-token": "test"},
    )

    assert response.status_code == 204

    # Verifica que o produto foi removido
    deleted = db.query(Product).filter_by(id=product_obj.id).first()
    assert deleted is None


def test_delete_product_not_found(client, db):
    """
    Testa a exclusão de um produto inexistente
    """

    # Garante que o usuário admin existe
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

    response = client.delete(
        "/products/9999",
        headers={"jwt-token": "test"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"
