from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def health():
    return {"status": "ok"}


@router.get("/alembic")
async def health_alembic(
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        text("SELECT version_num FROM alembic_version")
    )

    revision = result.scalar_one_or_none()
    return {"alembic_revision": revision}
