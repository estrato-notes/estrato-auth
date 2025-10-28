"""Arquivo que faz a verificação e gera o hash da senha do usuário"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(plain_password: str, hashed_password: str) -> bool:
    """Realiza a verificação da hash com a senha em texto puro"""
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(plain_password: str) -> str:
    """Gera o hash da string pura passada no parâmetro"""
    return pwd_context.hash(plain_password)
