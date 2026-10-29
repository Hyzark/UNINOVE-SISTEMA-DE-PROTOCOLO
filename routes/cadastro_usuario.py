from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel, Field, ConfigDict, field_validator
import sqlite3
from repositories.cadastro_usuario_repository import create_cadastro_func
from repositories.auditoria_repository import listar_historico_cadastros
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
    nivel_acesso: int = Field(ge=1, le=3)

    @field_validator("nivel_acesso")
    @classmethod
    def validar_nivel_acesso(cls, value):
        if value not in (1, 3):
            raise ValueError("Selecione o nível de acesso 1 ou 3.")
        return value

    @field_validator("email")
    @classmethod
    def validar_email_empresa(cls, value):
        value = value.strip().lower()
        if not value.endswith("@empresa.sp.gov.br") or value.count("@") != 1:
            raise ValueError("Use um e-mail @empresa.sp.gov.br.")
        return value


@router.get("/usuarios/historico")
def historico_usuarios(user_id: int = Depends(require_admin)):
    return [
        {"id": evento[0], "acao": evento[1], "descricao": evento[2],
         "criado_em": evento[3], "usuario": evento[4]}
        for evento in listar_historico_cadastros("usuarios")
    ]

@router.post("/cadastrarfuncionario")
def create_cadastro_funcionario_route(cadastro: Funcionario, user_id: int = Depends(require_admin)):
    try:
        hashed_password = hash_password(cadastro.senha)
        create_cadastro_func(cadastro, hashed_password, user_id)
        return {"mensagem": "Funcionário criado!"}
    except EmailJaExisteException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email já cadastrado ou setor inválido.")
