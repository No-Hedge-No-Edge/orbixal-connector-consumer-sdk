# Connector Consumer SDK

Internal-first SDK for agents and internal callers consuming bound connector inputs through the runtime service.

This package is structured so it can be copied into a standalone repository root and published independently.

## Import Surface

The primary public API includes:

- `AsyncConnectorClient`
- `AsyncConnectorAuthorizationClient`
- `ConnectorClient`
- `ConnectorAuthorizationClient`
- `ConnectorExecutionContext`
- typed runtime-mapped SDK exceptions
- normalized `RecordsResult` and `TabularResult`
- schema-derived contract models in `connector_consumer_sdk.generated` and `connector_consumer_sdk.models`

## Quick Start

Bound access is the default path for agents:

```python
from connector_consumer_sdk import ConnectorClient, ConnectorExecutionContext, GitHubSearchIssues

client = ConnectorClient(
    runtime_url="http://runtime-service:8002",
    execution_context=ConnectorExecutionContext(
        pipeline_id="pipe_1",
        agent_node_id="node_1",
        request_id="req_123",
    ),
)

with client:
    issues = client.input("issue_source")
    result = issues.query_action(GitHubSearchIssues("label:bug"))
    first_issue = result.first()
```

Direct instance access remains available as a lower-level escape hatch:

```python
from connector_consumer_sdk import ConnectorClient

with ConnectorClient(runtime_url="http://runtime-service:8002") as client:
    result = client.read(
        connector_instance_id="conninst_123",
        action="get_issue",
        params={"repo": "orbixal/platform", "issue_number": 15},
    )
```

Async access is also available for async agent/runtime code:

```python
from connector_consumer_sdk import AsyncConnectorClient, ConnectorExecutionContext

async with AsyncConnectorClient(
    runtime_url="http://runtime-service:8002",
    execution_context=ConnectorExecutionContext(
        pipeline_id="pipe_1",
        agent_node_id="node_1",
    ),
) as client:
    result = await client.query_from_input(
        input_name="issue_source",
        action="search_issues",
        params={"query": "label:bug"},
    )
```

OAuth authorization is backend-owned. The consumer SDK can initiate the backend flow for an
existing connector instance and return the provider redirect URL, but it does not hold OAuth app
credentials, exchange authorization codes, or store tokens:

```python
from connector_consumer_sdk import ConnectorAuthorizationClient

with ConnectorAuthorizationClient(
    control_plane_url="http://control-plane:8000",
    credential_service_url="http://credential-service:8001",
) as client:
    session = client.start_authorization(
        connector_instance_id="conninst_123",
        requested_scopes=["repo", "read:user"],
        return_url="https://app.example.com/connectors/github",
    )

    redirect_user_to = session.authorization_url
```

After the provider redirects to the backend callback URL, callers can poll sanitized session
status:

```python
status = client.get_authorization_session(session.oauth_session_id)
```

## Supported Flows

The current SDK supports:

- backend-owned OAuth authorization initiation and session status lookup
- async `describe_input`, `list_resources_from_input`, `read_from_input`, `query_from_input`
- async direct `describe`, `list_resources`, `read`, and `query`
- async `iter_query_from_input` and `iter_query`
- `describe_input`
- `list_resources_from_input`
- `read_from_input`
- `query_from_input`
- `iter_query_from_input`
- direct `describe`, `list_resources`, `read`, and `query`

## Result Shapes

`read` and `query` return ergonomic result objects:

- `RecordsResult`
- `TabularResult`

Convenience helpers expose stable metadata and common result accessors:

```python
if result.has_more:
    next_cursor = result.cursor

request_id = result.request_id
connector_key = result.connector_key

if isinstance(result, RecordsResult):
    first_record = result.require_first()
    text_blocks = result.content_texts()

if isinstance(result, TabularResult):
    columns = result.column_names
    first_row_values = result.require_first_row()
```

The package also preserves schema-derived wire models under:

- `connector_consumer_sdk.generated`
- `connector_consumer_sdk.models`

## Error Taxonomy

All SDK exceptions expose stable fields for agent orchestration:

- `code`: canonical runtime/provider code
- `category`: one of the `ConnectorErrorCategory` values
- `retryable`: runtime retryability flag
- `retry_recommendation`: one of `RetryRecommendation`
- `retry_after_seconds`: parsed backoff hint when present

Examples:

- `ExecutionQuotaExceededError` maps to category `quota` and recommendation `retry_with_backoff`.
- `ProviderUnavailableError` maps to category `provider`.
- `AuthExpiredError` maps to category `auth` and recommendation `refresh_auth`.

## Safe Retries

Retries are opt-in and limited to safe read-style operations by default:

```python
from connector_consumer_sdk import ConnectorClient, RetryPolicy

client = ConnectorClient(
    runtime_url="http://runtime-service:8002",
    retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.2),
)
```

The SDK does not retry `test_connection`, auth refresh cases, or non-retryable runtime errors.

## Typed Actions

The SDK includes typed wrappers for common first-party actions, including GitHub, SEC, market
intelligence, and tabular reads:

```python
from connector_consumer_sdk import MarketIntelGetQuote, SECSearchCompanies

company = client.input("sec").query_action(SECSearchCompanies("Apple")).require_first()
quote = client.input("market_intel").read_action(MarketIntelGetQuote("AAPL")).require_first()
```

## Testing

The client accepts an injected transport for tests and internal harnesses.

Example with a custom transport:

```python
from connector_consumer_sdk import ConnectorClient


class FakeTransport:
    def execute(self, payload: dict) -> dict:
        return {
            "kind": "records",
            "records": [{"id": "1", "type": "issue"}],
            "cursor": None,
            "meta": {
                "connector_key": "github",
                "connector_version": "1.0.0",
                "action": "search_issues",
                "request_id": "req_test",
            },
        }

    def close(self) -> None:
        pass


with ConnectorClient(transport=FakeTransport()) as client:
    result = client.query("conninst_123", "search_issues", {"query": "bug"})
```

## Development

Common package-local commands:

- `uv sync --group dev`
- `uv run pytest`
- `uv build`
- `uv run python scripts/sync_contract_models.py --check`
- `uv run python scripts/generate_action_wrappers.py --manifest-root /Users/tgall/orbixal-first-party-connectors/dist`

Release/versioning policy lives in `docs/RELEASE_AND_COMPATIBILITY.md`.

## Remaining Work

The SDK is still internal-first and scaffold-stage in a few areas:

- no async transport other than HTTP/custom injected transport
- no publishing/release workflow yet

## Contract Source Of Truth

The generated modules under `src/connector_consumer_sdk/generated/` are vendored into this package. The canonical shared contract schemas still live in the Orbixal platform monorepo and should remain schema-first.

Until schema sync is automated, update generated files in this package by syncing from the platform repo rather than editing them by hand.

Generated files under `src/connector_consumer_sdk/generated/` must be regenerated from `schemas/`, not hand-edited.
