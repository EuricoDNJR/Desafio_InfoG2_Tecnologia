from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
import re


def is_valid_cpf(cpf: str) -> bool:  # validador de cpf que segue a logica oficial
    cpf = re.sub(r"[^0-9]", "", cpf)  # remove tudo que não for número

    if (
        len(cpf) != 11 or cpf == cpf[0] * 11
    ):  # um CPF deve ter 11 dígitos e não pode ser uma sequência de números iguais
        return False

    sum1 = sum(
        int(cpf[i]) * (10 - i) for i in range(9)
    )  # soma os 9 primeiros dígitos multiplicados por 10, 9, 8, ..., 2
    digit1 = (sum1 * 10 % 11) % 10  # calcula o primeiro dígito verificador

    sum2 = sum(
        int(cpf[i]) * (11 - i) for i in range(10)
    )  # soma os 10 primeiros dígitos multiplicados por 11, 10, 9, ..., 2
    digit2 = (sum2 * 10 % 11) % 10  # calcula o segundo dígito verificador

    return (
        cpf[-2:] == f"{digit1}{digit2}"
    )  # verifica se os dois últimos dígitos do CPF são iguais aos dígitos verificadores calculados


class ClientSchema(BaseModel):
    name: str
    email: EmailStr
    cpf: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if not is_valid_cpf(v):
            raise ValueError("Invalid CPF")
        return v


# class ClientOut(BaseModel):
#     id: int
#     firebaseIdWhoCreated: str
#     name: str
#     email: EmailStr
#     cpf: str

#     model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str

    model_config = ConfigDict(from_attributes=True)


class ClientListPaginatedResponse(BaseModel):
    page: int
    limit: int
    clients: List[ClientListResponse]

    model_config = ConfigDict(from_attributes=True)


class ClientUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if v and not is_valid_cpf(v):
            raise ValueError("CPF inválido")
        return v


class ClientCreateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str

    model_config = ConfigDict(from_attributes=True)
