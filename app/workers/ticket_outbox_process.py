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


async def main() -> None:
    interval_seconds = 5

    while True:
        batch_size = 0

        try:
            async with async_session_factory() as session:
                processor: TicketOutboxProcessor = await builder(session)
                logger.info(
                    "Proccess %s is started at %s",
                    type(processor).__name__,
                    datetime.now(),
                )

                batch_size = await processor.run(
                    logger=logger,
                )

        except Exception as exc:
            logger.exception("Process failed with %s", exc)

        if batch_size == 0:
            await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
