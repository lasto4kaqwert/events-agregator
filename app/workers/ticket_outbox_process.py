from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.async_session_factory import async_session_factory
from app.core.dependencies import build_ticket_outbox_processor as builder

if TYPE_CHECKING:
    from app.services.workers import TicketOutboxProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

logger = logging.getLogger(__name__)

async def run_once(
    processor: TicketOutboxProcessor,
) -> None:
    logger.info(
        "Proccess %s is started at %s",
        type(processor).__name__,
        datetime.now(),
    )

    await processor.run(
        logger=logger,
    )


async def main() -> None:
    interval_seconds = 15

    while True:
        try:
            async with async_session_factory() as session:
                processor: TicketOutboxProcessor = await builder(session)
                await run_once(processor)

        except Exception as exc:
            logger.info("Process failed with %s", exc)

        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
