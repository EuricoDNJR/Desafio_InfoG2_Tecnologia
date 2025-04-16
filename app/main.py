from fastapi import FastAPI
from app.db.database import engine
from app.db.base import Base
from app.models import user


async def lifespan(app: FastAPI):
    print(">> Criando tabelas")
    Base.metadata.create_all(bind=engine)

    yield

    pass


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"msg": "API Running Lets Bora!"}
