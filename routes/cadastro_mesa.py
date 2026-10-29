
from fastapi import HTTPException, APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from repositories.cadastro_mesas_repository import (
    create_cadastro_mesa,
    get_usuario_setor_by_id
)
from config import TIPO_ADMIN, TIPO_FUNCIONARIO, TIPO_GERENTE
from repositories.login_repository import get_painel_usuario
from services.security.auth_services import get_current_user

router = APIRouter()


class Mesa(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str = Field(min_length=1, max_length=100)


def require_operador(request: Request):
    user_id = get_current_user(request)
    dados = get_painel_usuario(user_id)
    if dados is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo.")
    usuario, _ = dados
    if usuario[3] not in (TIPO_ADMIN, TIPO_FUNCIONARIO, TIPO_GERENTE):
        raise HTTPException(status_code=403, detail="Acesso permitido somente a usuários do setor.")
    return user_id


@router.post("/cadastrarMesa")
def create_cadastro_mesa_route(
    mesa: Mesa,
    user_id: int = Depends(require_operador)
):
    setor = get_usuario_setor_by_id(user_id)

    if setor is None:
        raise HTTPException(
            status_code=404,
            detail="Setor do funcionário não encontrado."
        )

    mesa_id = create_cadastro_mesa(mesa.nome, setor[0])

    return {
        "mensagem": "Mesa criada com sucesso!",
        "id": mesa_id,
        "mesa": mesa.nome
    }
