from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Scanner API"
    app_version: str = "1.0.0"
    debug: bool = False

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""

    secret_key: str = ""
    access_token_expire_days: int = 300
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "besoft:showgo"

    default_country_code: str = "uz"
    default_country_id: int = 1
    time_zone_difference: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
