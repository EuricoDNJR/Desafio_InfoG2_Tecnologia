import os
from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.db.base import Base
from app.db.models import user, client, product, order

from .routers.auth import auth
from .routers.clients import clients
from .routers.products import products
from .routers.orders import orders
from .utils.helper import logging


dotenv.load_dotenv()

ENV = os.getenv("ENV")
TEST = os.getenv("TEST")
logging.info(f"ENV: {ENV}")
logging.info(f"TEST: {TEST}")

api_version = "v0.1.0"
route_version = "v1"

api_metadata = {
    "title": "Lu Estilo API",
    "description": "API de gerenciamento da Lu Estilo",
    "version": api_version,
}

if ENV == "dev":
    app = FastAPI(
        title=api_metadata["title"],
        description=api_metadata["description"],
        version=api_metadata["version"],
    )
else:
    app = FastAPI(
        title=api_metadata["title"],
        description=api_metadata["description"],
        version=api_metadata["version"],
        docs_url=None,
        redoc_url=None,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

response_404 = {404: {"description": "Not found"}}

app.include_router(
    auth.router,
    prefix=f"/auth",
    tags=["auth"],
    responses=response_404,
)

app.include_router(
    clients.router,
    prefix=f"/clients",
    tags=["clients"],
    responses=response_404,
)

app.include_router(
    products.router,
    prefix=f"/products",
    tags=["products"],
    responses=response_404,
)

app.include_router(
    orders.router,
    prefix=f"/orders",
    tags=["orders"],
    responses=response_404,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting database connection")
    Base.metadata.create_all(bind=engine)

    yield

    logging.info("Closing database connection")
    engine.dispose()

    pass


app.router.lifespan_context = lifespan


@app.get("/")
def root():
    return {"msg": "API Running Lets Bora!"}
