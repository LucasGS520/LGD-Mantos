from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_PASSWORD: str = "minhaloja123"
    APP_SECRET: str = "dev-secret-change-in-production"
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
