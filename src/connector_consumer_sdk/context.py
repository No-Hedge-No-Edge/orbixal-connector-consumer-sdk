"""Execution-context helpers for the consumer SDK."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConnectorExecutionContext:
    """Bound execution context for pipeline-scoped connector access."""

    pipeline_id: str
    agent_node_id: str
    request_id: str | None = None

    def as_runtime_execution_context(self) -> dict[str, str]:
        """Return the canonical runtime execution-context payload."""

        payload: dict[str, str] = {
            "pipeline_id": self.pipeline_id,
            "agent_node_id": self.agent_node_id,
        }
        if self.request_id is not None:
            payload["request_id"] = self.request_id
        return payload
