import uuid

from fastapi import APIRouter, Depends

from app.services.agregator_service import AgregatorService
from app.core.dependencies import get_agregator_service

from app.schemas.sync import SyncRunSchema

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
)


@router.get("/last", response_model=SyncRunSchema)
async def get_last_syn(
    service: AgregatorService = Depends(get_agregator_service),
) -> SyncRunSchema:
    return await service.get_last_sync()


@router.post("/trigger", response_model=SyncRunSchema)
async def run_sync(
    service: AgregatorService = Depends(get_agregator_service),
) -> SyncRunSchema:
    return await service.run_sync()


@router.get("/{sync_id}", response_model=SyncRunSchema)
async def get_sync_by_id(
    sync_id: uuid.UUID,
    service: AgregatorService = Depends(get_agregator_service),
) -> SyncRunSchema:
    return await service.get_sync_by_id(sync_id=sync_id)