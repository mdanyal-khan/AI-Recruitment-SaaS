from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    supabase_url: str
    supabase_service_role_key: str

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "AI Recruitment SaaS"

    APP_ENV: str = "development"
    DEBUG: bool = False

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()