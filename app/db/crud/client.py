from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.client import Client


def create_client(
    db: Session,
    firebaseIdWhoCreated: str,
    name: str,
    email: str,
    cpf: str,
) -> Client:
    db_client = Client(
        firebaseIdWhoCreated=firebaseIdWhoCreated,
        name=name,
        email=email,
        cpf=cpf,
    )
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except IntegrityError:
        db.rollback()
        raise ValueError("Cliente já existe.")
