
from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel

from repositories.cadastro_mesas_repository import (
    create_cadastro_mesa,
    get_usuario_setor_by_id
)
from services.security.auth_services import require_funcionario

router = APIRouter()


class Mesa(BaseModel):
    nome: str


@router.post("/cadastrarMesa")
def create_cadastro_mesa_route(
    mesa: Mesa,
    user_id: int = Depends(require_funcionario)
):
    setor = get_usuario_setor_by_id(user_id)

    if setor is None:
        raise HTTPException(
            status_code=404,
            detail="Setor do funcionário não encontrado."
        )

    create_cadastro_mesa(mesa.nome, setor[0])

    return {
        "mensagem": "Mesa criada com sucesso!",
        "mesa": mesa.nome
    }
