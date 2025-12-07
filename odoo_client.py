import os
import time
import logging
from typing import Any, Dict, Optional, Sequence
import httpx
import asyncio

logger = logging.getLogger("odoo")

class OdooClient:
    """Async client wrapper for Odoo 19 External JSON-2 API.

    Provides a minimal abstraction for calling model methods:
    - search_read
    - create
    - write
    - unlink
    - arbitrary method via call

    Configuration via environment variables:
      ODOO_URL       Base URL (e.g. https://erp.smarterbot.cl)
      ODOO_DB        Database name (e.g. smarterbot_prod)
      ODOO_API_KEY   User API key (bearer token)

    Basic retry with exponential backoff for transient network or 5xx errors.
    """

    def __init__(self,
                 base_url: Optional[str] = None,
                 db: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: float = 10.0,
                 max_retries: int = 3,
                 backoff_factor: float = 0.5) -> None:
        self.base_url = (base_url or os.getenv("ODOO_URL", "")).rstrip("/")
        self.db = db or os.getenv("ODOO_DB", "")
        self.api_key = api_key or os.getenv("ODOO_API_KEY", "")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._semaphore = asyncio.Semaphore(int(os.getenv("ODOO_MAX_CONCURRENCY", "8")))
        if not (self.base_url and self.db and self.api_key):
            logger.warning("OdooClient incomplete config: ODOO_URL/ODOO_DB/ODOO_API_KEY required")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
            "X-Odoo-Database": self.db,
        }

    async def _request(self, model: str, method: str, payload: Dict[str, Any]) -> Any:
        if not (self.base_url and self.db and self.api_key):
            raise RuntimeError("Odoo client not configured")
        url = f"{self.base_url}/json/2/{model}/{method}"
        attempt = 0
        last_exc: Optional[Exception] = None
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                while attempt <= self.max_retries:
                    try:
                        start = time.perf_counter()
                        resp = await client.post(url, json=payload, headers=self._headers())
                        latency_ms = int((time.perf_counter() - start) * 1000)
                        if resp.status_code >= 500:
                            raise httpx.HTTPStatusError("Server error", request=resp.request, response=resp)
                        resp.raise_for_status()
                        data = resp.json()
                        logger.info(f"odoo_call model={model} method={method} status={resp.status_code} latency_ms={latency_ms}")
                        return {"ok": True, "data": data, "latency_ms": latency_ms}
                    except (httpx.HTTPError, httpx.TimeoutException) as e:
                        last_exc = e
                        attempt += 1
                        if attempt > self.max_retries:
                            break
                        sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                        await asyncio.sleep(sleep_time)
                # exhausted
                logger.error(f"odoo_call_failed model={model} method={method} error={last_exc}")
                raise last_exc or RuntimeError("Unknown Odoo error")

    # Public helpers
    async def search_read(self, model: str, domain: Sequence[Any], fields: Sequence[str], limit: int = 80) -> Any:
        return await self._request(model, "search_read", {
            "domain": domain,
            "fields": list(fields),
            "limit": limit,
        })

    async def create(self, model: str, values: Dict[str, Any]) -> Any:
        return await self._request(model, "create", {"values": values})

    async def write(self, model: str, record_id: int, values: Dict[str, Any]) -> Any:
        return await self._request(model, "write", {"ids": [record_id], "values": values})

    async def unlink(self, model: str, record_id: int) -> Any:
        return await self._request(model, "unlink", {"ids": [record_id]})

    async def call(self, model: str, method: str, params: Dict[str, Any]) -> Any:
        return await self._request(model, method, params)

# Singleton instance
odoo_client = OdooClient()
