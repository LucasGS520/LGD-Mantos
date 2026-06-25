"""Configurações carregadas do ambiente para o backend."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Agrupa variáveis de ambiente usadas pela API.

    Os valores padrão existem para facilitar o desenvolvimento local; em
    produção, devem ser sobrescritos por variáveis reais no ambiente.
    """

    DATABASE_URL: str
    APP_PASSWORD: str = "minhaloja123"
    APP_SECRET: str = "dev-secret-change-in-production"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    class Config:
        """Define o arquivo `.env` como fonte adicional de configuração local."""

        env_file = ".env"

settings = Settings()
