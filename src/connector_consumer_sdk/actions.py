"""Typed action helpers for common first-party connector operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol


class ConnectorAction(Protocol):
    """Minimal contract for typed connector action wrappers."""

    name: str
    operation: Literal["read", "query"]

    def params(self) -> dict[str, object]:
        """Return runtime params for this action."""


@dataclass(frozen=True, slots=True)
class GitHubSearchIssues:
    query: str
    name: str = "search_issues"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        return {"query": self.query}


@dataclass(frozen=True, slots=True)
class GitHubGetIssue:
    repo: str
    issue_number: int
    name: str = "get_issue"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        return {"repo": self.repo, "issue_number": self.issue_number}


@dataclass(frozen=True, slots=True)
class SECSearchCompanies:
    query: str
    name: str = "search_companies"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        return {"query": self.query}


@dataclass(frozen=True, slots=True)
class SECGetCompanyFacts:
    cik: str
    name: str = "get_company_facts"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        return {"cik": self.cik}


@dataclass(frozen=True, slots=True)
class MarketIntelGetQuote:
    symbol: str
    name: str = "get_quote"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        return {"symbol": self.symbol}


@dataclass(frozen=True, slots=True)
class MarketIntelCompanyNews:
    symbol: str
    limit: int = 10
    name: str = "company_news"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        return {"symbol": self.symbol, "limit": self.limit}


@dataclass(frozen=True, slots=True)
class TabularReadRows:
    sheet: str
    limit: int | None = None
    name: str = "read_rows"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {"sheet": self.sheet}
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload
