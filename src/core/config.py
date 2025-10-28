"""Arquivo de configuração global da aplicação"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Classe que carrega todas as variáveis de ambiente definidas"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "db_auth"
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def DATABASE_URL(self) -> str:
        """Retorna a URL do banco de dados"""

        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        server = self.POSTGRES_SERVER
        port = self.POSTGRES_PORT
        db_name = self.POSTGRES_DB

        return f"postgresql://{user}:{password}@{server}:{port}/{db_name}"


settings = Settings()
