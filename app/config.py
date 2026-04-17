from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FinanceAPI"
    database_url: str = "sqlite:///./finance.db"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
