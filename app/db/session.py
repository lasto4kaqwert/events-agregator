import os
from collections.abc import AsyncGenerator

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


engine = create_async_engine(
    os.environ.get("POSTGRES_CONNECTION_STRING"),
    poolclass=NullPool,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    async with SessionLocal() as session:
        yield session