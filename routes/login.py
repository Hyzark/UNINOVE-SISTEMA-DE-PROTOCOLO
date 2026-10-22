from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from services.login_services import (
    auth_password,
    CredenciaisInvalidasException
)

router = APIRouter()


class Usuarios(BaseModel):
    email: str
    senha: str


@router.post("/login")
def create_login_route(request: Request, usuario: Usuarios):
    try:
        user_id, nome = auth_password(
            usuario.email,
            usuario.senha
        )

        request.session["user_id"] = user_id

        return {
            "message": f"Bem-vindo, {nome}!",
        }

    except CredenciaisInvalidasException:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos."
        )
