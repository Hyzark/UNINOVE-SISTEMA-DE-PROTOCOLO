from repositories.login_repository import get_usuario_by_email
from services.security.password import verify_password


class CredenciaisInvalidasException(Exception):
    pass


def auth_password(email, password):
    result = get_usuario_by_email(email)

    if result is None:
        raise CredenciaisInvalidasException("Email ou senha inválidos.")

    senha_valida = verify_password(password, result[3])

    if not senha_valida:
        raise CredenciaisInvalidasException("Email ou senha inválidos.")

    return result[0], result[1]

