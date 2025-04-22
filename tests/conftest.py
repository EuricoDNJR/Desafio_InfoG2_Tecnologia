import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_db

# URL de Conexão de Teste para o PostgreSQL (conectando-se ao test_db)
SQLALCHEMY_DATABASE_URL = (
    "postgresql://test_user:test_password@host.docker.internal:5433/test_db"
)

# Criando um engine de conexão para os testes
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})

# Criando uma session local de testes
SessionLocalTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db():
    """
    Fixture que fornece a sessão de banco de dados de teste.
    Cria as tabelas antes e limpa tudo depois de cada teste.
    """
    Base.metadata.create_all(bind=engine_test)
    db_session = SessionLocalTest()

    try:
        yield db_session
    finally:
        db_session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            db_session.execute(table.delete())
        db_session.commit()
        db_session.close()


@pytest.fixture(scope="function")
def client(db):
    """
    Fixture que fornece o TestClient com o banco de dados de teste injetado.
    """

    # Override do get_db para usar a session de teste
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
