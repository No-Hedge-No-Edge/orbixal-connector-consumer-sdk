"""Ergonomic result objects for consumer SDK callers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from connector_consumer_sdk.generated.result_models import ColumnDef, RecordItem, RowItem


@dataclass(slots=True, kw_only=True)
class ConnectorResult:
    """Base normalized result object returned by the client."""

    kind: str
    cursor: str | None
    meta: dict[str, Any]
    raw: dict[str, Any] | None = None


@dataclass(slots=True, kw_only=True)
class RecordsResult(ConnectorResult):
    """Normalized records result."""

    records: list[RecordItem] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class TabularResult(ConnectorResult):
    """Normalized tabular result."""

    columns: list[ColumnDef] = field(default_factory=list)
    rows: list[RowItem] = field(default_factory=list)
