from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from repositories.setores_repository import create_cadastro_setor
from services.security.auth_services import require_admin

router = APIRouter()

class Setor(BaseModel):
    nome: str
    descricao: str

@router.post("/cadastrarsetor")
def create_cadastro_setor_route(cadastro: Setor, user_type = Depends(require_admin)):
        
    try:
        create_cadastro_setor(cadastro)
        return {"mensagem": "Setor criado!", "cadastro": cadastro}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
