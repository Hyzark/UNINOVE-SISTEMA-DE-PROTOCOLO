from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routes.cadastro_usuario import router as cadastro_router
from routes.login import router as login_router
from routes.cadastro_mesa import router as cadastro_mesa_router
from routes.cadastro_setor import router as cadastro_setor_router
app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="uma-chave-secreta-forte"
)

app.include_router(cadastro_router)

app.include_router(login_router)

app.include_router(cadastro_mesa_router)

app.include_router(cadastro_setor_router)



