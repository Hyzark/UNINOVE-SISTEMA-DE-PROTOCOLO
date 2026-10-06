from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from repositories.cadastro_usuario_repository import create_cadastro_func
from services.security.auth_services import require_admin
from services.cadastro_usuario_services import cadastrar_funcionario, EmailJaExisteException

router = APIRouter()

class Funcionario(BaseModel):
    nome: str
    email: str
    senha: str
    cargo: str
    setor_id: int

@router.post("/cadastrarfuncionario")
def create_cadastro_funcionario_route(cadastro: Funcionario, user_type = Depends(require_admin)):
    try:
        create_cadastro_func(cadastro, user_type)
        return {"mensagem": "Funcionário criado!", "cadastro": cadastro}
    except EmailJaExisteException as e:
        raise HTTPException(status_code=400, detail=str(e))
