import pytest
from app.db.models.client import Client
from app.db.models.user import User


@pytest.fixture(scope="function")
def fake_jwt_token():
    return "test"


@pytest.fixture(scope="function")
def valid_client_data():
    return {"name": "João", "email": "joaocesar@gmail.com", "cpf": "006.444.280-23"}


@pytest.fixture(scope="function")
def existing_client_data():
    return {"name": "Maria", "email": "maria@gmail.com", "cpf": "006.444.280-23"}


def test_create_client_success(client, valid_client_data, fake_jwt_token, db):
    """
    Teste para verificar a criação de um cliente com dados válidos
    """
    response = client.post(
        "/clients/",
        json=valid_client_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Cliente criado com sucesso"
    assert "id" in response.json()

    client_in_db = (
        db.query(Client).filter(Client.email == valid_client_data["email"]).first()
    )
    assert client_in_db is not None


def test_get_client_by_id_success(client, db, fake_jwt_token):
    """
    Testa a recuperação de um cliente existente pelo ID
    """
    # Cria um cliente diretamente no banco de dados
    new_client = Client(
        name="Ana",
        email="ana@gmail.com",
        cpf="067.574.850-01",
        firebaseIdWhoCreated="test",
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    # Faz a requisição para buscar o cliente
    response = client.get(
        f"/clients/{new_client.id}",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    assert response.json()["id"] == new_client.id
    assert response.json()["name"] == "Ana"
    assert response.json()["email"] == "ana@gmail.com"
    assert response.json()["cpf"] == "067.574.850-01"


def test_get_client_by_id_not_found(client, fake_jwt_token):
    """
    Testa a tentativa de buscar um cliente inexistente
    """
    response = client.get(
        "/clients/999999",  # ID que provavelmente não existe
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cliente não encontrado"


def test_list_clients_success(client, db, fake_jwt_token):
    """
    Testa listagem de clientes com sucesso (sem filtros)
    """
    # Cria dois clientes no banco
    client1 = Client(
        name="Carlos",
        email="carlos@example.com",
        cpf="231.131.070-40",
        firebaseIdWhoCreated="test",
    )
    client2 = Client(
        name="Ana",
        email="ana@example.com",
        cpf="060.448.170-59",
        firebaseIdWhoCreated="test",
    )
    db.add_all([client1, client2])
    db.commit()

    response = client.get(
        "/clients/",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert isinstance(data["clients"], list)
    assert len(data["clients"]) >= 2  # Pode haver mais se o banco já tiver clientes
    emails = [client["email"] for client in data["clients"]]
    assert "carlos@example.com" in emails
    assert "ana@example.com" in emails


def test_list_clients_with_filters(client, db, fake_jwt_token):
    """
    Testa listagem com filtro por nome e email
    """
    client1 = Client(
        name="Beatriz",
        email="bia@example.com",
        cpf="429.255.270-35",
        firebaseIdWhoCreated="test",
    )
    db.add(client1)
    db.commit()

    response = client.get(
        "/clients/?name=Beatriz&email=bia@example.com",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10
    assert len(data["clients"]) >= 1
    assert data["clients"][0]["name"] == "Beatriz"
    assert data["clients"][0]["email"] == "bia@example.com"


def test_list_clients_empty_result(client, db, fake_jwt_token):
    """
    Testa listagem que não retorna resultados
    """
    response = client.get(
        "/clients/?name=Inexistente",
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["clients"] == []


def test_update_client_success(client, db, fake_jwt_token):
    """
    Testa atualização de cliente com dados válidos
    """
    # Cria cliente inicial
    client_obj = Client(
        name="Marcos",
        email="marcos@example.com",
        cpf="246.322.610-25",
        firebaseIdWhoCreated="test",
    )
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    updated_data = {
        "name": "Marcos Silva Atualizado",
        "email": "marcos.silva.atualizado@example.com",
        "cpf": "929.291.820-67",
    }

    response = client.put(
        f"/clients/{client_obj.id}",
        json=updated_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cliente atualizado com sucesso"
    assert data["id"] == client_obj.id

    # Verifica no banco
    updated_client = db.query(Client).get(client_obj.id)
    assert updated_client.name == "Marcos Silva Atualizado"
    assert updated_client.email == "marcos.silva.atualizado@example.com"


def test_update_client_not_found(client, db, fake_jwt_token):
    """
    Testa tentativa de atualização de cliente inexistente
    """
    updated_data = {
        "name": "Ghost",
        "email": "ghost@example.com",
        "cpf": "386.134.490-42",
    }

    response = client.put(
        "/clients/9999",
        json=updated_data,
        headers={"jwt-token": fake_jwt_token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Cliente não encontrado"


def test_delete_client_success(client, db):
    """
    Testa a exclusão de um cliente existente com permissão de admin
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

    # Cria um cliente que será deletado
    client_obj = Client(
        name="Carlos Deletável",
        email="carlos.delete@example.com",
        cpf="171.634.060-88",
        firebaseIdWhoCreated="test",
    )
    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    # Realiza a exclusão
    response = client.delete(
        f"/clients/{client_obj.id}",
        headers={"jwt-token": "test"},
    )

    assert response.status_code == 204

    # Verifica que o cliente foi removido
    deleted = db.query(Client).filter_by(id=client_obj.id).first()
    assert deleted is None
