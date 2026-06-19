import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_session

from app.services.agregator_service import AgregatorService
from app.services.external_api_service import ExternalAPIService
from app.services.local_repository_service import LocalRepositoryService
from app.services.synchronization_service import SynchronizationService


async def get_local_repository_service(
    session: AsyncSession = Depends(get_session),
) -> LocalRepositoryService:
    return LocalRepositoryService(session=session)

async def get_external_api_service() -> ExternalAPIService:
    return ExternalAPIService(
        base_url=os.environ.get("EVENT_PROVIDER_HOST"),
        api_key=os.environ.get("EVENT_PROVIDER_API_KEY"),
    )

async def get_synchronization_service(
    local: LocalRepositoryService = Depends(get_local_repository_service),
    external: ExternalAPIService = Depends(get_external_api_service),
) -> SynchronizationService:
    return SynchronizationService(
        local=local,
        external=external,
    )

async def get_agregator_service(
    local: LocalRepositoryService = Depends(get_local_repository_service),
    external: ExternalAPIService = Depends(get_external_api_service),
    sync: SynchronizationService = Depends(get_synchronization_service),
) -> AgregatorService:
    return AgregatorService(
        local=local,
        external=external,
        sync=sync,
    )