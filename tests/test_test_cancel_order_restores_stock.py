def test_cancel_order_restores_stock(client, db):
    # 1. Criar cliente
    client_data = {
        "name": "Cliente Cancelamento",
        "email": "cancelamento@example.com",
        "cpf": "037.845.990-28",
    }
    response = client.post("/clients/", json=client_data, headers={"jwt-token": "test"})
    assert response.status_code == 201
    client_id = response.json()["id"]

    # 2. Criar produto
    product_data = {
        "description": "Produto Cancelável",
        "price": 30.0,
        "barcode": "9999999999999",
        "section": "Teste",
        "stock": 5,
        "expiration_date": "31-12-2025",
        "images": [],
    }
    response = client.post(
        "/products/", json=product_data, headers={"jwt-token": "test"}
    )
    assert response.status_code == 201
    product = response.json()
    product_id = product["id"]

    # 3. Criar pedido
    order_data = {
        "client_id": client_id,
        "items": [{"product_id": product_id, "quantity": 2}],
    }
    response = client.post("/orders/", json=order_data, headers={"jwt-token": "test"})
    assert response.status_code == 201
    order = response.json()
    order_id = order["id"]

    # 4. Confirmar estoque foi reduzido
    response = client.get(f"/products/{product_id}", headers={"jwt-token": "test"})
    assert response.status_code == 200
    assert response.json()["stock"] == 3  # 5 - 2

    # 5. Atualizar status para cancelado
    update_data = {"status": "cancelado"}
    response = client.put(
        f"/orders/{order_id}", json=update_data, headers={"jwt-token": "test"}
    )
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["status"] == "cancelado"

    # 6. Verificar que o estoque foi restaurado
    response = client.get(f"/products/{product_id}", headers={"jwt-token": "test"})
    assert response.status_code == 200
    assert response.json()["stock"] == 5  # restaurado

    # 7. Verificar que o pedido ainda existe
    response = client.get(f"/orders/{order_id}", headers={"jwt-token": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "cancelado"
