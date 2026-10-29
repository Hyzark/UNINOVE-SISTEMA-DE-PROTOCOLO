from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from repositories.setores_repository import create_cadastro_setor, listar_setores_ativos
from repositories.auditoria_repository import listar_historico_cadastros
from services.security.auth_services import require_admin

router = APIRouter()

@router.get("/setores")
def listar_setores():
    return [{"id": setor[0], "nome": setor[1]} for setor in listar_setores_ativos()]


@router.get("/setores/historico")
def historico_setores(user_id: int = Depends(require_admin)):
    return [
        {"id": evento[0], "acao": evento[1], "descricao": evento[2],
         "criado_em": evento[3], "usuario": evento[4]}
        for evento in listar_historico_cadastros("setores")
    ]

class Setor(BaseModel):
    nome: str
    descricao: str

@router.post("/cadastrarsetor")
def create_cadastro_setor_route(cadastro: Setor, user_id: int = Depends(require_admin)):
        
    try:
        create_cadastro_setor(cadastro, user_id)
        return {"mensagem": "Setor criado!", "cadastro": cadastro}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
