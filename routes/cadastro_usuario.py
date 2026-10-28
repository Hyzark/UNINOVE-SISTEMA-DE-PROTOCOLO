from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel, Field, ConfigDict, field_validator
import sqlite3
from repositories.cadastro_usuario_repository import create_cadastro_func
from services.security.auth_services import require_admin
from services.cadastro_usuario_services import EmailJaExisteException
from services.security.password import hash_password

router = APIRouter()

class Funcionario(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str = Field(min_length=1)
    email: str = Field(min_length=1)
    senha: str = Field(min_length=1)
    cargo: str = Field(min_length=1)
    setor_id: int = Field(gt=0)

    @field_validator("email")
    @classmethod
    def validar_email_empresa(cls, value):
        value = value.strip().lower()
        if not value.endswith("@empresa.sp.gov.br") or value.count("@") != 1:
            raise ValueError("Use um e-mail @empresa.sp.gov.br.")
        return value

@router.post("/cadastrarfuncionario")
def create_cadastro_funcionario_route(cadastro: Funcionario, user_type = Depends(require_admin)):
    try:
        hashed_password = hash_password(cadastro.senha)
        create_cadastro_func(cadastro, hashed_password)
        return {"mensagem": "Funcionário criado!"}
    except EmailJaExisteException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email já cadastrado ou setor inválido.")
