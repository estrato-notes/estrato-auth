import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.core.models import User
from src.modules.auth.schemas import Token, UserCreate, UserLogin, UserUpdate
from src.modules.auth.service import AuthService


@pytest.fixture
def mock_user_repo():
    """Cria um mock para o user_repository."""
    with patch(
        "src.modules.auth.service.user_repository", new_callable=MagicMock
    ) as mock:
        yield mock


@pytest.fixture
def mock_jwt_utils():
    """Cria um mock para o JWTUtils."""
    with patch("src.modules.auth.service.JWTUtils", new_callable=MagicMock) as mock:
        mock.create_access_token.return_value = "fake.access.token"
        yield mock


@pytest.fixture
def mock_verify_hash():
    """Cria um mock para a função verify_hash."""
    with patch("src.modules.auth.service.verify_hash", new_callable=MagicMock) as mock:
        yield mock


class TestUnitAuthService:
    """Agrupa todos os testes unitários para o AuthService."""

    def test_register_user_success(
        self, mock_user_repo: MagicMock, mock_jwt_utils: MagicMock
    ):
        """
        Testa se o serviço chama o repositório e o JWTUtils para registrar
        um usuário com sucesso.
        """
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="password123",
        )
        mock_db_session = MagicMock()
        mock_new_user = User(
            id=uuid.uuid4(), email=user_data.email, full_name=user_data.full_name
        )

        mock_user_repo.create_user.return_value = mock_new_user

        result = AuthService.register_user(mock_db_session, user_data)

        mock_user_repo.create_user.assert_called_once_with(mock_db_session, user_data)
        mock_jwt_utils.create_access_token.assert_called_once_with(
            data={"sub": str(mock_new_user.id)}
        )
        assert isinstance(result, Token)
        assert result.access_token == "fake.access.token"

    def test_register_user_duplicate_email_raises_409(self, mock_user_repo: MagicMock):
        """
        Testa se o serviço levanta HTTPException 409 ao receber IntegrityError
        (email duplicado) do repositório.
        """
        user_data = UserCreate(
            email="duplicate@example.com",
            full_name="Test User",
            password="password123",
        )
        mock_db_session = MagicMock()
        mock_db_session.rollback = MagicMock()

        mock_user_repo.create_user.side_effect = IntegrityError(
            "mocked error", params=None, orig=None
        )

        with pytest.raises(HTTPException) as exc_info:
            AuthService.register_user(mock_db_session, user_data)

        assert exc_info.value.status_code == 409
        assert "Um usuário com esse email já existe" in exc_info.value.detail
        mock_db_session.rollback.assert_called_once()

    def test_login_user_success(
        self,
        mock_user_repo: MagicMock,
        mock_jwt_utils: MagicMock,
        mock_verify_hash: MagicMock,
    ):
        """Testa o login bem-sucedido de um usuário."""
        login_data = UserLogin(email="test@example.com", password="password123")
        mock_db_session = MagicMock()
        mock_user = User(
            id=uuid.uuid4(),
            email=login_data.email,
            hashed_password="hashed_password",
        )

        mock_user_repo.get_user_by_email.return_value = mock_user
        mock_verify_hash.return_value = True

        result = AuthService.login_user(mock_db_session, login_data)

        mock_user_repo.get_user_by_email.assert_called_once_with(
            mock_db_session, login_data.email
        )
        mock_verify_hash.assert_called_once_with(
            login_data.password, mock_user.hashed_password
        )
        mock_jwt_utils.create_access_token.assert_called_once_with(
            data={"sub": str(mock_user.id)}
        )
        assert result.access_token == "fake.access.token"

    def test_login_user_not_found_raises_401(
        self,
        mock_user_repo: MagicMock,
        mock_jwt_utils: MagicMock,
        mock_verify_hash: MagicMock,
    ):
        """Testa se o login falha com 401 se o email não for encontrado."""
        login_data = UserLogin(email="wrong@example.com", password="password123")
        mock_db_session = MagicMock()
        mock_user_repo.get_user_by_email.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            AuthService.login_user(mock_db_session, login_data)

        assert exc_info.value.status_code == 401
        assert "Email ou senha incorretos" in exc_info.value.detail
        mock_verify_hash.assert_not_called()
        mock_jwt_utils.create_access_token.assert_not_called()

    def test_login_user_wrong_password_raises_401(
        self,
        mock_user_repo: MagicMock,
        mock_jwt_utils: MagicMock,
        mock_verify_hash: MagicMock,
    ):
        """Testa se o login falha com 401 se a senha estiver incorreta."""
        login_data = UserLogin(email="test@example.com", password="wrongpassword")
        mock_db_session = MagicMock()
        mock_user = User(
            id=uuid.uuid4(),
            email=login_data.email,
            hashed_password="hashed_password",
        )

        mock_user_repo.get_user_by_email.return_value = mock_user
        mock_verify_hash.return_value = False  # Senha incorreta

        with pytest.raises(HTTPException) as exc_info:
            AuthService.login_user(mock_db_session, login_data)

        assert exc_info.value.status_code == 401
        assert "Email ou senha incorretos" in exc_info.value.detail
        mock_jwt_utils.create_access_token.assert_not_called()

    def test_get_user_by_id_not_found_raises_404(self, mock_user_repo: MagicMock):
        """Testa se o serviço levanta HTTPException 404 se o repo retornar None."""
        user_id = uuid.uuid4()
        mock_db_session = MagicMock()
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            AuthService.get_user_by_id(mock_db_session, user_id)

        assert exc_info.value.status_code == 404
        assert "O usuário não foi encontrado" in exc_info.value.detail

    def test_update_user_success(self, mock_user_repo: MagicMock):
        """Testa a atualização de um usuário com sucesso."""
        user_id = uuid.uuid4()
        update_data = UserUpdate(full_name="Nome Atualizado")
        mock_db_session = MagicMock()
        mock_user_to_update = User(id=user_id, full_name="Nome Antigo")
        mock_updated_user = User(id=user_id, full_name=update_data.full_name)

        # Mock para a verificação interna get_user_by_id
        mock_user_repo.get_user_by_id.return_value = mock_user_to_update
        # Mock para o retorno do update
        mock_user_repo.update_user.return_value = mock_updated_user

        result = AuthService.update_user(mock_db_session, user_id, update_data)

        mock_user_repo.get_user_by_id.assert_called_once_with(mock_db_session, user_id)
        mock_user_repo.update_user.assert_called_once_with(
            mock_db_session, mock_user_to_update, update_data
        )
        assert result.full_name == "Nome Atualizado"

    def test_delete_user_success(self, mock_user_repo: MagicMock):
        """Testa se o serviço chama o repositório para deletar um usuário."""
        user_id = uuid.uuid4()
        mock_db_session = MagicMock()
        mock_user_to_delete = User(id=user_id, full_name="Para Deletar")

        mock_user_repo.get_user_by_id.return_value = mock_user_to_delete

        AuthService.delete_user(mock_db_session, user_id)

        mock_user_repo.get_user_by_id.assert_called_once_with(mock_db_session, user_id)
        mock_user_repo.delete_user.assert_called_once_with(
            mock_db_session, mock_user_to_delete
        )
