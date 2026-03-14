import asyncio
import logging

logger = logging.getLogger(__name__)


def price_calc(quantidade: int) -> float:
    if quantidade <= 10:
        return 1.00
    return round(quantidade * 0.08, 2)
