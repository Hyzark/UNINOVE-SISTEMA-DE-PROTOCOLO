from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.login_services import auth_password

router = APIRouter()

class Usuarios(BaseModel):
    email: str
    senha: str

@router.post("/login")
def create_login_route(request: Request, usuario: Usuarios):
    user_id, nome = auth_password(usuario.email, usuario.senha)

    request.session["user_id"] = user_id
    return {
        "message": f"Bem vindo, {nome}!"
    }

