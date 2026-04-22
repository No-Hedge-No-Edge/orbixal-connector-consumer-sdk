"""Public-facing connector consumer SDK package."""

from connector_consumer_sdk.client import AsyncConnectorClient, ConnectorClient
from connector_consumer_sdk.context import ConnectorExecutionContext
from connector_consumer_sdk.exceptions import (
    AuthExpiredError,
    AuthInvalidError,
    BindingNotFoundError,
    ConnectorClientError,
    ConnectorNotAvailableError,
    CredentialResolutionError,
    InvalidRuntimeRequestError,
    OperationNotSupportedError,
    PayloadTooLargeError,
    ProviderRateLimitedError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResultNormalizationError,
    RuntimeExecutionError,
)
from connector_consumer_sdk.generated.discovery_models import (
    ConnectorDescription,
    OperationDescriptor,
    ResourceItem,
    ResourcePage,
)
from connector_consumer_sdk.generated.error_models import ErrorEnvelope, ErrorPayload
from connector_consumer_sdk.generated.result_models import (
    ColumnDef,
    RecordItem,
    RecordsEnvelope,
    RecordsMeta,
    RowItem,
    TabularEnvelope,
    TabularMeta,
)
from connector_consumer_sdk.generated.runtime_models import (
    BOUND_EXECUTION_KEYS,
    DIRECT_EXECUTION_KEYS,
    ExecutionContext,
    RuntimeExecuteRequest,
    RuntimeInput,
    RuntimeOperation,
)
from connector_consumer_sdk.generated.state_models import (
    CredentialState,
    HealthStatus,
    InstanceStatus,
)
from connector_consumer_sdk.results import ConnectorResult, RecordsResult, TabularResult

__all__ = [
    "BOUND_EXECUTION_KEYS",
    "ColumnDef",
    "AsyncConnectorClient",
    "AuthExpiredError",
    "AuthInvalidError",
    "BindingNotFoundError",
    "ConnectorClient",
    "ConnectorClientError",
    "ConnectorDescription",
    "ConnectorExecutionContext",
    "ConnectorNotAvailableError",
    "ConnectorResult",
    "CredentialResolutionError",
    "CredentialState",
    "DIRECT_EXECUTION_KEYS",
    "ErrorEnvelope",
    "ErrorPayload",
    "ExecutionContext",
    "HealthStatus",
    "InstanceStatus",
    "InvalidRuntimeRequestError",
    "OperationNotSupportedError",
    "OperationDescriptor",
    "PayloadTooLargeError",
    "ProviderRateLimitedError",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "RecordItem",
    "RecordsResult",
    "RecordsEnvelope",
    "RecordsMeta",
    "ResourceItem",
    "ResourcePage",
    "ResultNormalizationError",
    "RuntimeExecutionError",
    "RowItem",
    "RuntimeExecuteRequest",
    "RuntimeInput",
    "RuntimeOperation",
    "TabularResult",
    "TabularEnvelope",
    "TabularMeta",
]
