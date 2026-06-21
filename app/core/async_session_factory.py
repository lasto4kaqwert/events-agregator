import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    os.environ.get("POSTGRES_CONNECTION_STRING").replace(
        "postgres://", "postgresql+asyncpg://"
    ),
    poolclass=NullPool,
    echo=False,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
