from __future__ import annotations

import json

import httpx
import pytest

from connector_consumer_sdk import (
    AsyncConnectorClient,
    BindingNotFoundError,
    ConnectorClient,
    ConnectorExecutionContext,
    ConnectorNotAvailableError,
    CredentialResolutionError,
    InvalidRuntimeRequestError,
    ProviderUnavailableError,
    RecordsResult,
    ResultNormalizationError,
    TabularResult,
)
from connector_consumer_sdk.transport import HTTPAsyncConnectorTransport, HTTPConnectorTransport


def build_client(
    handler,
    *,
    execution_context: ConnectorExecutionContext | None = None,
) -> ConnectorClient:
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPConnectorTransport(
        runtime_url="https://runtime.test",
        http_client=http_client,
    )
    return ConnectorClient(
        transport=transport,
        execution_context=execution_context,
    )


def build_async_client(
    handler,
    *,
    execution_context: ConnectorExecutionContext | None = None,
) -> AsyncConnectorClient:
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HTTPAsyncConnectorTransport(
        runtime_url="https://runtime.test",
        http_client=http_client,
    )
    return AsyncConnectorClient(
        transport=transport,
        execution_context=execution_context,
    )


def test_transport_applies_auth_header_with_injected_http_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token_123"
        return httpx.Response(
            200,
            json={
                "connector_instance_id": "conninst_123",
                "connector_key": "github",
                "connector_version": "1.0.0",
                "capabilities": [],
                "operations": [],
                "resource_types": [],
                "auth_type": "oauth2",
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPConnectorTransport(
        runtime_url="https://runtime.test",
        auth_token="token_123",
        http_client=http_client,
    )
    client = ConnectorClient(transport=transport)

    description = client.describe("conninst_123")

    assert description["connector_instance_id"] == "conninst_123"
    client.close()


def test_describe_input_posts_bound_request_and_returns_description() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode("utf-8")))
        assert request.url == "https://runtime.test/api/v1/runtime/execute"
        return httpx.Response(
            200,
            json={
                "connector_instance_id": "conninst_123",
                "connector_key": "github",
                "connector_version": "1.0.0",
                "capabilities": ["record_get", "search"],
                "operations": [{"name": "get_issue", "kind": "read"}],
                "resource_types": ["repository"],
                "auth_type": "oauth2",
            },
        )

    client = build_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
            request_id="req_123",
        ),
    )

    description = client.describe_input("issue_source")

    assert description["connector_key"] == "github"
    assert requests == [
        {
            "pipeline_id": "pipe_1",
            "agent_node_id": "node_1",
            "input_name": "issue_source",
            "operation": "describe",
            "execution_context": {
                "pipeline_id": "pipe_1",
                "agent_node_id": "node_1",
                "request_id": "req_123",
            },
        }
    ]
    client.close()


def test_query_from_input_returns_records_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["input"] == {
            "action": "search_issues",
            "params": {"query": "label:bug"},
            "include_raw": False,
        }
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [
                    {
                        "id": "issue_1",
                        "type": "issue",
                        "title": "Broken auth flow",
                        "content": {"text": "Details"},
                        "attributes": {"repo": "orbixal/platform"},
                        "timestamps": {},
                        "source": {"provider_url": "https://example.test/issues/1"},
                    }
                ],
                "cursor": "cursor_1",
                "meta": {
                    "connector_key": "github",
                    "connector_version": "1.0.0",
                    "action": "search_issues",
                    "request_id": "req_123",
                },
                "raw": None,
            },
        )

    client = build_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    result = client.query_from_input(
        input_name="issue_source",
        action="search_issues",
        params={"query": "label:bug"},
    )

    assert isinstance(result, RecordsResult)
    assert result.kind == "records"
    assert result.cursor == "cursor_1"
    assert result.records[0]["id"] == "issue_1"
    client.close()


def test_read_returns_tabular_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["operation"] == "read"
        return httpx.Response(
            200,
            json={
                "kind": "tabular",
                "columns": [{"name": "symbol", "type": "string"}],
                "rows": [{"row_id": "1", "values": {"symbol": "AAPL"}}],
                "cursor": None,
                "meta": {
                    "connector_key": "google_sheets",
                    "connector_version": "1.0.0",
                    "action": "read_rows",
                    "request_id": "req_456",
                },
                "raw": {"sheet": "prices"},
            },
        )

    client = build_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    result = client.read_from_input(
        input_name="market_data",
        action="read_rows",
        params={"range": "A1:A2"},
        include_raw=True,
    )

    assert isinstance(result, TabularResult)
    assert result.columns[0]["name"] == "symbol"
    assert result.raw == {"sheet": "prices"}
    client.close()


def test_iter_query_from_input_follows_cursor() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        requests.append(payload)
        cursor = payload.get("input", {}).get("cursor")
        if cursor is None:
            return httpx.Response(
                200,
                json={
                    "kind": "records",
                    "records": [{"id": "issue_1", "type": "issue"}],
                    "cursor": "cursor_1",
                    "meta": {
                        "connector_key": "github",
                        "connector_version": "1.0.0",
                        "action": "search_issues",
                        "request_id": "req_1",
                    },
                },
            )
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [{"id": "issue_2", "type": "issue"}],
                "cursor": None,
                "meta": {
                    "connector_key": "github",
                    "connector_version": "1.0.0",
                    "action": "search_issues",
                    "request_id": "req_2",
                },
            },
        )

    client = build_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    pages = list(
        client.iter_query_from_input(
            input_name="issue_source",
            action="search_issues",
            params={"query": "label:bug"},
        )
    )

    assert [page.records[0]["id"] for page in pages] == ["issue_1", "issue_2"]
    assert requests[1]["input"]["cursor"] == "cursor_1"
    client.close()


