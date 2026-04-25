"""Configurações carregadas do ambiente para o backend."""

import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Agrupa variáveis de ambiente usadas pela API.

    Os valores padrão existem para facilitar o desenvolvimento local; em
    produção, devem ser sobrescritos por variáveis reais no ambiente.
    """

    DATABASE_URL: str
    APP_PASSWORD: str = "minhaloja123"
    APP_SECRET: str = "dev-secret-change-in-production"
    ANTHROPIC_API_KEY: str = ""

    class Config:
        """Define o arquivo `.env` como fonte adicional de configuração local."""

        env_file = ".env"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Normaliza a URL para SQLAlchemy async e valida cenários comuns de deploy."""

        if not isinstance(value, str) or not value.strip():
            raise ValueError("DATABASE_URL não foi definida corretamente.")

        database_url = value.strip()

        # Render e outros provedores podem entregar `postgres://` por padrão.
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # O backend usa SQLAlchemy assíncrono, então força o driver asyncpg.
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        parsed = urlparse(database_url)

        # Host `db` funciona no docker-compose local, mas não em produção.
        if parsed.hostname == "db" and os.getenv("RENDER") == "true":
            raise ValueError(
                "DATABASE_URL aponta para host 'db' (ambiente local). "
                "No Render, use a URL do PostgreSQL gerenciada pela própria plataforma."
            )

        # Banco gerenciado do Render exige SSL para conexões externas.
        query_items = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if os.getenv("RENDER") == "true" and "sslmode" not in query_items:
            query_items["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(query_items))
            database_url = urlunparse(parsed)

        return database_url

settings = Settings()
