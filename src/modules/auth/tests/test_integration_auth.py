import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient) -> tuple[dict, dict]:
    """
    Fixture específica para os testes de integração de auth.
    Cria um usuário de teste, faz login e retorna os headers de autenticação
    e os dados do usuário.
    """
    user_data = {
        "email": "auth-test@example.com",
        "full_name": "Auth Test User",
        "password": "StrongPassword123",
    }

    # 1. Registrar
    reg_response = client.post("/auth/register", json=user_data)

    if reg_response.status_code == 409:
        # Se o usuário já existir (testes anteriores), apenas faz login
        login_response = client.post(
            "/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
    else:
        # Se foi um registro novo
        assert reg_response.status_code == 201
        token = reg_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    return headers, user_data


class TestAuthRoutes:
    """Agrupa todos os testes de integração para as rotas do módulo Auth."""

    # --- Testes de /auth/register ---

    def test_register_success_returns_201(self, client: TestClient):
        """Testa a criação de um novo usuário (POST /auth/register)."""
        user_data = {
            "email": "test-user-reg@example.com",
            "full_name": "Test User Reg",
            "password": "password123",
        }
        response = client.post("/auth/register", json=user_data)
        data = response.json()

        assert response.status_code == 201
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.parametrize(
        "payload, expected_detail_substring",
        [
            (
                {"full_name": "Nome", "password": "123"},
                "Field required",
            ),  # email faltando
            (
                {"email": "a@b.c", "full_name": "Nome"},
                "Field required",
            ),  # password faltando
            (
                {"email": "a@b.c", "password": "123"},
                "Field required",
            ),  # full_name faltando
            (
                {
                    "email": "a@b.c",
                    "full_name": "Nome",
                    "password": "123",
                },  # password < 8
                "String should have at least 8 characters",
            ),
            (
                {
                    "email": "a@b.c",
                    "full_name": "a",
                    "password": "password123",
                },  # full_name < 3
                "String should have at least 3 characters",
            ),
        ],
    )
    def test_register_with_invalid_data_fails_422(
        self, client: TestClient, payload: dict, expected_detail_substring: str
    ):
        """Testa que o registro com dados inválidos falha (POST /auth/register)."""
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422
        assert expected_detail_substring in str(response.json())

    def test_register_duplicate_email_fails_409(self, client: TestClient):
        """Testa que a criação de um usuário com email duplicado falha (POST /auth/register)."""
        user_data = {
            "email": "duplicate@example.com",
            "full_name": "User A",
            "password": "password123",
        }
        # Cria na primeira vez (ou ignora se já existir)
        client.post("/auth/register", json=user_data)

        # A segunda tentativa DEVE falhar
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 409
        assert "Um usuário com esse email já existe" in response.json()["detail"]

    # --- Testes de /auth/login ---

    @pytest.fixture
    def login_user(self, client: TestClient):
        """Fixture de classe para garantir que o usuário de login exista."""
        user_data = {
            "email": "login-user@example.com",
            "full_name": "Login User",
            "password": "password123",
        }
        # Garante que o usuário exista para os testes de login
        client.post("/auth/register", json=user_data)
        return user_data

    def test_login_success_returns_200(self, client: TestClient, login_user: dict):
        """Testa o login com credenciais corretas (POST /auth/login)."""
        login_payload = {
            "email": login_user["email"],
            "password": login_user["password"],
        }
        response = client.post("/auth/login", json=login_payload)
        data = response.json()

        assert response.status_code == 200
        assert "access_token" in data

    @pytest.mark.parametrize(
        "email_key, password_key, expected_status, expected_detail",
        [
            (
                "non-existent@example.com",
                "password123",
                401,
                "Email ou senha incorretos",
            ),
            ("email", "wrong-password", 401, "Email ou senha incorretos"),
        ],
    )
    def test_login_invalid_credentials_fails_401(
        self,
        client: TestClient,
        login_user: dict,
        email_key: str,
        password_key: str,
        expected_status: int,
        expected_detail: str,
    ):
        """Testa que o login com credenciais erradas falha (POST /auth/login)."""

        # Usa os dados da fixture 'login_user' para montar o payload
        email = login_user["email"] if email_key == "email" else email_key
        password = (
            login_user["password"] if password_key == "password" else password_key
        )

        response = client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == expected_status
        assert expected_detail in response.json()["detail"]

    # --- Testes de /auth/users/me (Rotas Protegidas) ---

    def test_get_users_me_success_returns_200(
        self, client: TestClient, auth_headers: tuple[dict, dict]
    ):
        """Testa a busca de dados do usuário logado (GET /auth/users/me)."""
        headers, user_data = auth_headers
        response = client.get("/auth/users/me", headers=headers)
        data = response.json()

        assert response.status_code == 200
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data

    @pytest.mark.parametrize(
        "headers, expected_status",
        [
            (None, 403),  # FastAPI retorna 403 por padrão para HTTPBearer faltando
            ({"Authorization": "Bearer bad-invalid-token"}, 401),
        ],
    )
    def test_get_users_me_invalid_auth_fails(
        self, client: TestClient, headers: dict | None, expected_status: int
    ):
        """Testa que acessar rotas protegidas sem token ou com token inválido falha."""
        response = client.get("/auth/users/me", headers=headers)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "update_payload, expected_name, new_password",
        [
            ({"full_name": "Nome Atualizado"}, "Nome Atualizado", None),
            (
                {"password": "NewStrongPassword123"},
                "Auth Test User",
                "NewStrongPassword123",
            ),
            (
                {"full_name": "Nome Final", "password": "PasswordFinal123"},
                "Nome Final",
                "PasswordFinal123",
            ),
        ],
    )
    def test_update_users_me_success_returns_200(
        self,
        client: TestClient,
        auth_headers: tuple[dict, dict],
        update_payload: dict,
        expected_name: str,
        new_password: str | None,
    ):
        """Testa a atualização dos dados do usuário logado (PATCH /auth/users/me)."""
        headers, user_data = auth_headers

        response = client.patch("/auth/users/me", headers=headers, json=update_payload)
        data = response.json()

        assert response.status_code == 200
        assert data["full_name"] == expected_name
        assert data["email"] == user_data["email"]

        # Se a senha foi atualizada, testa o login com a nova senha
        if new_password:
            # Login com senha antiga deve falhar
            old_login_resp = client.post(
                "/auth/login",
                json={"email": user_data["email"], "password": user_data["password"]},
            )
            assert old_login_resp.status_code == 401

            # Login com senha nova deve funcionar
            new_login_resp = client.post(
                "/auth/login",
                json={"email": user_data["email"], "password": new_password},
            )
            assert new_login_resp.status_code == 200

    def test_delete_users_me_success_returns_204(
        self, client: TestClient, auth_headers: tuple[dict, dict]
    ):
        """Testa a exclusão da conta do usuário logado (DELETE /auth/users/me)."""
        headers, user_data = auth_headers

        delete_response = client.delete("/auth/users/me", headers=headers)
        assert delete_response.status_code == 204

        # Tentar buscar o usuário deve falhar (pois o token é baseado no ID que não existe mais)
        get_response = client.get("/auth/users/me", headers=headers)
        assert get_response.status_code == 404

        # Tentar fazer login deve falhar
        login_response = client.post(
            "/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        assert login_response.status_code == 401
