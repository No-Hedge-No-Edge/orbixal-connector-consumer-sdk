"""Typed consumer SDK exceptions."""

from __future__ import annotations

from typing import Any


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
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.request_id = request_id
        self.retryable = retryable
        self.status_code = status_code
        self.details = details or {}


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


class OperationNotSupportedError(ConnectorClientError):
    """Raised when a connector action is unsupported."""


class PayloadTooLargeError(ConnectorClientError):
    """Raised when a request or response payload exceeds allowed size."""


class ResultNormalizationError(ConnectorClientError):
    """Raised when runtime cannot normalize a provider result safely."""


class RuntimeExecutionError(ConnectorClientError):
    """Raised for runtime failures that do not map to a narrower SDK exception."""