def test_bound_instance_not_found_maps_to_binding_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={
                "error": {
                    "code": "instance_not_found",
                    "message": "Pipeline binding was not found.",
                    "retryable": False,
                    "request_id": "req_missing",
                    "details": {"input_name": "issue_source"},
                }
            },
        )

    client = build_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    with pytest.raises(BindingNotFoundError) as exc_info:
        client.describe_input("issue_source")

    assert exc_info.value.code == "instance_not_found"
    assert exc_info.value.request_id == "req_missing"
    client.close()


def test_direct_instance_not_found_maps_to_connector_not_available() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={
                "error": {
                    "code": "instance_not_found",
                    "message": "Connector instance was not found.",
                    "retryable": False,
                    "request_id": "req_missing",
                    "details": {"connector_instance_id": "conninst_123"},
                }
            },
        )

    client = build_client(handler)

    with pytest.raises(ConnectorNotAvailableError) as exc_info:
        client.describe("conninst_123")

    assert exc_info.value.code == "instance_not_found"
    assert exc_info.value.details["connector_instance_id"] == "conninst_123"
    client.close()


def test_invalid_request_maps_to_invalid_runtime_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": "invalid_request",
                    "message": "Request payload validation failed.",
                    "retryable": False,
                    "request_id": "req_invalid",
                    "details": {"errors": [{"loc": ["operation"]}]},
                }
            },
        )

    client = build_client(handler)

    with pytest.raises(InvalidRuntimeRequestError) as exc_info:
        client.describe("conninst_123")

    assert exc_info.value.status_code == 400
    client.close()


def test_credential_resolution_failed_maps_to_specific_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            502,
            json={
                "error": {
                    "code": "credential_resolution_failed",
                    "message": "Credential Service could not resolve credentials.",
                    "retryable": True,
                    "request_id": "req_cred",
                    "details": {"service": "credential_service"},
                }
            },
        )

    client = build_client(handler)

    with pytest.raises(CredentialResolutionError) as exc_info:
        client.describe("conninst_123")

    assert exc_info.value.retryable is True
    client.close()


def test_provider_unavailable_maps_to_provider_unavailable_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={
                "error": {
                    "code": "provider_unavailable",
                    "message": "Provider is unavailable.",
                    "retryable": True,
                    "request_id": "req_provider",
                    "details": {},
                }
            },
        )

    client = build_client(handler)

    with pytest.raises(ProviderUnavailableError) as exc_info:
        client.describe("conninst_123")

    assert exc_info.value.code == "provider_unavailable"
    client.close()


def test_normalization_failed_maps_to_result_normalization_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            502,
            json={
                "error": {
                    "code": "normalization_failed",
                    "message": "Provider output could not be normalized.",
                    "retryable": False,
                    "request_id": "req_norm",
                    "details": {},
                }
            },
        )

    client = build_client(handler)

    with pytest.raises(ResultNormalizationError):
        client.describe("conninst_123")

    client.close()


def test_bound_access_requires_execution_context() -> None:
    client = build_client(lambda request: httpx.Response(200, json={}))

    with pytest.raises(ValueError):
        client.describe_input("issue_source")

    client.close()


@pytest.mark.anyio
async def test_async_query_from_input_returns_records_result() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["operation"] == "query"
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [{"id": "issue_async", "type": "issue"}],
                "cursor": None,
                "meta": {
                    "connector_key": "github",
                    "connector_version": "1.0.0",
                    "action": "search_issues",
                    "request_id": "req_async",
                },
            },
        )

    client = build_async_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    result = await client.query_from_input(
        input_name="issue_source",
        action="search_issues",
        params={"query": "label:bug"},
    )

    assert isinstance(result, RecordsResult)
    assert result.records[0]["id"] == "issue_async"
    await client.aclose()


@pytest.mark.anyio
async def test_async_iter_query_from_input_follows_cursor() -> None:
    requests: list[dict] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        requests.append(payload)
        cursor = payload.get("input", {}).get("cursor")
        if cursor is None:
            return httpx.Response(
                200,
                json={
                    "kind": "records",
                    "records": [{"id": "issue_1", "type": "issue"}],
                    "cursor": "cursor_1",
                    "meta": {
                        "connector_key": "github",
                        "connector_version": "1.0.0",
                        "action": "search_issues",
                        "request_id": "req_1",
                    },
                },
            )
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [{"id": "issue_2", "type": "issue"}],
                "cursor": None,
                "meta": {
                    "connector_key": "github",
                    "connector_version": "1.0.0",
                    "action": "search_issues",
                    "request_id": "req_2",
                },
            },
        )

    client = build_async_client(
        handler,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
        ),
    )

    pages = []
    async for page in client.iter_query_from_input(
        input_name="issue_source",
        action="search_issues",
        params={"query": "label:bug"},
    ):
        pages.append(page)

    assert [page.records[0]["id"] for page in pages] == ["issue_1", "issue_2"]
    assert requests[1]["input"]["cursor"] == "cursor_1"
    await client.aclose()
