from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routes.cadastro_usuario import router as cadastro_router
from routes.login import router as login_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="uma-chave-secreta-forte"
)

app.include_router(cadastro_router)

app.include_router(login_router)

