"""Runtime transport helpers for the consumer SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
import json

import httpx


class ConnectorTransport(Protocol):
    """Transport contract used by the consumer SDK client."""

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one runtime request and return the decoded success payload."""

    def close(self) -> None:
        """Release any transport-owned resources."""


class AsyncConnectorTransport(Protocol):
    """Async transport contract used by the consumer SDK client."""

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one runtime request and return the decoded success payload."""

    async def aclose(self) -> None:
        """Release any transport-owned resources."""


@dataclass(slots=True)
class HTTPTransportResponseError(Exception):
    """Raised when runtime returns a non-success HTTP response."""

    status_code: int
    payload: dict[str, Any] | None
    raw_text: str | None = None


@dataclass(slots=True)
class HTTPTransportUnavailableError(Exception):
    """Raised when the runtime endpoint cannot be reached or decoded."""

    message: str


class HTTPConnectorTransport:
    """HTTP transport that talks to the runtime execute endpoint."""

    def __init__(
        self,
        *,
        runtime_url: str,
        auth_token: str | None = None,
        timeout_seconds: float = 15.0,
        endpoint_path: str = "/api/v1/runtime/execute",
        headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.execute_url = f"{runtime_url.rstrip('/')}{endpoint_path}"
        self._owns_client = http_client is None
        self._headers = dict(headers or {})
        if auth_token is not None:
            self._headers.setdefault("Authorization", f"Bearer {auth_token}")
        self._client = http_client or httpx.Client(timeout=timeout_seconds, headers=self._headers)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.post(self.execute_url, json=payload, headers=self._headers)
        except httpx.HTTPError as exc:
            raise HTTPTransportUnavailableError(str(exc)) from exc

        parsed_payload = self._decode_json(response)
        if response.is_success:
            if parsed_payload is None:
                raise HTTPTransportUnavailableError(
                    "Runtime returned a success response without a JSON body."
                )
            return parsed_payload

        raise HTTPTransportResponseError(
            status_code=response.status_code,
            payload=parsed_payload,
            raw_text=response.text or None,
        )

    @staticmethod
    def _decode_json(response: httpx.Response) -> dict[str, Any] | None:
        try:
            payload = response.json()
        except (json.JSONDecodeError, ValueError):
            return None
        if isinstance(payload, dict):
            return payload
        return None


class HTTPAsyncConnectorTransport:
    """Async HTTP transport that talks to the runtime execute endpoint."""

    def __init__(
        self,
        *,
        runtime_url: str,
        auth_token: str | None = None,
        timeout_seconds: float = 15.0,
        endpoint_path: str = "/api/v1/runtime/execute",
        headers: dict[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.execute_url = f"{runtime_url.rstrip('/')}{endpoint_path}"
        self._owns_client = http_client is None
        self._headers = dict(headers or {})
        if auth_token is not None:
            self._headers.setdefault("Authorization", f"Bearer {auth_token}")
        self._client = http_client or httpx.AsyncClient(timeout=timeout_seconds, headers=self._headers)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._client.post(self.execute_url, json=payload, headers=self._headers)
        except httpx.HTTPError as exc:
            raise HTTPTransportUnavailableError(str(exc)) from exc

        parsed_payload = HTTPConnectorTransport._decode_json(response)
        if response.is_success:
            if parsed_payload is None:
                raise HTTPTransportUnavailableError(
                    "Runtime returned a success response without a JSON body."
                )
            return parsed_payload

        raise HTTPTransportResponseError(
            status_code=response.status_code,
            payload=parsed_payload,
            raw_text=response.text or None,
        )
