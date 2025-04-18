from typing import Optional

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


def get_clients(
    db: Session,
    name: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Client)

    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))

    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))

    return query.offset(skip).limit(limit).all()


def get_client_by_id(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()


def update_client(db: Session, client, name=None, email=None, cpf=None):
    if name:
        client.name = name
    if email:
        client.email = email
    if cpf:
        client.cpf = cpf

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client):
    db.delete(client)
    db.commit()
