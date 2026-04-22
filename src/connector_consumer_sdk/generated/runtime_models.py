
# Generated from canonical contract schemas. Do not edit by hand.

from typing import Any, Literal, TypedDict


RuntimeOperation = Literal['describe', 'test_connection', 'list_resources', 'read', 'query']


class ExecutionContext(TypedDict, total=False):
    pipeline_id: str
    agent_node_id: str
    request_id: str


class RuntimeInput(TypedDict, total=False):
    action: str
    params: dict[str, Any]
    cursor: str | None
    include_raw: bool
    mode: Literal["fast", "full"]
    query: dict[str, Any]


class RuntimeExecuteRequest(TypedDict, total=False):
    connector_instance_id: str
    pipeline_id: str
    agent_node_id: str
    input_name: str
    operation: RuntimeOperation
    input: RuntimeInput
    execution_context: ExecutionContext


DIRECT_EXECUTION_KEYS = ("connector_instance_id",)
BOUND_EXECUTION_KEYS = ("pipeline_id", "agent_node_id", "input_name")
