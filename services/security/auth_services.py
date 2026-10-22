from config import TIPO_FUNCIONARIO, TIPO_ADMIN
from repositories.login_repository import get_usuario_by_id
from fastapi import Request, HTTPException

def get_current_user(request: Request):
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não está logado."
        )

    return user_id

def require_admin(request: Request):
    user_id = get_current_user(request)
    usuario = get_usuario_by_id(user_id)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado."
        )
    if usuario[3] != TIPO_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Usuário não é administrador."
        )
    return user_id

def require_funcionario(request: Request):
    user_id = get_current_user(request)
    usuario = get_usuario_by_id(user_id)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado."
        )
    if usuario[3] != TIPO_FUNCIONARIO:
        raise HTTPException(
            status_code=403,
            detail="Usuário não é funcionário."
        )
    return user_id

def require_funcionario_id(user_id: int):
    usuario = get_usuario_by_id(user_id)
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado."
        )
    if usuario[3] != TIPO_FUNCIONARIO:
        raise HTTPException(
            status_code=403,
            detail="Usuário não é funcionário."
        )
    return user_id

