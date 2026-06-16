from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def health():
    return {"status": "ok"}


@router.get("/db")
async def health_db(
    session: AsyncSession = Depends(get_session),
):
    try:
        await session.execute(
            text("SELECT 1")
        )

        return {"status": "ok"}
    
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavaiable: {exc}",
        )