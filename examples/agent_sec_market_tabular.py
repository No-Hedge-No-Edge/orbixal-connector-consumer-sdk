"""SEC, market, and tabular examples using typed Consumer SDK actions."""

from __future__ import annotations

from connector_consumer_sdk import (
    ConnectorClient,
    ConnectorExecutionContext,
    MarketIntelGetQuote,
    SECGetCompanyFacts,
    SECSearchCompanies,
    TabularReadRows,
)


def load_company_and_quote() -> dict[str, object]:
    context = ConnectorExecutionContext(
        pipeline_id="pipe_research",
        agent_node_id="node_company_brief",
        request_id="req_company_brief_123",
    )
    with ConnectorClient(
        runtime_url="http://runtime-service:8002",
        execution_context=context,
    ) as client:
        sec = client.input("sec")
        market = client.input("market_intel")

        company = sec.query_action(SECSearchCompanies("Apple")).require_first()
        facts = sec.read_action(SECGetCompanyFacts(cik=str(company["id"]))).require_first()
        quote = market.read_action(MarketIntelGetQuote("AAPL")).require_first()

    return {
        "company": company,
        "facts": facts,
        "quote": quote,
    }


def load_rows() -> list[dict[str, object]]:
    context = ConnectorExecutionContext(
        pipeline_id="pipe_research",
        agent_node_id="node_tabular",
    )
    with ConnectorClient(
        runtime_url="http://runtime-service:8002",
        execution_context=context,
    ) as client:
        rows = client.input("market_data").read_action(TabularReadRows("prices", limit=50))
        return rows.values()
