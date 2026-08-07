"""Execution-context helpers for the consumer SDK."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any


_RUNTIME_CONTEXT_KEYS = {
    "org_id",
    "project_id",
    "pipeline_id",
    "pipeline_run_id",
    "step_id",
    "step_execution_id",
    "agent_node_id",
    "trace_id",
    "request_id",
    "approval_context",
    "lockfile_checksum",
    "connector_bindings",
    "dependency_lock",
}


def _non_empty(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _project_id(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


@dataclass(frozen=True, slots=True)
class ConnectorExecutionContext:
    """Bound execution context for pipeline-scoped connector access."""

    pipeline_id: str
    agent_node_id: str
    request_id: str | None = None
    org_id: str | None = None
    project_id: int | None = None
    pipeline_run_id: str | None = None
    step_id: str | None = None
    step_execution_id: str | None = None
    trace_id: str | None = None
    approval_context: dict[str, Any] | None = None
    lockfile_checksum: str | None = None
    connector_bindings: list[dict[str, Any]] | None = None
    dependency_lock: dict[str, Any] | None = None

    @classmethod
    def from_environment(cls) -> "ConnectorExecutionContext | None":
        """Build context from Orbixal runner environment variables when available."""

        raw_context = os.environ.get("ORBIXAL_RUNTIME_EXECUTION_CONTEXT")
        parsed_context: dict[str, Any] = {}
        if raw_context:
            try:
                loaded = json.loads(raw_context)
            except json.JSONDecodeError:
                loaded = {}
            if isinstance(loaded, dict):
                parsed_context = {key: loaded.get(key) for key in _RUNTIME_CONTEXT_KEYS if key in loaded}

        env_context = {
            "org_id": os.environ.get("ORBIXAL_PIPELINE_ORG_ID"),
            "project_id": os.environ.get("ORBIXAL_PIPELINE_PROJECT_ID"),
            "pipeline_id": os.environ.get("ORBIXAL_PIPELINE_ID"),
            "pipeline_run_id": os.environ.get("ORBIXAL_PIPELINE_RUN_ID"),
            "step_id": os.environ.get("ORBIXAL_PIPELINE_STEP_ID"),
            "step_execution_id": os.environ.get("ORBIXAL_PIPELINE_STEP_EXECUTION_ID"),
            "agent_node_id": os.environ.get("ORBIXAL_PIPELINE_STEP_ID"),
            "trace_id": os.environ.get("ORBIXAL_PIPELINE_TRACE_ID"),
        }
        merged = {**env_context, **{key: value for key, value in parsed_context.items() if value is not None}}

        pipeline_id = _non_empty(merged.get("pipeline_id"))
        agent_node_id = _non_empty(merged.get("agent_node_id") or merged.get("step_id"))
        if pipeline_id is None or agent_node_id is None:
            return None

        return cls(
            pipeline_id=pipeline_id,
            agent_node_id=agent_node_id,
            request_id=_non_empty(merged.get("request_id")),
            org_id=_non_empty(merged.get("org_id")),
            project_id=_project_id(merged.get("project_id")),
            pipeline_run_id=_non_empty(merged.get("pipeline_run_id")),
            step_id=_non_empty(merged.get("step_id")),
            step_execution_id=_non_empty(merged.get("step_execution_id")),
            trace_id=_non_empty(merged.get("trace_id")),
            approval_context=(
                dict(merged["approval_context"]) if isinstance(merged.get("approval_context"), dict) else None
            ),
            lockfile_checksum=_non_empty(merged.get("lockfile_checksum")),
            connector_bindings=(
                [dict(item) for item in merged["connector_bindings"] if isinstance(item, dict)]
                if isinstance(merged.get("connector_bindings"), list)
                else None
            ),
            dependency_lock=(dict(merged["dependency_lock"]) if isinstance(merged.get("dependency_lock"), dict) else None),
        )

    def with_environment_defaults(self) -> "ConnectorExecutionContext":
        """Fill missing fields from runner-provided environment context."""

        environment_context = self.from_environment()
        if environment_context is None:
            return self
        return ConnectorExecutionContext(
            pipeline_id=self.pipeline_id or environment_context.pipeline_id,
            agent_node_id=self.agent_node_id or environment_context.agent_node_id,
            request_id=self.request_id or environment_context.request_id,
            org_id=self.org_id or environment_context.org_id,
            project_id=self.project_id if self.project_id is not None else environment_context.project_id,
            pipeline_run_id=self.pipeline_run_id or environment_context.pipeline_run_id,
            step_id=self.step_id or environment_context.step_id,
            step_execution_id=self.step_execution_id or environment_context.step_execution_id,
            trace_id=self.trace_id or environment_context.trace_id,
            approval_context=self.approval_context or environment_context.approval_context,
            lockfile_checksum=self.lockfile_checksum or environment_context.lockfile_checksum,
            connector_bindings=self.connector_bindings or environment_context.connector_bindings,
            dependency_lock=self.dependency_lock or environment_context.dependency_lock,
        )

    def as_runtime_execution_context(self) -> dict[str, Any]:
        """Return the canonical runtime execution-context payload."""

        payload: dict[str, Any] = {
            "pipeline_id": self.pipeline_id,
            "agent_node_id": self.agent_node_id,
        }
        if self.org_id is not None:
            payload["org_id"] = self.org_id
        if self.project_id is not None:
            payload["project_id"] = self.project_id
        if self.pipeline_run_id is not None:
            payload["pipeline_run_id"] = self.pipeline_run_id
        if self.step_id is not None:
            payload["step_id"] = self.step_id
        if self.step_execution_id is not None:
            payload["step_execution_id"] = self.step_execution_id
        if self.trace_id is not None:
            payload["trace_id"] = self.trace_id
        if self.request_id is not None:
            payload["request_id"] = self.request_id
        if self.lockfile_checksum is not None:
            payload["lockfile_checksum"] = self.lockfile_checksum
        if self.connector_bindings:
            payload["connector_bindings"] = [dict(item) for item in self.connector_bindings]
        if self.dependency_lock:
            payload["dependency_lock"] = dict(self.dependency_lock)
        return payload

    def as_approval_context(self) -> dict[str, Any] | None:
        """Return approval context for runtime requests when this run resumed from an approval gate."""

        return dict(self.approval_context) if isinstance(self.approval_context, dict) else None
