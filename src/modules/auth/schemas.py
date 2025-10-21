import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(
        ..., min_length=3, max_length=100, description="Nome completo"
    )


class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, max_length=100, description="Senha do usuário"
    )


class UserLogin(BaseModel):
    email: str = Field(..., description="Email do usuário")
    password: str = Field(
        ..., min_length=8, max_length=100, description="Senha do usuário"
    )


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, min_length=3, max_length=100, description="Novo nome do usuário"
    )
    password: Optional[str] = Field(
        None, min_length=8, max_length=100, description="Nova senha"
    )


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = Field(None, description="ID do usuário")
