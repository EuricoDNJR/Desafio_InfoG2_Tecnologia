import os

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from firebase_admin import auth

from ...dependencies import get_db, get_token_header
from ...db.schemas.users import SignUpSchema, LoginSchema
from ...utils.helper import firebase, logging
from ...db.crud import user as crud


dotenv.load_dotenv()

TEST = os.getenv("TEST")

router = APIRouter()


@router.post("/register/", dependencies=[Depends(get_token_header)])
async def create_an_account(
    user_data: SignUpSchema, jwt_token: str = Header(...), db: Session = Depends(get_db)
):
    """
    Create an account for the user.
    E.g:

        {
            "name": "João",
            "email": "joaocesar@gmail.com",
            "password": "bombadorato1",
            "role": "admin"
        }

    """
    email = user_data.email
    password = user_data.password
    role = user_data.role
    name = user_data.name

    try:
        user = auth.create_user(email=email, password=password)

        logging.info("Decoding firebase JWT token")
        decoded_token = {"uid": jwt_token}

        if TEST != "ON":
            decoded_token = auth.verify_id_token(jwt_token)

        elif jwt_token != "test":
            raise auth.InvalidIdTokenError("Invalid JWT token")

        logging.info(f"Firebase JWT Token decoded")

        logging.info("Inserting user into database")
        user = crud.create_user(
            db=db,
            firebaseId=user.uid,
            firebaseIdWhoCreated=decoded_token["uid"],
            email=email,
            role=role,
            name=name,
        )
        logging.info("User inserted into database")

        return JSONResponse(
            content={
                "message": f"Conta de usuário criada com sucesso para o usuário {user.id}"
            },
            status_code=201,
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400, detail=f"Conta já criada para o email {email}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao criar conta para o email {email} {e}"
        )


@router.post("/login/")
async def create_access_token(user_data: LoginSchema):
    """
    Create an access token for the user.
    E.g:

        {
            "email": "joaocesar@gmail.com",
            "password": "bombadorato1"
        }
    """
    email = user_data.email
    password = user_data.password

    try:
        user = firebase.auth().sign_in_with_email_and_password(
            email=email, password=password
        )

        token = user["idToken"]
        refresh_token = user["refreshToken"]
        expires_in = user.get("expiresIn", "3600")

        return JSONResponse(
            content={
                "token": token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            },
            status_code=200,
        )

    except:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")


@router.post("/refresh-token/")
async def refresh_token(jwt_refresh_token: str = Header(...)):
    """
    Refresh the access token for the user.
    """
    try:
        logging.info("Refreshing Firebase token")
        refreshed_user = firebase.auth().refresh(jwt_refresh_token)

        return JSONResponse(
            content={
                "access_token": refreshed_user["idToken"],
                "refresh_token": refreshed_user["refreshToken"],
                "expires_in": refreshed_user.get("expiresIn", 3600),
            },
            status_code=200,
        )

    except Exception as e:
        logging.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar o token: {e}")
