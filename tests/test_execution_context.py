from __future__ import annotations

import json

import httpx

from connector_consumer_sdk import ConnectorClient, ConnectorExecutionContext
from connector_consumer_sdk.transport import HTTPConnectorTransport


def test_execution_context_loads_runner_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "ORBIXAL_RUNTIME_EXECUTION_CONTEXT",
        json.dumps(
            {
                "schema_version": 1,
                "org_id": "org_123",
                "project_id": 42,
                "pipeline_id": "pipe_123",
                "pipeline_run_id": "run_123",
                "step_id": "agent_step",
                "step_execution_id": "step_exec_123",
                "attempt": 1,
                "trace_id": "trace_123",
                "approval_context": {
                    "approval_id": "appr_123",
                    "status": "approved",
                    "approved_by": "user_123",
                    "policy_key": "gmail.send",
                },
            }
        ),
    )

    context = ConnectorExecutionContext.from_environment()

    assert context is not None
    assert context.as_runtime_execution_context() == {
        "pipeline_id": "pipe_123",
        "agent_node_id": "agent_step",
        "org_id": "org_123",
        "project_id": 42,
        "pipeline_run_id": "run_123",
        "step_id": "agent_step",
        "step_execution_id": "step_exec_123",
        "trace_id": "trace_123",
    }
    assert context.as_approval_context() == {
        "approval_id": "appr_123",
        "status": "approved",
        "approved_by": "user_123",
        "policy_key": "gmail.send",
    }


def test_execution_context_merges_explicit_context_with_runner_defaults(monkeypatch) -> None:
    monkeypatch.setenv("ORBIXAL_PIPELINE_ORG_ID", "org_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_PROJECT_ID", "42")
    monkeypatch.setenv("ORBIXAL_PIPELINE_ID", "pipe_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_RUN_ID", "run_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_STEP_ID", "agent_step")
    monkeypatch.setenv("ORBIXAL_PIPELINE_STEP_EXECUTION_ID", "step_exec_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_TRACE_ID", "trace_123")

    context = ConnectorExecutionContext(
        pipeline_id="explicit_pipe",
        agent_node_id="explicit_node",
        request_id="req_123",
    ).with_environment_defaults()

    assert context.as_runtime_execution_context() == {
        "pipeline_id": "explicit_pipe",
        "agent_node_id": "explicit_node",
        "org_id": "org_123",
        "project_id": 42,
        "pipeline_run_id": "run_123",
        "step_id": "agent_step",
        "step_execution_id": "step_exec_123",
        "trace_id": "trace_123",
        "request_id": "req_123",
    }


def test_client_uses_runner_environment_context_by_default(monkeypatch) -> None:
    monkeypatch.setenv("ORBIXAL_PIPELINE_ORG_ID", "org_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_PROJECT_ID", "42")
    monkeypatch.setenv("ORBIXAL_PIPELINE_ID", "pipe_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_RUN_ID", "run_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_STEP_ID", "agent_step")
    monkeypatch.setenv("ORBIXAL_PIPELINE_STEP_EXECUTION_ID", "step_exec_123")
    monkeypatch.setenv("ORBIXAL_PIPELINE_TRACE_ID", "trace_123")
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode("utf-8")))
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
    transport = HTTPConnectorTransport(runtime_url="https://runtime.test", http_client=http_client)

    with ConnectorClient(transport=transport) as client:
        client.describe_input("issue_source")

    assert requests == [
        {
            "pipeline_id": "pipe_123",
            "agent_node_id": "agent_step",
            "input_name": "issue_source",
            "operation": "describe",
            "execution_context": {
                "pipeline_id": "pipe_123",
                "agent_node_id": "agent_step",
                "org_id": "org_123",
                "project_id": 42,
                "pipeline_run_id": "run_123",
                "step_id": "agent_step",
                "step_execution_id": "step_exec_123",
                "trace_id": "trace_123",
            },
        }
    ]


def test_client_adds_approval_context_from_runner_environment(monkeypatch) -> None:
    monkeypatch.setenv(
        "ORBIXAL_RUNTIME_EXECUTION_CONTEXT",
        json.dumps(
            {
                "schema_version": 1,
                "org_id": "org_123",
                "project_id": 42,
                "pipeline_id": "pipe_123",
                "pipeline_run_id": "run_123",
                "step_id": "agent_step",
                "trace_id": "trace_123",
                "approval_context": {
                    "approval_id": "appr_123",
                    "status": "approved",
                    "approved_by": "user_123",
                    "policy_key": "gmail.send",
                },
            }
        ),
    )
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            200,
            json={
                "kind": "records",
                "records": [],
                "cursor": None,
                "meta": {"request_id": "req_123"},
                "raw": None,
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = HTTPConnectorTransport(runtime_url="https://runtime.test", http_client=http_client)

    with ConnectorClient(transport=transport) as client:
        client.input("mailbox").query("search_messages", {"query": "from:buyer@example.com"})

    assert requests[0]["approval_context"] == {
        "approval_id": "appr_123",
        "status": "approved",
        "approved_by": "user_123",
        "policy_key": "gmail.send",
    }
