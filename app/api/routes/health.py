from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from typing import Any
from datetime import date
from app.services.events_provider_client import EventsProviderClient

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
    
@router.get("/test-provider", response_model=None)
async def health_test_provider() -> Any:
    try:
        events_provider = EventsProviderClient()

        result = await events_provider.events(
            changed_at=date(2000, 1, 1)
        )

        return {
            "type": str(type(result)),
            "data": result
        }
    except Exception as exc:
        return {
            "errro_type": type(exc).__name__,
            "error": str(exc),
        }