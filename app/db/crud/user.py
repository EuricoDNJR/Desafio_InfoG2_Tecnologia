from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.user import User


def create_user(
    db: Session,
    firebaseId: str,
    firebaseIdWhoCreated: str,
    name: str,
    email: str,
    role: str = "user",
) -> User:
    db_user = User(
        firebaseId=firebaseId,
        firebaseIdWhoCreated=firebaseIdWhoCreated,
        name=name,
        email=email,
        role=role,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Usuário já existe.")
