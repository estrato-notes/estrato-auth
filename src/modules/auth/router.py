import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.jwt import JWTUtils
from src.core.models import User

from .schemas import Token, UserCreate, UserLogin, UserResponse, UserUpdate
from .service import AuthService as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = HTTPBearer()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    creds: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)],
) -> User:
    """Busca e retorna o usuário ativo no momento pelo ID"""
    token = creds.credentials
    token_data = JWTUtils.decode_access_token(token)
    user_id = uuid.UUID(token_data.user_id)
    return auth_service.get_user_by_id(db, user_id)


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo usuário e retorna o token",
)
def register(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]) -> Token:
    """Realiza o cadastro de um usuário"""
    return auth_service.register_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Autentica o usuário e retorna o token",
)
def login(user_login_data: UserLogin, db: Annotated[Session, Depends(get_db)]) -> Token:
    """Realiza a autenticação de um usuário"""
    return auth_service.login_user(db, user_login_data)


@router.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retorna os dados do usuário logado",
)
def get_logged_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Retorna os dados do usuário logado no momento"""
    return current_user


@router.patch(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza os dados do usuário (nome e senha)",
)
def update_logged_user_data(
    user_update_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Atualiza os dados do usuário logado"""
    return auth_service.update_user(db, current_user.id, user_update_data)


@router.delete(
    "/users/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deleta a conta do usuário logado",
)
def delete_logged_user_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Deleta a conta do usuário logado no momento"""
    auth_service.delete_user(db, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
