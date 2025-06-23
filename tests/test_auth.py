from firebase_admin import auth

from app.db.models.user import User


def delete_firebase_user_by_email(email: str):
    try:
        user_record = auth.get_user_by_email(email)
        auth.delete_user(user_record.uid)
    except auth.UserNotFoundError:
        pass
    except Exception as e:
        print(f"Erro ao tentar excluir usuário do Firebase: {e}")


def test_register_user_success(client, db):
    """
    Testa o registro de um novo usuário
    """
    email = "testuser@example.com"
    # Limpa banco local e Firebase
    db.query(User).filter_by(email=email).delete()
    db.commit()
    delete_firebase_user_by_email(email)

    response = client.post(
        "/auth/register/",
        headers={"jwt-token": "test"},
        json={
            "name": "Usuário Teste",
            "email": email,
            "password": "senhaSegura123",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert "Conta de usuário criada com sucesso" in response.json()["message"]


def test_register_user_duplicate_email(client, db):
    """
    Testa o registro com email já existente
    """
    email = "existing@example.com"

    # Limpa banco local e Firebase
    db.query(User).filter_by(email=email).delete()
    db.commit()
    delete_firebase_user_by_email(email)

    # Cria o usuário localmente
    user = User(
        name="Usuário Existente",
        email=email,
        firebaseId="existing_firebase_id",
        role="user",
        firebaseIdWhoCreated="test",
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/auth/register/",
        headers={"jwt-token": "test"},
        json={
            "name": "Outro Nome",
            "email": email,
            "password": "senha123",
            "role": "user",
        },
    )

    assert response.status_code == 400
    assert (
        "Erro ao criar conta para o email existing@example.com Usuário já existe."
        in response.json()["detail"]
    )


def test_login_invalid_credentials(client):
    """
    Testa o login com credenciais inválidas
    """
    response = client.post(
        "/auth/login/",
        json={
            "email": "naoexiste@example.com",
            "password": "senhaerrada",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Credenciais inválidas"
