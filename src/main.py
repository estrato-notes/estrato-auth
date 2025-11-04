"""Main do serviço de autenticação do projeto Estrato"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

# Router
from .modules.auth.router import router as auth_router

app = FastAPI(title="Estrato Auth API")

origins = [settings.CLIENT_ORIGIN_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
