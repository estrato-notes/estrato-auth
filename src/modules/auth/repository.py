"""Repository do módulo de autenticação"""

import uuid

from sqlalchemy.orm import Session

from src.core.models import User
from src.core.security import get_hashed_password

from .schemas import UserCreate, UserUpdate


class UserRepository:
    """Agrupa os métodos que conversam diretamente com o banco"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Cria e adiciona um novo usuário no banco"""
        hashed_password = get_hashed_password(user_data.password)

        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    @staticmethod
    def get_user_by_email(db: Session, user_email: str) -> User | None:
        """Busca e retorna um user referente ao email passado"""
        return db.query(User).filter(User.email == user_email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
        """Busca e retorna um user referente ao ID passado"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user: User, user_update_data: UserUpdate) -> User:
        """Edita as informações do usuário"""
        updated_data = user_update_data.model_dump(exclude_unset=True)

        if "password" in updated_data:
            hashed_password = get_hashed_password(updated_data["password"])
            user.hashed_password = hashed_password

        if "full_name" in updated_data:
            user.full_name = updated_data["full_name"]

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def delete_user(db: Session, user: User):
        """Deleta o usuário do banco"""
        db.delete(user)
        db.commit()
