from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.schemas.sync import SyncRunSchema

from app.core.dependencies import (
    get_getter_sync_usesace,
    get_last_sync_usecase,
    get_trigger_sync_usecase,
)

if TYPE_CHECKING:
    from app.usecases import (
        GetSyncUseCase,
        LastSyncUseCase,
        TriggerSyncUseCase,
    )

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
)


@router.get("/last", response_model=SyncRunSchema)
async def get_last_syn(
    usecase: LastSyncUseCase = Depends(get_last_sync_usecase),
) -> SyncRunSchema:
    return await usecase.do()


@router.post("/trigger", response_model=SyncRunSchema)
async def run_sync(
    usecase: TriggerSyncUseCase = Depends(get_trigger_sync_usecase),
) -> SyncRunSchema:
    return await usecase.do()


@router.get("/{sync_id}", response_model=SyncRunSchema)
async def get_sync_by_id(
    sync_id: uuid.UUID,
    usecase: GetSyncUseCase = Depends(get_getter_sync_usesace),
) -> SyncRunSchema:
    return await usecase.do(sync_id=sync_id)