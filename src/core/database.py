"""Arquivo de configuração da conexão com o banco de dados"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Método que fornece uma sessão do banco para outros métodos enquanto for necessário"""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
