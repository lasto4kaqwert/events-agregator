import asyncio
import logging
import sys

from app.core.async_session_factory import async_session_factory
from app.core.dependencies import build_trigger_sync_usecase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

logger = logging.getLogger(__name__)


async def run_once() -> None:
    async with async_session_factory() as session:
        usecase = await build_trigger_sync_usecase(session=session)
        await usecase.do()


async def main() -> None:
    interval_seconds = 86400
    # interval_seconds = 30

    logger.info(
        "Events sync worker started with interval_seconds=%s",
        interval_seconds,
    )

    while True:
        try:
            await run_once()
        except Exception:
            logger.exception("Unexpected worker error")

        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
