from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path
from fastapi import Request
import secrets
from starlette.middleware.sessions import SessionMiddleware
from routes.cadastro_usuario import router as cadastro_router
from routes.login import router as login_router
from routes.cadastro_mesa import router as cadastro_mesa_router
from routes.cadastro_setor import router as cadastro_setor_router
from routes.processos import router as processos_router
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/protocolo", StaticFiles(directory=BASE_DIR / "protocolo-digital"), name="protocolo")

@app.get("/", include_in_schema=False)
def pagina_login(request: Request):
    request.session.clear()
    return FileResponse(BASE_DIR / "protocolo-digital" / "templates" / "login.html")

@app.get("/sistema", include_in_schema=False)
def pagina_sistema(request: Request):
    if request.session.get("user_id") is None:
        return RedirectResponse(url="/", status_code=303)
    return FileResponse(BASE_DIR / "protocolo-digital" / "index.html")

app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    max_age=None
)

app.include_router(cadastro_router)

app.include_router(login_router)

app.include_router(cadastro_mesa_router)

app.include_router(cadastro_setor_router)

app.include_router(processos_router)



