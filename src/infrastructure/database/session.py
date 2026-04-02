import ssl
from contextlib import asynccontextmanager

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

engine = create_async_engine(
    db_url,
    connect_args={
        "command_timeout": 10,
        "statement_cache_size": 0,
        # "ssl": ssl_ctx,
        # "command_timeout": 10,
        # "server_settings": {"statement_timeout": "30000"},
    },
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0,
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
