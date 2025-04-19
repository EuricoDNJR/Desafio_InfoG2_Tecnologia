import os
from typing import Optional

import dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from firebase_admin import auth

from ...dependencies import get_db, get_token_header
from ...db.schemas.clients import (
    ClientSchema,
    ClientListResponse,
    ClientUpdateSchema,
    ClientListPaginatedResponse,
)
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
    response_model=ClientListPaginatedResponse,
    dependencies=[Depends(get_token_header)],
)
async def list_clients(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    """
    List clients with pagination and filter.
    E.g:

        {
            "page": 1,
            "limit": 10,
            "name": "João",
            "email": "",
        }

    """
    try:

        skip = (page - 1) * limit
        logging.info("Fetching clients from database")
        clients = crud.get_clients(
            db=db,
            skip=skip,
            limit=limit,
            name=name,
            email=email,
        )

        return {
            "page": page,
            "limit": limit,
            "clients": clients,
        }

    except Exception as e:
        logging.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=400, detail="Erro ao listar clientes")


@router.get(
    "/{client_id}",
    response_model=ClientListResponse,
    dependencies=[Depends(get_token_header)],
)
async def get_client_by_id(
    client_id: int,
    db: Session = Depends(get_db),
):
    """
    Get client by ID
    """
    try:

        logging.info(f"Fetching client with ID {client_id} from database")
        client = crud.get_client_by_id(db=db, client_id=client_id)

        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        return client

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logging.error(f"Error fetching client: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao buscar cliente")


@router.put(
    "/{client_id}",
    dependencies=[Depends(get_token_header)],
)
async def update_client(
    client_id: int,
    client_data: ClientUpdateSchema,
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Update client by ID
    E.g:

        {
            "name": "Joãozin",
            "email": "joazinreload@gmail.com",
            "cpf": "12345678901",
        }
    """

    try:

        client = crud.get_client_by_id(db=db, client_id=client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        updated_client = crud.update_client(
            db=db,
            client=client,
            name=client_data.name,
            email=client_data.email,
            cpf=client_data.cpf,
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Cliente atualizado com sucesso",
                "id": updated_client.id,
            },
        )

    except HTTPException as http_exc:
        raise http_exc

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email ou CPF já cadastrado")

    except Exception as e:
        logging.error(f"Erro ao atualizar cliente: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao atualizar cliente")


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_token_header)],
)
async def delete_client(
    client_id: int,
    jwt_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Delete a client by ID.
    """
    try:
        logging.info("Decoding Firebase JWT token")
        decoded_token = auth.verify_id_token(jwt_token)
        user_id = decoded_token.get("uid")

        logging.info(f"User {user_id} requested deletion of client ID {client_id}")

        client = crud.get_client_by_id(db=db, client_id=client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        crud.delete_client(db=db, client=client)

        logging.info(f"Client ID {client_id} deleted by user {user_id}")
        return

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logging.error(f"Erro ao excluir cliente: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Erro ao excluir cliente")
