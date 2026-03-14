import time
import aiohttp
from app.config.settings import settings


class WalletClient:
    TIMEOUT = 15.0

    def __init__(self):
        self._base = settings.WALLET_URL.rstrip("/")
        self._key = settings.WALLET_API_KEY

    @property
    def _headers(self) -> dict:
        return {"x-api-key": self._key, "Content-Type": "application/json"}

    async def criar_pagamento(self, amount: float, payer_name: str,
                               payer_document: str, description: str,
                               external_id: str) -> dict:
        body = {
            "amount": round(amount, 2),
            "payerName": payer_name,
            "payerDocument": payer_document,
            "description": description,
            "externalId": external_id,
        }
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{self._base}/payments/create",
                json=body,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
            ) as r:
                data = await r.json(content_type=None)
                if r.status >= 400:
                    raise Exception(f"Wallet HTTP {r.status}: {data}")
                return data

    async def consultar(self, payment_id: str) -> dict:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{self._base}/payments/{payment_id}",
                headers={"x-api-key": self._key},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as r:
                return await r.json(content_type=None)
