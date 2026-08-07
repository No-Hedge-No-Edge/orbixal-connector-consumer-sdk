"""Ergonomic result objects for consumer SDK callers."""

from __future__ import annotations

from collections.abc import Iterator
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

    @property
    def has_more(self) -> bool:
        return self.cursor is not None

    @property
    def connector_key(self) -> str | None:
        value = self.meta.get("connector_key")
        return value if isinstance(value, str) else None

    @property
    def connector_version(self) -> str | None:
        value = self.meta.get("connector_version")
        return value if isinstance(value, str) else None

    @property
    def action(self) -> str | None:
        value = self.meta.get("action")
        return value if isinstance(value, str) else None

    @property
    def request_id(self) -> str | None:
        value = self.meta.get("request_id")
        return value if isinstance(value, str) else None


@dataclass(slots=True, kw_only=True)
class RecordsResult(ConnectorResult):
    """Normalized records result."""

    records: list[RecordItem] = field(default_factory=list)

    def __iter__(self) -> Iterator[RecordItem]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def first(self) -> RecordItem | None:
        return self.records[0] if self.records else None

    def require_first(self) -> RecordItem:
        record = self.first()
        if record is None:
            raise ValueError("RecordsResult is empty.")
        return record

    def to_list(self) -> list[RecordItem]:
        return list(self.records)

    def content_texts(self) -> list[str]:
        texts: list[str] = []
        for record in self.records:
            content = record.get("content")
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str):
                texts.append(text)
        return texts


@dataclass(slots=True, kw_only=True)
class TabularResult(ConnectorResult):
    """Normalized tabular result."""

    columns: list[ColumnDef] = field(default_factory=list)
    rows: list[RowItem] = field(default_factory=list)

    def __iter__(self) -> Iterator[RowItem]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    @property
    def column_names(self) -> list[str]:
        return [column["name"] for column in self.columns]

    def values(self) -> list[dict[str, Any]]:
        return [dict(row["values"]) for row in self.rows]

    def first_row(self) -> dict[str, Any] | None:
        return dict(self.rows[0]["values"]) if self.rows else None

    def require_first_row(self) -> dict[str, Any]:
        row = self.first_row()
        if row is None:
            raise ValueError("TabularResult is empty.")
        return row
