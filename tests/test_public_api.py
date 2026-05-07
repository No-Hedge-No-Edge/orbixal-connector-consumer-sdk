from __future__ import annotations

import tomllib
from pathlib import Path

import connector_consumer_sdk


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_top_level_exports_include_client_surface() -> None:
    expected_exports = {
        "AsyncConnectorAuthorizationClient",
        "AsyncConnectorClient",
        "ConnectorAuthorizationClient",
        "ConnectorClient",
        "ConnectorExecutionContext",
        "ConnectorClientError",
        "BindingNotFoundError",
        "ConnectorNotAvailableError",
        "InvalidRuntimeRequestError",
        "CredentialResolutionError",
        "OAuthAuthorizationError",
        "OAuthAuthorizationSession",
        "OAuthAuthorizationSessionStatus",
        "ProviderUnavailableError",
        "ResultNormalizationError",
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
