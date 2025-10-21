import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.jwt import JWTUtils
from src.core.models import User
from src.core.security import verify_hash

from .repository import UserRepository as user_repository
from .schemas import Token, UserCreate, UserLogin, UserUpdate


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> Token:
        try:
            new_user = user_repository.create_user(db, user_data)
            access_token = JWTUtils.create_access_token(data={"sub": str(new_user.id)})
            return Token(access_token=access_token)
        except IntegrityError as err:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Um usuário com esse email já existe",
            ) from err

    @staticmethod
    def login_user(db: Session, user_login_data: UserLogin) -> Token:
        user = user_repository.get_user_by_email(db, user_login_data.email)

        if not user or not verify_hash(user_login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = JWTUtils.create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token)

    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> User:
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="O usuário não foi encontrado",
            )
        return user

    @staticmethod
    def update_user(
        db: Session, user_id: uuid.UUID, user_update_data: UserUpdate
    ) -> User:
        user_to_update = AuthService.get_user_by_id(db, user_id)

        try:
            return user_repository.update_user(db, user_to_update, user_update_data)
        except IntegrityError as err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Um usuário com esse email já existe",
            ) from err

    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID):
        user_to_delete = AuthService.get_user_by_id(db, user_id)
        user_repository.delete_user(db, user_to_delete)
