"""Schemas do módulo de autenticação"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Schema base para os outros schemas"""

    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(
        ..., min_length=3, max_length=100, description="Nome completo"
    )


class UserCreate(UserBase):
    """Schema para a criação de um usuário"""

    password: str = Field(
        ..., min_length=8, max_length=100, description="Senha do usuário"
    )


class UserLogin(BaseModel):
    """Schema para o login de usuário"""

    email: str = Field(..., description="Email do usuário")
    password: str = Field(
        ..., min_length=8, max_length=100, description="Senha do usuário"
    )


class UserUpdate(BaseModel):
    """Schema para realizar alterações nos dados do usuário"""

    full_name: Optional[str] = Field(
        None, min_length=3, max_length=100, description="Novo nome do usuário"
    )
    password: Optional[str] = Field(
        None, min_length=8, max_length=100, description="Nova senha"
    )


class UserResponse(UserBase):
    """Schema de retorno com dados do usuário"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema básico do token JWT"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema que contém o id do usuário contigo no token JWT"""

    user_id: Optional[str] = Field(None, description="ID do usuário")
