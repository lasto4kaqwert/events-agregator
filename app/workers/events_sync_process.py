import logging

logging.basicConfig()

logger = logging.getLogger(__name__)

async def run() -> None:
    print("Events backgroun sync started")
