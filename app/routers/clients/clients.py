import os
from typing import List

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from firebase_admin import auth

from app.db.schemas.clients import ClientOut

from ...dependencies import get_db, get_token_header
from ...db.schemas.clients import ClientSchema, ClientListResponse
from ...utils.helper import firebase, logging
from ...db.crud import client as crud

dotenv.load_dotenv()

TEST = os.getenv("TEST")

router = APIRouter()


@router.post("/", dependencies=[Depends(get_token_header)])
async def create_an_client(
    client_data: ClientSchema,
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Create an client.
    E.g:

        {
            "name": "João",
            "email": "joaocesar@gmail.com",
            "cpf": "12345678901"
        }
    """
    name = client_data.name
    email = client_data.email
    cpf = client_data.cpf

    try:
        logging.info("Decoding firebase JWT token")
        decoded_token = {"uid": jwt_token}

        if TEST != "ON":
            decoded_token = auth.verify_id_token(jwt_token)

        elif jwt_token != "test":
            raise auth.InvalidIdTokenError("Invalid JWT token")

        logging.info(f"Firebase JWT Token decoded")

        logging.info("Inserting client into database")
        client = crud.create_client(
            db=db,
            firebaseIdWhoCreated=decoded_token["uid"],
            name=name,
            email=email,
            cpf=cpf,
        )

        return JSONResponse(
            status_code=200,
            content={"message": "Cliente criado com sucesso", "id": client.id},
        )

    except Exception as e:
        logging.error(f"Error creating client: {e}")
        raise HTTPException(status_code=400, detail="Erro ao criar o cliente")

    except IntegrityError as e:
        logging.error(f"Integrity error: {e}")
        raise HTTPException(status_code=400, detail="Email ou CPF já cadastrado")


@router.get(
    "/",
    response_model=List[ClientListResponse],
    dependencies=[Depends(get_token_header)],
)
async def list_clients(
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    name: str = Query(None),
    email: str = Query(None),
):
    """
    List clients with pagination and filter.
    E.g:

        {
            "page": 1,
            "limit": 10,
            "name": "João",
            "email": "joaocesar2@gmail.com"
        }
    """
    logging.info("Listing clients")
    try:

        logging.info("Decoding firebase JWT token")
        decoded_token = {"uid": jwt_token}

        if TEST != "ON":
            decoded_token = auth.verify_id_token(jwt_token)

        elif jwt_token != "test":
            raise auth.InvalidIdTokenError("Invalid JWT token")

        logging.info(f"Firebase JWT Token decoded")

        skip = (page - 1) * limit  # Pular os registros já retornados

        logging.info("Fetching clients from database")
        clients = crud.get_clients(
            db=db,
            skip=skip,
            limit=limit,
            name=name,
            email=email,
        )

        return clients

    except Exception as e:
        logging.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=400, detail="Erro ao listar clientes")
