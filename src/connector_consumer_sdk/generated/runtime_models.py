
# Generated from canonical contract schemas. Do not edit by hand.

from typing import Any, Literal, TypedDict


RuntimeOperation = Literal['describe', 'test_connection', 'list_resources', 'read', 'query']
ConnectorExecutionMode = Literal['fixture', 'mock', 'record_replay', 'redacted_replay', 'live_read_only', 'live']
ApprovalStatus = Literal['pending', 'approved', 'denied', 'expired']


class ExecutionContext(TypedDict, total=False):
    org_id: str
    project_id: int
    pipeline_id: str
    pipeline_run_id: str
    step_id: str
    step_execution_id: str
    agent_node_id: str
    trace_id: str
    request_id: str


class RuntimeInput(TypedDict, total=False):
    action: str
    params: dict[str, Any]
    cursor: str | None
    include_raw: bool
    mode: Literal["fast", "full"]
    query: dict[str, Any]


class PermissionRequirement(TypedDict, total=False):
    resource_type: str
    resource_id: str | None
    action: str
    scope: str | None
    risk_class: str
    approval_required: bool
    credential_source: str
    data_sensitivity: str
    egress_allowed: bool
    retention_allowed: bool


class ApprovalContext(TypedDict, total=False):
    approval_id: str
    status: ApprovalStatus
    approved_by: str
    policy_key: str


class RuntimeExecuteRequest(TypedDict, total=False):
    connector_instance_id: str
    pipeline_id: str
    agent_node_id: str
    input_name: str
    operation: RuntimeOperation
    input: RuntimeInput
    connector_mode: ConnectorExecutionMode
    permission_contract: list[PermissionRequirement]
    approval_context: ApprovalContext | None
    idempotency_key: str | None
    execution_context: ExecutionContext


DIRECT_EXECUTION_KEYS = ("connector_instance_id",)
BOUND_EXECUTION_KEYS = ("pipeline_id", "agent_node_id", "input_name")
