from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session

router = APIRouter(
    prefix="/debug",
    tags=["debug"]
)


@router.get("/glitchtip-error")
async def glitchtip_error() -> None:
    raise RuntimeError("GlitchTip test error")


@router.get("/alembic-version")
async def alembic_version(
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        text("SELECT version_num FROM alembic_version")
    )

    revision = result.scalar_one_or_none()
    return {"alembic_revision": revision}
