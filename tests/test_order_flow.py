def test_full_order_flow(client):
    # 1. Criar cliente
    client_data = {
        "name": "Pedro Silva",
        "email": "pedrosilva@gmail.com",
        "cpf": "905.106.940-55",
    }
    response = client.post("/clients/", json=client_data, headers={"jwt-token": "test"})
    assert response.status_code == 201
    client_id = response.json()["id"]

    # 2. Criar produto
    product_data = {
        "description": "Produto Teste Flow",
        "price": 50.0,
        "barcode": "1234567890444",
        "section": "Eletrônicos",
        "stock": 10,
        "expiration_date": "31-12-2025",
        "images": ["img1.jpg", "img2.jpg"],
    }
    response = client.post(
        "/products/", json=product_data, headers={"jwt-token": "test"}
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    # 3. Criar pedido
    order_data = {
        "client_id": client_id,
        "items": [{"product_id": product_id, "quantity": 2}],
    }
    response = client.post("/orders/", json=order_data, headers={"jwt-token": "test"})
    assert response.status_code == 201
    order = response.json()
    assert order["client_id"] == client_id
    assert order["total_value"] == 100.0  # 2 x 50.0

    # 4. Verificar estoque foi atualizado
    response = client.get(f"/products/{product_id}", headers={"jwt-token": "test"})
    assert response.status_code == 200
    product = response.json()
    assert product["stock"] == 8  # 10 - 2

    # 5. Verifica pedido salvo
    response = client.get(f"/orders/{order['id']}", headers={"jwt-token": "test"})
    assert response.status_code == 200
    order_details = response.json()
    assert len(order_details["items"]) == 1
    assert order_details["items"][0]["product_id"] == product_id
    assert order_details["items"][0]["quantity"] == 2
