from fastapi import FastAPI

app = FastAPI(title="Estrato Auth API")

from .modules.auth.router import router as auth_router  # noqa: E402

app.include_router(auth_router)
