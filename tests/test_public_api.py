from __future__ import annotations

import tomllib
from pathlib import Path

import connector_consumer_sdk


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_top_level_exports_include_client_surface() -> None:
    expected_exports = {
        "AsyncConnectorAuthorizationClient",
        "AsyncBoundConnector",
        "AsyncConnectorClient",
        "BoundConnector",
        "ConnectorAuthorizationClient",
        "ConnectorAction",
        "ConnectorClient",
        "ConnectorErrorCategory",
        "ConnectorExecutionContext",
        "ConnectorClientError",
        "BindingNotFoundError",
        "ConnectorNotAvailableError",
        "InvalidRuntimeRequestError",
        "CredentialResolutionError",
        "ExecutionQuotaExceededError",
        "GitHubGetIssue",
        "GitHubSearchIssues",
        "OAuthAuthorizationError",
        "MarketIntelCompanyNews",
        "MarketIntelGetQuote",
        "OAuthAuthorizationSession",
        "OAuthAuthorizationSessionStatus",
        "ProviderUnavailableError",
        "RetryRecommendation",
        "RetryPolicy",
        "ResultNormalizationError",
        "SECGetCompanyFacts",
        "SECSearchCompanies",
        "TabularReadRows",
        "RecordsResult",
        "TabularResult",
        "ConnectorDescription",
        "ResourcePage",
    }

    assert expected_exports.issubset(set(connector_consumer_sdk.__all__))


def test_package_pyproject_declares_typed_http_client_dependency() -> None:
    pyproject_data = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text())

    project = pyproject_data["project"]
    assert project["name"] == "orbixal-connector-consumer-sdk"
    assert "httpx>=0.28,<1.0" in project["dependencies"]
    assert "Typing :: Typed" in project["classifiers"]
    assert "pytest>=9.0.3" in pyproject_data["dependency-groups"]["dev"]
    assert (PACKAGE_ROOT / "src" / "connector_consumer_sdk" / "py.typed").exists()
    assert (PACKAGE_ROOT / "scripts" / "sync_contract_models.py").exists()
    assert (PACKAGE_ROOT / "scripts" / "generate_action_wrappers.py").exists()
    assert (PACKAGE_ROOT / "docs" / "RELEASE_AND_COMPATIBILITY.md").exists()
    assert (PACKAGE_ROOT / "src" / "connector_consumer_sdk" / "first_party_actions.py").exists()


def test_generated_first_party_actions_use_dedicated_module() -> None:
    from connector_consumer_sdk.first_party_actions import GithubSearchIssues

    action = GithubSearchIssues(query="repo:orbixal/data is:open")

    assert action.operation == "query"
    assert action.name == "search_issues"
    assert action.params() == {"query": "repo:orbixal/data is:open"}
    assert "GithubSearchIssues" not in connector_consumer_sdk.__all__
