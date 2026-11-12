import ssl
from contextlib import asynccontextmanager
from uuid import uuid4

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.config import settings
from src.infrastructure.database.models import Base


ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

db_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

_connect_args: dict = {
    "command_timeout": 10,
    # "ssl": ssl_ctx,
    # "server_settings": {"statement_timeout": "30000"},
}

# Настройки prepared statements зависят от того, что стоит перед БД.
# При прямом подключении к Postgres кэши оставляем включёнными — так быстрее.
if settings.db_pgbouncer:
    # Кэшей prepared statements два, и они независимы:
    #   statement_cache_size          — собственный кэш asyncpg;
    #   prepared_statement_cache_size — кэш шима asyncpg внутри SQLAlchemy.
    # Отключать нужно оба: одного первого недостаточно.
    _connect_args["statement_cache_size"] = 0
    _connect_args["prepared_statement_cache_size"] = 0
    # asyncpg нумерует statements последовательно (__asyncpg_stmt_1__, _2__, ...).
    # В transaction-режиме несколько клиентских соединений делят одно серверное,
    # из-за чего имена конфликтуют ("prepared statement already exists").
    # Уникальное имя на каждый statement убирает коллизии.
    _connect_args["prepared_statement_name_func"] = lambda: f"__asyncpg_{uuid4()}__"

engine = create_async_engine(
    db_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    # Прежний pool_size=1 заставлял сервис выполнять ровно один запрос за раз:
    # остальные запросы ждали в QueuePool до pool_timeout и падали с
    # "QueuePool limit of size 1 overflow 0 reached".
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=30,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose(close=False)


@asynccontextmanager
async def force_master_session():
    async with AsyncSessionLocal() as session:
        yield session
