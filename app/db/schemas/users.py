from pydantic import BaseModel, ConfigDict


class SignUpSchema(BaseModel):
    name: str
    email: str
    password: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)
