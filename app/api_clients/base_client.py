import asyncio
import logging
import aiohttp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class APIServerError(Exception):
    pass


class APIUnavailableError(Exception):
    pass


class BaseAPIClient(ABC):
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    TIMEOUT = 15.0

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    @abstractmethod
    def _build_headers(self) -> dict:
        pass

    async def _request(self, method: str, endpoint: str,
                        body: dict | None = None) -> dict:
        url = f"{self._base_url}{endpoint}"
        headers = self._build_headers()
        last_exc = None

        for attempt in range(self.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method, url,
                        json=body or {},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
                    ) as response:
                        if response.status >= 500:
                            raise APIServerError(f"HTTP {response.status}")
                        return await response.json(content_type=None)
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
                last_exc = e
                logger.warning(f"[API] Tentativa {attempt+1}/{self.MAX_RETRIES} falhou: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
            except APIServerError:
                raise

        raise APIUnavailableError(
            f"API indisponível após {self.MAX_RETRIES} tentativas: {last_exc}"
        )
