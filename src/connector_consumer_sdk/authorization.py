"""OAuth authorization helpers for connector instances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast
import json

import httpx

from connector_consumer_sdk.exceptions import OAuthAuthorizationError


@dataclass(slots=True, kw_only=True)
class OAuthAuthorizationSession:
    """Provider redirect information for a connector-instance OAuth flow."""

    connector_instance_id: str
    oauth_session_id: str
    authorization_url: str
    expires_at: str


@dataclass(slots=True, kw_only=True)
class OAuthAuthorizationSessionStatus:
    """Sanitized OAuth authorization-session status."""

    oauth_session_id: str
    connector_instance_id: str
    provider: str
    status: str
    requested_scopes: list[str]
    return_url: str | None
    credential_record_id: str | None
    error_code: str | None
    error_description: str | None
    expires_at: str
    completed_at: str | None


class ConnectorAuthorizationClient:
    """Sync client for backend-owned connector authorization flows."""

    # TODO: Move this setup-oriented OAuth orchestration surface to a frontend/platform SDK.
    # The consumer SDK is intended for published assets consuming existing connector instances.

    def __init__(
        self,
        *,
        control_plane_url: str,
        credential_service_url: str | None = None,
        auth_token: str | None = None,
        timeout_seconds: float = 15.0,
        headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.control_plane_url = control_plane_url.rstrip("/")
        self.credential_service_url = (credential_service_url or control_plane_url).rstrip("/")
        self._owns_client = http_client is None
        self._headers = dict(headers or {})
        if auth_token is not None:
            self._headers.setdefault("Authorization", f"Bearer {auth_token}")
        self._client = http_client or httpx.Client(timeout=timeout_seconds, headers=self._headers)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "ConnectorAuthorizationClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def start_authorization(
        self,
        *,
        connector_instance_id: str,
        provider: str | None = None,
        requested_scopes: list[str] | None = None,
        return_url: str | None = None,
    ) -> OAuthAuthorizationSession:
        """Create a backend OAuth authorization session and return provider redirect data."""

        payload = _authorization_request_payload(
            provider=provider,
            requested_scopes=requested_scopes,
            return_url=return_url,
        )
        url = (
            f"{self.control_plane_url}/api/v1/connector-instances/"
            f"{connector_instance_id}/authorization-sessions"
        )
        try:
            response = self._client.post(url, json=payload, headers=self._headers)
        except httpx.HTTPError as exc:
            raise OAuthAuthorizationError(
                str(exc),
                code="authorization_transport_error",
                retryable=True,
            ) from exc

        response_payload = _decode_response_payload(response)
        if not response.is_success:
            raise _authorization_response_error(response, response_payload)
        return _parse_authorization_session(response_payload)

    def get_authorization_session(
        self,
        oauth_session_id: str,
    ) -> OAuthAuthorizationSessionStatus:
        """Return sanitized OAuth authorization-session status from the backend."""

        url = f"{self.credential_service_url}/api/v1/credentials/oauth/sessions/{oauth_session_id}"
        try:
            response = self._client.get(url, headers=self._headers)
        except httpx.HTTPError as exc:
            raise OAuthAuthorizationError(
                str(exc),
                code="authorization_transport_error",
                retryable=True,
            ) from exc

        response_payload = _decode_response_payload(response)
        if not response.is_success:
            raise _authorization_response_error(response, response_payload)
        return _parse_authorization_session_status(response_payload)


class AsyncConnectorAuthorizationClient:
    """Async client for backend-owned connector authorization flows."""

    def __init__(
        self,
        *,
        control_plane_url: str,
        credential_service_url: str | None = None,
        auth_token: str | None = None,
        timeout_seconds: float = 15.0,
        headers: dict[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.control_plane_url = control_plane_url.rstrip("/")
        self.credential_service_url = (credential_service_url or control_plane_url).rstrip("/")
        self._owns_client = http_client is None
        self._headers = dict(headers or {})
        if auth_token is not None:
            self._headers.setdefault("Authorization", f"Bearer {auth_token}")
        self._client = http_client or httpx.AsyncClient(
            timeout=timeout_seconds,
            headers=self._headers,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncConnectorAuthorizationClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def start_authorization(
        self,
        *,
        connector_instance_id: str,
        provider: str | None = None,
        requested_scopes: list[str] | None = None,
        return_url: str | None = None,
    ) -> OAuthAuthorizationSession:
        """Create a backend OAuth authorization session and return provider redirect data."""

        payload = _authorization_request_payload(
            provider=provider,
            requested_scopes=requested_scopes,
            return_url=return_url,
        )
        url = (
            f"{self.control_plane_url}/api/v1/connector-instances/"
            f"{connector_instance_id}/authorization-sessions"
        )
        try:
            response = await self._client.post(url, json=payload, headers=self._headers)
        except httpx.HTTPError as exc:
            raise OAuthAuthorizationError(
                str(exc),
                code="authorization_transport_error",
                retryable=True,
            ) from exc

        response_payload = _decode_response_payload(response)
        if not response.is_success:
            raise _authorization_response_error(response, response_payload)
        return _parse_authorization_session(response_payload)

    async def get_authorization_session(
        self,
        oauth_session_id: str,
    ) -> OAuthAuthorizationSessionStatus:
        """Return sanitized OAuth authorization-session status from the backend."""

        url = f"{self.credential_service_url}/api/v1/credentials/oauth/sessions/{oauth_session_id}"
        try:
            response = await self._client.get(url, headers=self._headers)
        except httpx.HTTPError as exc:
            raise OAuthAuthorizationError(
                str(exc),
                code="authorization_transport_error",
                retryable=True,
            ) from exc

        response_payload = _decode_response_payload(response)
        if not response.is_success:
            raise _authorization_response_error(response, response_payload)
        return _parse_authorization_session_status(response_payload)


def _authorization_request_payload(
    *,
    provider: str | None,
    requested_scopes: list[str] | None,
    return_url: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if provider is not None:
        payload["provider"] = provider
    if requested_scopes is not None:
        payload["requested_scopes"] = list(requested_scopes)
    if return_url is not None:
        payload["return_url"] = return_url
    return payload


def _decode_response_payload(response: httpx.Response) -> dict[str, Any] | None:
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _authorization_response_error(
    response: httpx.Response,
    payload: dict[str, Any] | None,
) -> OAuthAuthorizationError:
    message = "Authorization endpoint returned an error."
    details: dict[str, Any] = {}
    if payload is not None:
        details = payload
        detail = payload.get("detail")
        if isinstance(detail, str):
            message = detail
    elif response.text:
        details = {"raw_text": response.text}

    return OAuthAuthorizationError(
        message,
        code="authorization_http_error",
        retryable=response.status_code >= 500,
        status_code=response.status_code,
        details=details,
    )


def _parse_authorization_session(payload: dict[str, Any] | None) -> OAuthAuthorizationSession:
    if payload is None:
        raise OAuthAuthorizationError(
            "Authorization endpoint returned a success response without a JSON body.",
            code="authorization_invalid_response",
        )
    try:
        return OAuthAuthorizationSession(
            connector_instance_id=str(payload["connector_instance_id"]),
            oauth_session_id=str(payload["oauth_session_id"]),
            authorization_url=cast(str, payload["authorization_url"]),
            expires_at=cast(str, payload["expires_at"]),
        )
    except KeyError as exc:
        raise OAuthAuthorizationError(
            "Authorization endpoint returned an invalid authorization-session payload.",
            code="authorization_invalid_response",
            details={"payload": payload},
        ) from exc


def _parse_authorization_session_status(
    payload: dict[str, Any] | None,
) -> OAuthAuthorizationSessionStatus:
    if payload is None:
        raise OAuthAuthorizationError(
            "Authorization endpoint returned a success response without a JSON body.",
            code="authorization_invalid_response",
        )
    try:
        return OAuthAuthorizationSessionStatus(
            oauth_session_id=str(payload["oauth_session_id"]),
            connector_instance_id=str(payload["connector_instance_id"]),
            provider=cast(str, payload["provider"]),
            status=cast(str, payload["status"]),
            requested_scopes=cast(list[str], payload.get("requested_scopes", [])),
            return_url=cast(str | None, payload.get("return_url")),
            credential_record_id=cast(str | None, payload.get("credential_record_id")),
            error_code=cast(str | None, payload.get("error_code")),
            error_description=cast(str | None, payload.get("error_description")),
            expires_at=cast(str, payload["expires_at"]),
            completed_at=cast(str | None, payload.get("completed_at")),
        )
    except KeyError as exc:
        raise OAuthAuthorizationError(
            "Authorization endpoint returned an invalid authorization-session status payload.",
            code="authorization_invalid_response",
            details={"payload": payload},
        ) from exc
