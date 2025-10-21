from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt

from src.modules.auth.schemas import TokenData

from .config import settings


class JWTUtils:
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Gera um token JWT e o retorna"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> TokenData:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            user_id = payload.get("sub")

            if user_id:
                return TokenData(user_id=user_id)
            else:
                raise credentials_exception
        except JWTError as err:
            raise credentials_exception from err
