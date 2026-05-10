"""Typed consumer SDK exceptions."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ConnectorErrorCategory(StrEnum):
    """Stable, agent-facing error categories."""

    AUTH = "auth"
    CREDENTIAL = "credential"
    POLICY = "policy"
    PROVIDER = "provider"
    PACKAGE = "package"
    QUOTA = "quota"
    RATE_LIMIT = "rate_limit"
    RESULT = "result"
    RUNTIME = "runtime"
    TIMEOUT = "timeout"
    TRANSPORT = "transport"
    VALIDATION = "validation"


class RetryRecommendation(StrEnum):
    """Stable retry guidance for agent orchestration."""

    DO_NOT_RETRY = "do_not_retry"
    RETRY = "retry"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    REFRESH_AUTH = "refresh_auth"


class ConnectorClientError(Exception):
    """Base exception for consumer SDK failures."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        request_id: str | None = None,
        retryable: bool = False,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        category: ConnectorErrorCategory | str | None = None,
        retry_recommendation: RetryRecommendation | str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.request_id = request_id
        self.retryable = retryable
        self.status_code = status_code
        self.details = details or {}
        self.category = (
            ConnectorErrorCategory(category)
            if category is not None
            else category_for_error_code(code)
        )
        self.retry_recommendation = (
            RetryRecommendation(retry_recommendation)
            if retry_recommendation is not None
            else retry_recommendation_for_error_code(code=code, retryable=retryable)
        )

    @property
    def retry_after_seconds(self) -> float | None:
        """Return provider/runtime retry-after guidance when present."""

        value = self.details.get("retry_after_seconds") or self.details.get("retry_after")
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None


class BindingNotFoundError(ConnectorClientError):
    """Raised when a bound connector input cannot be resolved."""


class ConnectorNotAvailableError(ConnectorClientError):
    """Raised when a connector target exists but cannot be used."""


class InvalidRuntimeRequestError(ConnectorClientError):
    """Raised when the request sent to runtime violates a runtime invariant."""


class AuthExpiredError(ConnectorClientError):
    """Raised when connector credentials have expired."""


class AuthInvalidError(ConnectorClientError):
    """Raised when connector credentials are rejected."""


class CredentialResolutionError(ConnectorClientError):
    """Raised when runtime cannot resolve connector credentials safely."""


class ProviderTimeoutError(ConnectorClientError):
    """Raised when an upstream provider request times out."""


class ProviderUnavailableError(ConnectorClientError):
    """Raised when an upstream provider is unavailable."""


class ProviderRateLimitedError(ConnectorClientError):
    """Raised when an upstream provider rate limit is hit."""


class ExecutionQuotaExceededError(ConnectorClientError):
    """Raised when Orbixal runtime quota policy blocks an execution."""


class OperationNotSupportedError(ConnectorClientError):
    """Raised when a connector action is unsupported."""


class PayloadTooLargeError(ConnectorClientError):
    """Raised when a request or response payload exceeds allowed size."""


class ResultNormalizationError(ConnectorClientError):
    """Raised when runtime cannot normalize a provider result safely."""


class RuntimeExecutionError(ConnectorClientError):
    """Raised for runtime failures that do not map to a narrower SDK exception."""


class OAuthAuthorizationError(ConnectorClientError):
    """Raised when backend-owned OAuth authorization flow calls fail."""


def category_for_error_code(code: str) -> ConnectorErrorCategory:
    """Map canonical runtime error codes to stable SDK categories."""

    if code in {"auth_expired", "credential_expired", "auth_invalid"}:
        return ConnectorErrorCategory.AUTH
    if code == "credential_resolution_failed":
        return ConnectorErrorCategory.CREDENTIAL
    if code == "execution_quota_exceeded":
        return ConnectorErrorCategory.QUOTA
    if code == "provider_rate_limited":
        return ConnectorErrorCategory.RATE_LIMIT
    if code == "provider_timeout":
        return ConnectorErrorCategory.TIMEOUT
    if code == "provider_unavailable":
        return ConnectorErrorCategory.PROVIDER
    if code in {
        "connector_package_unavailable",
        "connector_package_integrity_failed",
        "connector_package_manifest_mismatch",
        "connector_runtime_incompatible",
        "connector_package_load_failed",
    }:
        return ConnectorErrorCategory.PACKAGE
    if code == "connector_execution_timeout":
        return ConnectorErrorCategory.TIMEOUT
    if code == "connector_response_too_large":
        return ConnectorErrorCategory.RESULT
    if code in {
        "instance_not_executable",
        "connector_version_not_usable",
        "operation_not_supported",
        "runner_policy_violation",
    }:
        return ConnectorErrorCategory.POLICY
    if code in {"payload_too_large", "normalization_failed", "invalid_result_payload"}:
        return ConnectorErrorCategory.RESULT
    if code in {"invalid_request", "misconfiguration", "resource_not_found"}:
        return ConnectorErrorCategory.VALIDATION
    if code == "runtime_transport_error":
        return ConnectorErrorCategory.TRANSPORT
    return ConnectorErrorCategory.RUNTIME


def retry_recommendation_for_error_code(
    *,
    code: str,
    retryable: bool,
) -> RetryRecommendation:
    """Return stable retry guidance for orchestration code."""

    if code in {"auth_expired", "credential_expired", "auth_invalid"}:
        return RetryRecommendation.REFRESH_AUTH
    if code in {"provider_rate_limited", "execution_quota_exceeded"}:
        return RetryRecommendation.RETRY_WITH_BACKOFF
    if retryable:
        return RetryRecommendation.RETRY
    return RetryRecommendation.DO_NOT_RETRY
