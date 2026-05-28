
# Generated from canonical contract schemas. Do not edit by hand.

from typing import Any, Literal, TypedDict


class ExecutionReceipt(TypedDict, total=False):
    receipt_id: str
    request_id: str
    connector_instance_id: str
    connector_key: str
    connector_version: str
    operation: str
    action: str | None
    connector_mode: str
    status: Literal["succeeded", "failed"]
    approval_id: str | None
    idempotency_key: str | None
    compensation_available: bool
    compensation_action: str | None
    payload_hash: str
    result_hash: str


class RecordItem(TypedDict, total=False):
    id: str
    type: str
    title: str | None
    content: dict[str, Any]
    attributes: dict[str, Any]
    timestamps: dict[str, Any]
    source: dict[str, Any]


class RecordsMetaRequired(TypedDict):
    connector_key: str
    connector_version: str
    action: str
    request_id: str


class RecordsMeta(RecordsMetaRequired, total=False):
    receipt: ExecutionReceipt
    entitlement: dict[str, Any] | None


class RecordsEnvelope(TypedDict, total=False):
    kind: Literal['records']
    records: list[RecordItem]
    cursor: str | None
    meta: RecordsMeta
    raw: dict[str, Any]


class ColumnDef(TypedDict):
    name: str
    type: str


class RowItem(TypedDict):
    row_id: str
    values: dict[str, Any]


class TabularMetaRequired(TypedDict):
    connector_key: str
    connector_version: str
    action: str
    request_id: str


class TabularMeta(TabularMetaRequired, total=False):
    receipt: ExecutionReceipt
    entitlement: dict[str, Any] | None


class TabularEnvelope(TypedDict, total=False):
    kind: Literal['tabular']
    columns: list[ColumnDef]
    rows: list[RowItem]
    cursor: str | None
    meta: TabularMeta
    raw: dict[str, Any]
