from __future__ import annotations

import json

import httpx

from connector_consumer_sdk import ConnectorClient, ConnectorExecutionContext, RecordsResult
from connector_consumer_sdk.transport import HTTPConnectorTransport


def test_consumer_sdk_bound_query_matches_runtime_execute_contract() -> None:
    captured_payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payloads.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [{"id": "issue_1", "type": "issue"}],
                "cursor": None,
                "meta": {
                    "connector_key": "github",
                    "connector_version": "1.0.1",
                    "action": "search_issues",
                    "request_id": "req_contract",
                },
                "raw": None,
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPConnectorTransport(
        runtime_url="https://runtime.test",
        http_client=http_client,
    )
    client = ConnectorClient(
        transport=transport,
        execution_context=ConnectorExecutionContext(
            pipeline_id="pipe_1",
            agent_node_id="node_1",
            request_id="req_contract",
        ),
    )

    result = client.input("issue_source").query(
        "search_issues",
        {"query": "label:bug"},
    )

    assert isinstance(result, RecordsResult)
    assert result.request_id == "req_contract"
    assert captured_payloads == [
        {
            "pipeline_id": "pipe_1",
            "agent_node_id": "node_1",
            "input_name": "issue_source",
            "operation": "query",
            "input": {
                "action": "search_issues",
                "params": {"query": "label:bug"},
                "include_raw": False,
            },
            "execution_context": {
                "pipeline_id": "pipe_1",
                "agent_node_id": "node_1",
                "request_id": "req_contract",
            },
        }
    ]
    client.close()
