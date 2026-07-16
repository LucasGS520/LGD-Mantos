"""Configurações carregadas do ambiente para o backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agrupa variáveis de ambiente usadas pela API.

    Segurança: DATABASE_URL, APP_PASSWORD e APP_SECRET são obrigatórios e NÃO
    possuem valor padrão — a aplicação se recusa a subir sem eles definidos.
    Isso impede que segredos de desenvolvimento vazem para produção.
    """

    DATABASE_URL: str
    APP_PASSWORD: str
    APP_SECRET: str
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # Origens permitidas para CORS, separadas por vírgula.
    # Em produção, definir CORS_ORIGINS com o domínio real do frontend
    # (ex.: "https://meuapp.vercel.app"). O padrão cobre desenvolvimento local.
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Converte CORS_ORIGINS em lista, ignorando entradas vazias."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        """Define o arquivo `.env` como fonte adicional de configuração local."""

        env_file = ".env"


settings = Settings()
