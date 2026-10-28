from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from services.login_services import (
    auth_password,
    CredenciaisInvalidasException
)
from repositories.login_repository import get_painel_usuario
from config import TIPO_ADMIN, TIPO_GERENTE

router = APIRouter()

@router.get("/sessao")
def consultar_sessao(request: Request):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Sessão encerrada.")
    dados = get_painel_usuario(user_id)
    if dados is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    usuario, mesas = dados
    admin = usuario[3] == TIPO_ADMIN
    perfil = "admin" if admin else "gerente" if usuario[3] == TIPO_GERENTE else "funcionario"
    return {"id": usuario[0], "nome": usuario[1], "email": usuario[2],
            "perfil": perfil, "nivel_acesso": usuario[3], "setor_id": usuario[4],
            "setor": usuario[5], "mesas": mesas}

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"mensagem": "Logout realizado."}


class Usuarios(BaseModel):
    email: str = Field(min_length=1)
    senha: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def validar_email_empresa(cls, value):
        value = value.strip().lower()
        dominios_permitidos = ("@empresa.sp.gov.br", "@admin.sp.gov.br")
        if value.count("@") != 1 or not value.endswith(dominios_permitidos):
            raise ValueError("Use um e-mail @empresa.sp.gov.br ou @admin.sp.gov.br.")
        return value


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
