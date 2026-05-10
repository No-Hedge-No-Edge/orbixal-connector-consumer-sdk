"""Generated typed action wrappers from connector manifests. Do not edit by hand."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


__all__ = ['CompanyIntelligenceGetAnalystSnapshot', 'CompanyIntelligenceGetCompanyContextForSymbols', 'CompanyIntelligenceGetCompanyProfile', 'CompanyIntelligenceGetEarningsContext', 'CompanyIntelligenceGetFinancialHighlights', 'CompanyIntelligenceGetPeerComparison', 'CompanyIntelligenceGetValuationSnapshot', 'GithubGetIssue', 'GithubSearchIssues', 'InstrumentReferenceGetCorporateActions', 'InstrumentReferenceGetMarketCalendar', 'InstrumentReferenceGetSecurityProfile', 'InstrumentReferenceGetSplitsDividends', 'InstrumentReferenceMapIssuerToSymbols', 'InstrumentReferenceResolveInstrument', 'InstrumentReferenceSearchSymbols', 'JournalActivityContextGetRecentWorkflowCases', 'JournalActivityContextGetRiskNotes', 'JournalActivityContextGetSymbolActivity', 'JournalActivityContextListRecentTrades', 'JournalActivityContextSearchJournalEntries', 'JournalActivityContextSummarizeDecisionHistory', 'MacroLatestReleases', 'MarketIntelCompanyNews', 'MarketIntelEarningsCalendar', 'MarketIntelGetQuote', 'MarketIntelInsiderTransactions', 'MarketIntelInstitutionalOwnership', 'MarketIntelMarketNews', 'PortfolioContextGetSummary', 'PortfolioContextListPositions', 'ResearchContextGetResearchContextForSymbols', 'ResearchContextGetSymbolThesis', 'ResearchContextListPrivateDatasets', 'ResearchContextQueryPrivateDataset', 'ResearchContextSearchNotes', 'RiskAnalyticsCalculateConcentration', 'RiskAnalyticsCalculateDrift', 'RiskAnalyticsCalculateExposure', 'RiskAnalyticsCheckRiskLimits', 'RiskAnalyticsGenerateRiskBrief', 'RiskAnalyticsProposeRebalance', 'RiskAnalyticsRunStressTest', 'SecGetCompanyFacts', 'SecListFilings', 'SecSearchCompanies', 'WatchlistContextGetWatchlistSnapshot']


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetCompanyProfile:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_company_profile"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetFinancialHighlights:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_financial_highlights"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetValuationSnapshot:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_valuation_snapshot"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetAnalystSnapshot:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_analyst_snapshot"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetEarningsContext:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_earnings_context"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetCompanyContextForSymbols:
    identifier: str | None = None
    limit: int | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_company_context_for_symbols"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class CompanyIntelligenceGetPeerComparison:
    symbol: str
    identifier: str | None = None
    limit: int | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_peer_comparison"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class GithubGetIssue:
    issue_number: int
    repo: str | None = None
    name: str = "get_issue"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["issue_number"] = self.issue_number
        if self.repo is not None:
            payload["repo"] = self.repo
        return payload


@dataclass(frozen=True, slots=True)
class GithubSearchIssues:
    query: str
    name: str = "search_issues"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["query"] = self.query
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceSearchSymbols:
    query: str
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    symbol: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "search_symbols"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["query"] = self.query
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceResolveInstrument:
    symbol: str
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    query: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "resolve_instrument"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceGetSecurityProfile:
    symbol: str
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    query: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "get_security_profile"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceGetMarketCalendar:
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "get_market_calendar"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceGetCorporateActions:
    symbol: str
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    query: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "get_corporate_actions"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceGetSplitsDividends:
    symbol: str
    from_date: str | None = None
    identifier: str | None = None
    issuer: str | None = None
    limit: int | None = None
    query: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "get_splits_dividends"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.issuer is not None:
            payload["issuer"] = self.issuer
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class InstrumentReferenceMapIssuerToSymbols:
    issuer: str
    from_date: str | None = None
    identifier: str | None = None
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    ticker: str | None = None
    to_date: str | None = None
    name: str = "map_issuer_to_symbols"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["issuer"] = self.issuer
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.identifier is not None:
            payload["identifier"] = self.identifier
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextListRecentTrades:
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "list_recent_trades"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextSearchJournalEntries:
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "search_journal_entries"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextGetRecentWorkflowCases:
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_recent_workflow_cases"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextGetRiskNotes:
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_risk_notes"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextGetSymbolActivity:
    symbol: str
    limit: int | None = None
    query: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "get_symbol_activity"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class JournalActivityContextSummarizeDecisionHistory:
    limit: int | None = None
    query: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    ticker: str | None = None
    name: str = "summarize_decision_history"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        if self.ticker is not None:
            payload["ticker"] = self.ticker
        return payload


@dataclass(frozen=True, slots=True)
class MacroLatestReleases:
    limit: int | None = None
    name: str = "latest_releases"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelGetQuote:
    symbol: str
    name: str = "get_quote"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelCompanyNews:
    symbol: str
    from_date: str | None = None
    limit: int | None = None
    to_date: str | None = None
    name: str = "company_news"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelMarketNews:
    category: str | None = None
    limit: int | None = None
    name: str = "market_news"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.category is not None:
            payload["category"] = self.category
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelEarningsCalendar:
    from_date: str | None = None
    limit: int | None = None
    symbol: str | None = None
    to_date: str | None = None
    name: str = "earnings_calendar"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelInsiderTransactions:
    symbol: str
    from_date: str | None = None
    limit: int | None = None
    to_date: str | None = None
    name: str = "insider_transactions"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.from_date is not None:
            payload["from_date"] = self.from_date
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.to_date is not None:
            payload["to_date"] = self.to_date
        return payload


@dataclass(frozen=True, slots=True)
class MarketIntelInstitutionalOwnership:
    symbol: str
    limit: int | None = None
    name: str = "institutional_ownership"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(frozen=True, slots=True)
class PortfolioContextListPositions:
    account_id: str | None = None
    authorization_id: str | None = None
    name: str = "list_positions"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.account_id is not None:
            payload["account_id"] = self.account_id
        if self.authorization_id is not None:
            payload["authorization_id"] = self.authorization_id
        return payload


@dataclass(frozen=True, slots=True)
class PortfolioContextGetSummary:
    account_id: str | None = None
    authorization_id: str | None = None
    name: str = "get_summary"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.account_id is not None:
            payload["account_id"] = self.account_id
        if self.authorization_id is not None:
            payload["authorization_id"] = self.authorization_id
        return payload


@dataclass(frozen=True, slots=True)
class ResearchContextSearchNotes:
    dataset_id: str | None = None
    limit: int | None = None
    query: str | None = None
    status: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    name: str = "search_notes"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.dataset_id is not None:
            payload["dataset_id"] = self.dataset_id
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.status is not None:
            payload["status"] = self.status
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        return payload


@dataclass(frozen=True, slots=True)
class ResearchContextGetSymbolThesis:
    symbol: str
    dataset_id: str | None = None
    limit: int | None = None
    query: str | None = None
    status: str | None = None
    symbols: list[object] | None = None
    name: str = "get_symbol_thesis"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["symbol"] = self.symbol
        if self.dataset_id is not None:
            payload["dataset_id"] = self.dataset_id
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.status is not None:
            payload["status"] = self.status
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        return payload


@dataclass(frozen=True, slots=True)
class ResearchContextGetResearchContextForSymbols:
    dataset_id: str | None = None
    limit: int | None = None
    query: str | None = None
    status: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    name: str = "get_research_context_for_symbols"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.dataset_id is not None:
            payload["dataset_id"] = self.dataset_id
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.status is not None:
            payload["status"] = self.status
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        return payload


@dataclass(frozen=True, slots=True)
class ResearchContextListPrivateDatasets:
    dataset_id: str | None = None
    limit: int | None = None
    query: str | None = None
    status: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    name: str = "list_private_datasets"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.dataset_id is not None:
            payload["dataset_id"] = self.dataset_id
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.status is not None:
            payload["status"] = self.status
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        return payload


@dataclass(frozen=True, slots=True)
class ResearchContextQueryPrivateDataset:
    dataset_id: str | None = None
    limit: int | None = None
    query: str | None = None
    status: str | None = None
    symbol: str | None = None
    symbols: list[object] | None = None
    name: str = "query_private_dataset"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.dataset_id is not None:
            payload["dataset_id"] = self.dataset_id
        if self.limit is not None:
            payload["limit"] = self.limit
        if self.query is not None:
            payload["query"] = self.query
        if self.status is not None:
            payload["status"] = self.status
        if self.symbol is not None:
            payload["symbol"] = self.symbol
        if self.symbols is not None:
            payload["symbols"] = self.symbols
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsCalculateExposure:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "calculate_exposure"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsCalculateConcentration:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "calculate_concentration"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsCalculateDrift:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "calculate_drift"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsRunStressTest:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "run_stress_test"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsCheckRiskLimits:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "check_risk_limits"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsProposeRebalance:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "propose_rebalance"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class RiskAnalyticsGenerateRiskBrief:
    limits: dict[str, Any] | None = None
    portfolio: dict[str, Any] | None = None
    portfolio_beta: float | None = None
    positions: list[object] | None = None
    target_allocation: dict[str, Any] | None = None
    name: str = "generate_risk_brief"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.limits is not None:
            payload["limits"] = self.limits
        if self.portfolio is not None:
            payload["portfolio"] = self.portfolio
        if self.portfolio_beta is not None:
            payload["portfolio_beta"] = self.portfolio_beta
        if self.positions is not None:
            payload["positions"] = self.positions
        if self.target_allocation is not None:
            payload["target_allocation"] = self.target_allocation
        return payload


@dataclass(frozen=True, slots=True)
class SecSearchCompanies:
    query: str
    limit: int | None = None
    name: str = "search_companies"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["query"] = self.query
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(frozen=True, slots=True)
class SecListFilings:
    identifier: str
    forms: list[object] | None = None
    limit: int | None = None
    name: str = "list_filings"
    operation: Literal["query"] = "query"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["identifier"] = self.identifier
        if self.forms is not None:
            payload["forms"] = self.forms
        if self.limit is not None:
            payload["limit"] = self.limit
        return payload


@dataclass(frozen=True, slots=True)
class SecGetCompanyFacts:
    identifier: str
    name: str = "get_company_facts"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["identifier"] = self.identifier
        return payload


@dataclass(frozen=True, slots=True)
class WatchlistContextGetWatchlistSnapshot:
    watchlist_id: str
    max_pages: int | None = None
    page_limit: int | None = None
    name: str = "get_watchlist_snapshot"
    operation: Literal["read"] = "read"

    def params(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        payload["watchlist_id"] = self.watchlist_id
        if self.max_pages is not None:
            payload["max_pages"] = self.max_pages
        if self.page_limit is not None:
            payload["page_limit"] = self.page_limit
        return payload
