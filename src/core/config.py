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

    # True, если перед БД стоит pgbouncer в transaction-режиме (KZ).
    # Отключает кэши prepared statements и включает уникальные имена для них.
    # Для прямого подключения к Postgres оставить False — кэш работает и быстрее.
    db_pgbouncer: bool = False
    # Потолок одновременных соединений от сервиса = db_pool_size + db_max_overflow.
    # Сверять с max_client_conn у pgbouncer либо с max_connections у Postgres.
    db_pool_size: int = 10
    db_max_overflow: int = 10

    secret_key: str = ""
    access_token_expire_days: int = 300
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "besoft:showgo"

    storage_url: str = "https://api.sxodim.uz/storage/images/"

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
