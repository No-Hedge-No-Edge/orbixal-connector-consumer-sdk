
# Generated from canonical contract schemas. Do not edit by hand.

from typing import Any, Literal, TypedDict


class OperationDescriptor(TypedDict):
    name: str
    kind: Literal['read', 'query']


class ConnectorDescription(TypedDict):
    connector_instance_id: str
    connector_key: str
    connector_version: str
    capabilities: list[str]
    operations: list[OperationDescriptor]
    resource_types: list[str]
    auth_type: str | None


class ResourceItem(TypedDict):
    id: str
    type: str
    name: str
    attributes: dict[str, Any]


class ResourcePage(TypedDict):
    items: list[ResourceItem]
    cursor: str | None
