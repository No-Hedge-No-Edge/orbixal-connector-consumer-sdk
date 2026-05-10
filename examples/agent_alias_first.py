"""Alias-first Consumer SDK usage from an agent node."""

from __future__ import annotations

from connector_consumer_sdk import (
    ConnectorClient,
    ConnectorExecutionContext,
    ProviderRateLimitedError,
)


def run_agent_step() -> list[str]:
    context = ConnectorExecutionContext(
        pipeline_id="pipe_1",
        agent_node_id="node_1",
        request_id="req_agent_step_123",
    )
    with ConnectorClient(
        runtime_url="http://runtime-service:8002",
        execution_context=context,
    ) as client:
        issues = client.input("issue_source")
        try:
            result = issues.query(
                "search_issues",
                {"query": "repo:orbixal/platform label:bug"},
            )
        except ProviderRateLimitedError as exc:
            retry_after = exc.retry_after_seconds
            raise RuntimeError(
                f"Provider rate limited; retry recommendation={exc.retry_recommendation}, "
                f"retry_after={retry_after}."
            ) from exc

    return [record["id"] for record in result]
