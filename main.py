from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from routes.cadastro_usuario import router as cadastro_router
from routes.login import router as login_router
from routes.cadastro_mesa import router as cadastro_mesa_router
from routes.cadastro_setor import router as cadastro_setor_router
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
app.mount("/style", StaticFiles(directory=BASE_DIR / "style"), name="style")

@app.get("/", include_in_schema=False)
def pagina_login():
    return FileResponse(BASE_DIR / "templates" / "login.html")

app.add_middleware(
    SessionMiddleware,
    secret_key="uma-chave-secreta-forte",
    max_age=None
)

app.include_router(cadastro_router)

app.include_router(login_router)

app.include_router(cadastro_mesa_router)

app.include_router(cadastro_setor_router)



