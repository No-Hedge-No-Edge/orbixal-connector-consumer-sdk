from __future__ import annotations

import json

import httpx
import pytest

from connector_consumer_sdk import (
    AsyncConnectorAuthorizationClient,
    ConnectorAuthorizationClient,
    OAuthAuthorizationError,
    OAuthAuthorizationSession,
    OAuthAuthorizationSessionStatus,
)


def test_start_authorization_posts_to_control_plane_and_returns_redirect() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(
            {
                "url": str(request.url),
                "headers": dict(request.headers),
                "payload": json.loads(request.content.decode("utf-8")),
            }
        )
        return httpx.Response(
            201,
            json={
                "connector_instance_id": "7f046781-81bd-4cfe-a2f4-d7737ae8c942",
                "oauth_session_id": "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556",
                "authorization_url": "https://provider.test/oauth/authorize?state=abc",
                "expires_at": "2026-05-06T10:15:00Z",
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = ConnectorAuthorizationClient(
        control_plane_url="https://control.test",
        auth_token="token_123",
        http_client=http_client,
    )

    session = client.start_authorization(
        connector_instance_id="7f046781-81bd-4cfe-a2f4-d7737ae8c942",
        provider="github",
        requested_scopes=["repo", "read:user"],
        return_url="https://app.test/connectors/github",
    )

    assert isinstance(session, OAuthAuthorizationSession)
    assert session.oauth_session_id == "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556"
    assert session.authorization_url.startswith("https://provider.test/oauth/authorize")
    assert len(requests) == 1
    assert requests[0]["url"] == (
        "https://control.test/api/v1/connector-instances/"
        "7f046781-81bd-4cfe-a2f4-d7737ae8c942/authorization-sessions"
    )
    assert requests[0]["headers"]["authorization"] == "Bearer token_123"
    assert requests[0]["payload"] == {
        "provider": "github",
        "requested_scopes": ["repo", "read:user"],
        "return_url": "https://app.test/connectors/github",
    }
    client.close()


def test_start_authorization_omits_empty_optional_fields() -> None:
    payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payloads.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            201,
            json={
                "connector_instance_id": "7f046781-81bd-4cfe-a2f4-d7737ae8c942",
                "oauth_session_id": "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556",
                "authorization_url": "https://provider.test/oauth/authorize?state=abc",
                "expires_at": "2026-05-06T10:15:00Z",
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = ConnectorAuthorizationClient(
        control_plane_url="https://control.test",
        http_client=http_client,
    )

    client.start_authorization(
        connector_instance_id="7f046781-81bd-4cfe-a2f4-d7737ae8c942",
    )

    assert payloads == [{}]
    client.close()


def test_get_authorization_session_uses_credential_service_url() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return httpx.Response(
            200,
            json={
                "oauth_session_id": "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556",
                "connector_instance_id": "7f046781-81bd-4cfe-a2f4-d7737ae8c942",
                "provider": "github",
                "status": "succeeded",
                "requested_scopes": ["repo"],
                "return_url": "https://app.test/connectors/github",
                "credential_record_id": "550ac282-c9af-48fc-8e03-0d225d560ff2",
                "error_code": None,
                "error_description": None,
                "expires_at": "2026-05-06T10:15:00Z",
                "completed_at": "2026-05-06T10:11:00Z",
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = ConnectorAuthorizationClient(
        control_plane_url="https://control.test",
        credential_service_url="https://credentials.test",
        http_client=http_client,
    )

    status = client.get_authorization_session("ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556")

    assert isinstance(status, OAuthAuthorizationSessionStatus)
    assert status.status == "succeeded"
    assert status.credential_record_id == "550ac282-c9af-48fc-8e03-0d225d560ff2"
    assert requests == [
        (
            "https://credentials.test/api/v1/credentials/oauth/sessions/"
            "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556"
        )
    ]
    client.close()


def test_authorization_http_error_maps_to_oauth_authorization_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Connector instance was not found."})

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = ConnectorAuthorizationClient(
        control_plane_url="https://control.test",
        http_client=http_client,
    )

    with pytest.raises(OAuthAuthorizationError) as exc_info:
        client.start_authorization(
            connector_instance_id="7f046781-81bd-4cfe-a2f4-d7737ae8c942",
        )

    assert exc_info.value.code == "authorization_http_error"
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Connector instance was not found."
    client.close()


@pytest.mark.anyio
async def test_async_start_authorization_posts_to_control_plane() -> None:
    requests: list[dict] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            201,
            json={
                "connector_instance_id": "7f046781-81bd-4cfe-a2f4-d7737ae8c942",
                "oauth_session_id": "ea78b9fb-ae62-4a18-b5d2-a9f46fb4a556",
                "authorization_url": "https://provider.test/oauth/authorize?state=abc",
                "expires_at": "2026-05-06T10:15:00Z",
            },
        )

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = AsyncConnectorAuthorizationClient(
        control_plane_url="https://control.test",
        http_client=http_client,
    )

    session = await client.start_authorization(
        connector_instance_id="7f046781-81bd-4cfe-a2f4-d7737ae8c942",
        requested_scopes=["repo"],
    )

    assert session.authorization_url.startswith("https://provider.test/oauth/authorize")
    assert requests == [{"requested_scopes": ["repo"]}]
    await client.aclose()
