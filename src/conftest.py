"""Arquivo de configuração global dos testes"""

import alembic.command
import alembic.config
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.database import get_db
from src.main import app

TEST_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Cria e limpa as tabelas do banco de testes para cada sessão de teste.
    Usa o alembic.ini do estrato-auth.
    """
    alembic_cfg = alembic.config.Config("alembic.ini")

    alembic.command.upgrade(alembic_cfg, "head")
    yield
    alembic.command.downgrade(alembic_cfg, "base")


@pytest.fixture
def db_session():
    """Fornece uma sessão limpa do banco para cada teste."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    if transaction.is_active:
        transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture
def client(db_session):
    """
    Fornece um TestClient com a dependência do Banco (get_db) sobrescrita
    para usar a sessão de teste.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
