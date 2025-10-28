"""Main do serviço de autenticação do projeto Estrato"""

from fastapi import FastAPI

# Router
from .modules.auth.router import router as auth_router

app = FastAPI(title="Estrato Auth API")


app.include_router(auth_router)
