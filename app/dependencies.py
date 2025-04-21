import os

import dotenv
from fastapi import Header, HTTPException, status, Depends
from firebase_admin import auth
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.database import SessionLocal
from app.db.crud.user import get_user_by_firebase_id

dotenv.load_dotenv()

TEST = os.getenv("TEST")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_token_header(jwt_token: str = Header()):
    try:
        if TEST == "ON":
            if jwt_token != "test":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid JWT token"
                )

            return "test"

        decoded_token = auth.verify_id_token(jwt_token)
        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid JWT token"
            )

        return decoded_token

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token"
        )


def get_current_user_with_role(required_role: str):
    async def _get_user(jwt_token: str = Header(...), db: Session = Depends(get_db)):
        try:
            if TEST == "ON":
                # Retorna um usuário admin de teste direto do banco
                user = db.query(User).filter(User.firebaseId == "test").first()
                if not user:
                    # Cria um se não existir
                    user = User(
                        name="Test Admin",
                        email="admin@test.com",
                        firebaseId="test",
                        role=required_role,
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                return user

            # Fluxo normal com autenticação real
            decoded_token = auth.verify_id_token(jwt_token)
            uid = decoded_token["uid"]

            user = get_user_by_firebase_id(db, firebaseId=uid)
            if not user:
                raise HTTPException(status_code=401, detail="Usuário não encontrado")

            if user.role != required_role:
                raise HTTPException(status_code=403, detail="Permissão negada")

            return user

        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

    return _get_user
