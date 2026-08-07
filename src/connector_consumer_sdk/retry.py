"""Retry policy helpers for safe connector runtime calls."""

from __future__ import annotations

from dataclasses import dataclass


SAFE_RETRY_OPERATIONS = frozenset({"describe", "list_resources", "read", "query"})


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential-backoff retry policy.

    Retries are disabled by default. ``max_attempts`` includes the initial
    request, so ``max_attempts=1`` means no retry.
    """

    max_attempts: int = 1
    base_delay_seconds: float = 0.25
    multiplier: float = 2.0
    max_delay_seconds: float = 2.0
    retry_operations: frozenset[str] = SAFE_RETRY_OPERATIONS

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("RetryPolicy.max_attempts must be at least 1.")
        if self.base_delay_seconds < 0:
            raise ValueError("RetryPolicy.base_delay_seconds cannot be negative.")
        if self.multiplier < 1:
            raise ValueError("RetryPolicy.multiplier must be at least 1.")
        if self.max_delay_seconds < 0:
            raise ValueError("RetryPolicy.max_delay_seconds cannot be negative.")

    @classmethod
    def disabled(cls) -> "RetryPolicy":
        return cls(max_attempts=1)

    def allows_operation(self, operation: str | None) -> bool:
        return operation in self.retry_operations

    def delay_for_attempt(
        self,
        *,
        retry_index: int,
        retry_after_seconds: float | None = None,
    ) -> float:
        if retry_after_seconds is not None:
            return min(max(retry_after_seconds, 0.0), self.max_delay_seconds)
        delay = self.base_delay_seconds * (self.multiplier ** max(retry_index - 1, 0))
        return min(delay, self.max_delay_seconds)
