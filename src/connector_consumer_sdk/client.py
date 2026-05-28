"""Primary client surfaces for the consumer SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
import asyncio
import time
from typing import Any, cast

from connector_consumer_sdk.actions import ConnectorAction
from connector_consumer_sdk.context import ConnectorExecutionContext
from connector_consumer_sdk.exceptions import (
    AuthExpiredError,
    AuthInvalidError,
    BindingNotFoundError,
    ConnectorClientError,
    ConnectorNotAvailableError,
    CredentialResolutionError,
    ExecutionQuotaExceededError,
    InvalidRuntimeRequestError,
    OperationNotSupportedError,
    PayloadTooLargeError,
    ProviderRateLimitedError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResultNormalizationError,
    RuntimeExecutionError,
)
from connector_consumer_sdk.generated.discovery_models import ConnectorDescription, ResourcePage
from connector_consumer_sdk.generated.error_models import ErrorEnvelope
from connector_consumer_sdk.generated.result_models import ColumnDef, RecordItem, RowItem
from connector_consumer_sdk.pagination import aiter_cursor_pages, iter_cursor_pages
from connector_consumer_sdk.retry import RetryPolicy
from connector_consumer_sdk.results import ConnectorResult, RecordsResult, TabularResult
from connector_consumer_sdk.transport import (
    AsyncConnectorTransport,
    ConnectorTransport,
    HTTPAsyncConnectorTransport,
    HTTPConnectorTransport,
    HTTPTransportResponseError,
    HTTPTransportUnavailableError,
)


class _ConnectorClientBase:
    """Shared payload, parsing, and error-mapping logic for connector clients."""

    def __init__(self, *, execution_context: ConnectorExecutionContext | None = None) -> None:
        self.execution_context = (
            ConnectorExecutionContext.from_environment()
            if execution_context is None
            else execution_context.with_environment_defaults()
        )

    def _build_bound_payload(
        self,
        *,
        input_name: str,
        operation: str,
        runtime_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self.execution_context is None:
            raise ValueError(
                "Bound connector access requires a ConnectorExecutionContext with pipeline_id and agent_node_id."
            )

        payload: dict[str, Any] = {
            "pipeline_id": self.execution_context.pipeline_id,
            "agent_node_id": self.execution_context.agent_node_id,
            "input_name": input_name,
            "operation": operation,
        }
        if runtime_input is not None:
            payload["input"] = runtime_input
        execution_context = self.execution_context.as_runtime_execution_context()
        if execution_context:
            payload["execution_context"] = execution_context
        approval_context = self.execution_context.as_approval_context()
        if approval_context:
            payload["approval_context"] = approval_context
        return payload

    def _build_direct_payload(
        self,
        *,
        connector_instance_id: str,
        operation: str,
        runtime_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "connector_instance_id": connector_instance_id,
            "operation": operation,
        }
        if runtime_input is not None:
            payload["input"] = runtime_input
        execution_context = self._execution_context_payload()
        if execution_context:
            payload["execution_context"] = execution_context
        approval_context = self._approval_context_payload()
        if approval_context:
            payload["approval_context"] = approval_context
        return payload

    def _execution_context_payload(self) -> dict[str, Any] | None:
        if self.execution_context is None:
            return None
        return self.execution_context.as_runtime_execution_context()

    def _approval_context_payload(self) -> dict[str, Any] | None:
        if self.execution_context is None:
            return None
        return self.execution_context.as_approval_context()

    @staticmethod
    def _build_action_input(
        *,
        action: str,
        params: dict[str, object],
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "action": action,
            "params": params,
            "include_raw": include_raw,
        }
        if cursor is not None:
            payload["cursor"] = cursor
        return payload

    @staticmethod
    def _build_list_resources_input(
        *,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any] | None:
        payload: dict[str, Any] = {}
        if query is not None:
            payload["query"] = query
        if cursor is not None:
            payload["cursor"] = cursor
        return payload or None

    @staticmethod
    def _map_response_error(
        exc: HTTPTransportResponseError,
        *,
        bound_request: bool,
    ) -> ConnectorClientError:
        payload = exc.payload
        if payload is None:
            return RuntimeExecutionError(
                "Runtime returned a non-JSON error response.",
                code="runtime_http_error",
                status_code=exc.status_code,
                details={"raw_text": exc.raw_text or ""},
            )

        envelope = cast(ErrorEnvelope, payload)
        error = envelope.get("error")
        if error is None:
            return RuntimeExecutionError(
                "Runtime returned an invalid error payload.",
                code="runtime_http_error",
                status_code=exc.status_code,
                details={"payload": payload},
            )

        code = error["code"]
        message = error["message"]
        request_id = error["request_id"]
        retryable = error["retryable"]
        details = error["details"]
        exception_type = _ConnectorClientBase._exception_type_for_code(
            code=code,
            bound_request=bound_request,
        )
        return exception_type(
            message,
            code=code,
            request_id=request_id,
            retryable=retryable,
            status_code=exc.status_code,
            details=details,
        )

    @staticmethod
    def _exception_type_for_code(
        *,
        code: str,
        bound_request: bool,
    ) -> type[ConnectorClientError]:
        if code == "instance_not_found":
            return BindingNotFoundError if bound_request else ConnectorNotAvailableError

        mapping: dict[str, type[ConnectorClientError]] = {
            "invalid_request": InvalidRuntimeRequestError,
            "instance_not_executable": ConnectorNotAvailableError,
            "connector_version_not_usable": ConnectorNotAvailableError,
            "execution_quota_exceeded": ExecutionQuotaExceededError,
            "provider_unavailable": ProviderUnavailableError,
            "credential_resolution_failed": CredentialResolutionError,
            "credential_expired": AuthExpiredError,
            "auth_expired": AuthExpiredError,
            "auth_invalid": AuthInvalidError,
            "provider_timeout": ProviderTimeoutError,
            "provider_rate_limited": ProviderRateLimitedError,
            "operation_not_supported": OperationNotSupportedError,
            "payload_too_large": PayloadTooLargeError,
            "connector_response_too_large": PayloadTooLargeError,
            "normalization_failed": ResultNormalizationError,
        }
        return mapping.get(code, RuntimeExecutionError)

    @staticmethod
    def _map_transport_unavailable(exc: HTTPTransportUnavailableError) -> RuntimeExecutionError:
        return RuntimeExecutionError(
            exc.message,
            code="runtime_transport_error",
            retryable=True,
        )

    @staticmethod
    def _should_retry_error(
        *,
        error: ConnectorClientError,
        operation: str | None,
        retry_policy: RetryPolicy,
        attempt: int,
    ) -> bool:
        return (
            attempt < retry_policy.max_attempts
            and retry_policy.allows_operation(operation)
            and error.retryable
            and error.retry_recommendation != "refresh_auth"
        )

    @staticmethod
    def _parse_result(payload: dict[str, Any]) -> ConnectorResult:
        kind = payload.get("kind")
        if kind == "records":
            return RecordsResult(
                kind="records",
                records=cast(list[RecordItem], payload.get("records", [])),
                cursor=cast(str | None, payload.get("cursor")),
                meta=cast(dict[str, Any], payload.get("meta", {})),
                raw=cast(dict[str, Any] | None, payload.get("raw")),
            )
        if kind == "tabular":
            return TabularResult(
                kind="tabular",
                columns=cast(list[ColumnDef], payload.get("columns", [])),
                rows=cast(list[RowItem], payload.get("rows", [])),
                cursor=cast(str | None, payload.get("cursor")),
                meta=cast(dict[str, Any], payload.get("meta", {})),
                raw=cast(dict[str, Any] | None, payload.get("raw")),
            )
        raise RuntimeExecutionError(
            "Runtime returned an unsupported result payload.",
            code="invalid_result_payload",
            details={"payload": payload},
        )


class ConnectorClient(_ConnectorClientBase):
    """Sync client for canonical runtime connector operations."""

    def __init__(
        self,
        *,
        runtime_url: str | None = None,
        auth_token: str | None = None,
        execution_context: ConnectorExecutionContext | None = None,
        timeout_seconds: float = 15.0,
        endpoint_path: str = "/api/v1/runtime/execute",
        transport: ConnectorTransport | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        if transport is None and runtime_url is None:
            raise ValueError("Provide either runtime_url or a custom transport.")

        super().__init__(execution_context=execution_context)
        self.transport = transport or HTTPConnectorTransport(
            runtime_url=runtime_url,
            auth_token=auth_token,
            timeout_seconds=timeout_seconds,
            endpoint_path=endpoint_path,
        )
        self.retry_policy = retry_policy or RetryPolicy.disabled()

    def close(self) -> None:
        self.transport.close()

    def input(self, input_name: str) -> BoundConnector:
        """Return an alias-first bound connector helper for agent code."""

        return BoundConnector(client=self, input_name=input_name)

    def alias(self, input_name: str) -> BoundConnector:
        """Alias for :meth:`input` for call sites that use connector aliases."""

        return self.input(input_name)

    def __enter__(self) -> "ConnectorClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def describe_input(self, input_name: str) -> ConnectorDescription:
        return cast(
            ConnectorDescription,
            self._send(
                payload=self._build_bound_payload(input_name=input_name, operation="describe"),
                bound_request=True,
            ),
        )

    def list_resources_from_input(
        self,
        input_name: str,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return cast(
            ResourcePage,
            self._send(
                payload=self._build_bound_payload(
                    input_name=input_name,
                    operation="list_resources",
                    runtime_input=self._build_list_resources_input(query=query, cursor=cursor),
                ),
                bound_request=True,
            ),
        )

    def read_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self._execute_result(
            payload=self._build_bound_payload(
                input_name=input_name,
                operation="read",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    include_raw=include_raw,
                ),
            ),
            bound_request=True,
        )

    def query_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self._execute_result(
            payload=self._build_bound_payload(
                input_name=input_name,
                operation="query",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    cursor=cursor,
                    include_raw=include_raw,
                ),
            ),
            bound_request=True,
        )

    def iter_query_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> Iterator[ConnectorResult]:
        return iter_cursor_pages(
            lambda cursor: self.query_from_input(
                input_name=input_name,
                action=action,
                params=params,
                cursor=cursor,
                include_raw=include_raw,
            )
        )

    def describe(self, connector_instance_id: str) -> ConnectorDescription:
        return cast(
            ConnectorDescription,
            self._send(
                payload=self._build_direct_payload(
                    connector_instance_id=connector_instance_id,
                    operation="describe",
                ),
                bound_request=False,
            ),
        )

    def list_resources(
        self,
        connector_instance_id: str,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return cast(
            ResourcePage,
            self._send(
                payload=self._build_direct_payload(
                    connector_instance_id=connector_instance_id,
                    operation="list_resources",
                    runtime_input=self._build_list_resources_input(query=query, cursor=cursor),
                ),
                bound_request=False,
            ),
        )

    def read(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self._execute_result(
            payload=self._build_direct_payload(
                connector_instance_id=connector_instance_id,
                operation="read",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    include_raw=include_raw,
                ),
            ),
            bound_request=False,
        )

    def query(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self._execute_result(
            payload=self._build_direct_payload(
                connector_instance_id=connector_instance_id,
                operation="query",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    cursor=cursor,
                    include_raw=include_raw,
                ),
            ),
            bound_request=False,
        )

    def iter_query(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> Iterator[ConnectorResult]:
        return iter_cursor_pages(
            lambda cursor: self.query(
                connector_instance_id=connector_instance_id,
                action=action,
                params=params,
                cursor=cursor,
                include_raw=include_raw,
            )
        )

    def _execute_result(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> ConnectorResult:
        return self._parse_result(self._send(payload=payload, bound_request=bound_request))

    def _send(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> dict[str, Any]:
        operation = cast(str | None, payload.get("operation"))
        attempt = 1
        while True:
            try:
                return self._send_once(payload=payload, bound_request=bound_request)
            except ConnectorClientError as exc:
                if not self._should_retry_error(
                    error=exc,
                    operation=operation,
                    retry_policy=self.retry_policy,
                    attempt=attempt,
                ):
                    raise
                delay = self.retry_policy.delay_for_attempt(
                    retry_index=attempt,
                    retry_after_seconds=exc.retry_after_seconds,
                )
                if delay > 0:
                    time.sleep(delay)
                attempt += 1

    def _send_once(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> dict[str, Any]:
        try:
            return self.transport.execute(payload)
        except HTTPTransportResponseError as exc:
            raise self._map_response_error(exc, bound_request=bound_request) from exc
        except HTTPTransportUnavailableError as exc:
            raise self._map_transport_unavailable(exc) from exc


class BoundConnector:
    """Alias-first sync helper for one bound connector input."""

    def __init__(self, *, client: ConnectorClient, input_name: str) -> None:
        self.client = client
        self.input_name = input_name

    def describe(self) -> ConnectorDescription:
        return self.client.describe_input(self.input_name)

    def list_resources(
        self,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return self.client.list_resources_from_input(
            self.input_name,
            query=query,
            cursor=cursor,
        )

    def read(
        self,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self.client.read_from_input(
            self.input_name,
            action=action,
            params=params,
            include_raw=include_raw,
        )

    def query(
        self,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return self.client.query_from_input(
            self.input_name,
            action=action,
            params=params,
            cursor=cursor,
            include_raw=include_raw,
        )

    def read_action(
        self,
        action: ConnectorAction,
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        if action.operation != "read":
            raise ValueError("read_action requires an action with operation='read'.")
        return self.read(action.name, action.params(), include_raw=include_raw)

    def query_action(
        self,
        action: ConnectorAction,
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        if action.operation != "query":
            raise ValueError("query_action requires an action with operation='query'.")
        return self.query(
            action.name,
            action.params(),
            cursor=cursor,
            include_raw=include_raw,
        )

    def iter_query(
        self,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> Iterator[ConnectorResult]:
        return self.client.iter_query_from_input(
            self.input_name,
            action=action,
            params=params,
            include_raw=include_raw,
        )


class AsyncConnectorClient(_ConnectorClientBase):
    """Async client for canonical runtime connector operations."""

    def __init__(
        self,
        *,
        runtime_url: str | None = None,
        auth_token: str | None = None,
        execution_context: ConnectorExecutionContext | None = None,
        timeout_seconds: float = 15.0,
        endpoint_path: str = "/api/v1/runtime/execute",
        transport: AsyncConnectorTransport | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        if transport is None and runtime_url is None:
            raise ValueError("Provide either runtime_url or a custom transport.")

        super().__init__(execution_context=execution_context)
        self.transport = transport or HTTPAsyncConnectorTransport(
            runtime_url=runtime_url,
            auth_token=auth_token,
            timeout_seconds=timeout_seconds,
            endpoint_path=endpoint_path,
        )
        self.retry_policy = retry_policy or RetryPolicy.disabled()

    async def aclose(self) -> None:
        await self.transport.aclose()

    def input(self, input_name: str) -> AsyncBoundConnector:
        """Return an alias-first bound connector helper for async agent code."""

        return AsyncBoundConnector(client=self, input_name=input_name)

    def alias(self, input_name: str) -> AsyncBoundConnector:
        """Alias for :meth:`input` for call sites that use connector aliases."""

        return self.input(input_name)

    async def __aenter__(self) -> "AsyncConnectorClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def describe_input(self, input_name: str) -> ConnectorDescription:
        return cast(
            ConnectorDescription,
            await self._send(
                payload=self._build_bound_payload(input_name=input_name, operation="describe"),
                bound_request=True,
            ),
        )

    async def list_resources_from_input(
        self,
        input_name: str,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return cast(
            ResourcePage,
            await self._send(
                payload=self._build_bound_payload(
                    input_name=input_name,
                    operation="list_resources",
                    runtime_input=self._build_list_resources_input(query=query, cursor=cursor),
                ),
                bound_request=True,
            ),
        )

    async def read_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self._execute_result(
            payload=self._build_bound_payload(
                input_name=input_name,
                operation="read",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    include_raw=include_raw,
                ),
            ),
            bound_request=True,
        )

    async def query_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self._execute_result(
            payload=self._build_bound_payload(
                input_name=input_name,
                operation="query",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    cursor=cursor,
                    include_raw=include_raw,
                ),
            ),
            bound_request=True,
        )

    def iter_query_from_input(
        self,
        input_name: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> AsyncIterator[ConnectorResult]:
        return aiter_cursor_pages(
            lambda cursor: self.query_from_input(
                input_name=input_name,
                action=action,
                params=params,
                cursor=cursor,
                include_raw=include_raw,
            )
        )

    async def describe(self, connector_instance_id: str) -> ConnectorDescription:
        return cast(
            ConnectorDescription,
            await self._send(
                payload=self._build_direct_payload(
                    connector_instance_id=connector_instance_id,
                    operation="describe",
                ),
                bound_request=False,
            ),
        )

    async def list_resources(
        self,
        connector_instance_id: str,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return cast(
            ResourcePage,
            await self._send(
                payload=self._build_direct_payload(
                    connector_instance_id=connector_instance_id,
                    operation="list_resources",
                    runtime_input=self._build_list_resources_input(query=query, cursor=cursor),
                ),
                bound_request=False,
            ),
        )

    async def read(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self._execute_result(
            payload=self._build_direct_payload(
                connector_instance_id=connector_instance_id,
                operation="read",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    include_raw=include_raw,
                ),
            ),
            bound_request=False,
        )

    async def query(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self._execute_result(
            payload=self._build_direct_payload(
                connector_instance_id=connector_instance_id,
                operation="query",
                runtime_input=self._build_action_input(
                    action=action,
                    params=params,
                    cursor=cursor,
                    include_raw=include_raw,
                ),
            ),
            bound_request=False,
        )

    def iter_query(
        self,
        connector_instance_id: str,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> AsyncIterator[ConnectorResult]:
        return aiter_cursor_pages(
            lambda cursor: self.query(
                connector_instance_id=connector_instance_id,
                action=action,
                params=params,
                cursor=cursor,
                include_raw=include_raw,
            )
        )

    async def _execute_result(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> ConnectorResult:
        return self._parse_result(await self._send(payload=payload, bound_request=bound_request))

    async def _send(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> dict[str, Any]:
        operation = cast(str | None, payload.get("operation"))
        attempt = 1
        while True:
            try:
                return await self._send_once(payload=payload, bound_request=bound_request)
            except ConnectorClientError as exc:
                if not self._should_retry_error(
                    error=exc,
                    operation=operation,
                    retry_policy=self.retry_policy,
                    attempt=attempt,
                ):
                    raise
                delay = self.retry_policy.delay_for_attempt(
                    retry_index=attempt,
                    retry_after_seconds=exc.retry_after_seconds,
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                attempt += 1

    async def _send_once(
        self,
        *,
        payload: dict[str, Any],
        bound_request: bool,
    ) -> dict[str, Any]:
        try:
            return await self.transport.execute(payload)
        except HTTPTransportResponseError as exc:
            raise self._map_response_error(exc, bound_request=bound_request) from exc
        except HTTPTransportUnavailableError as exc:
            raise self._map_transport_unavailable(exc) from exc


class AsyncBoundConnector:
    """Alias-first async helper for one bound connector input."""

    def __init__(self, *, client: AsyncConnectorClient, input_name: str) -> None:
        self.client = client
        self.input_name = input_name

    async def describe(self) -> ConnectorDescription:
        return await self.client.describe_input(self.input_name)

    async def list_resources(
        self,
        query: dict[str, object] | None = None,
        cursor: str | None = None,
    ) -> ResourcePage:
        return await self.client.list_resources_from_input(
            self.input_name,
            query=query,
            cursor=cursor,
        )

    async def read(
        self,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self.client.read_from_input(
            self.input_name,
            action=action,
            params=params,
            include_raw=include_raw,
        )

    async def query(
        self,
        action: str,
        params: dict[str, object],
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        return await self.client.query_from_input(
            self.input_name,
            action=action,
            params=params,
            cursor=cursor,
            include_raw=include_raw,
        )

    async def read_action(
        self,
        action: ConnectorAction,
        *,
        include_raw: bool = False,
    ) -> ConnectorResult:
        if action.operation != "read":
            raise ValueError("read_action requires an action with operation='read'.")
        return await self.read(action.name, action.params(), include_raw=include_raw)

    async def query_action(
        self,
        action: ConnectorAction,
        *,
        cursor: str | None = None,
        include_raw: bool = False,
    ) -> ConnectorResult:
        if action.operation != "query":
            raise ValueError("query_action requires an action with operation='query'.")
        return await self.query(
            action.name,
            action.params(),
            cursor=cursor,
            include_raw=include_raw,
        )

    def iter_query(
        self,
        action: str,
        params: dict[str, object],
        *,
        include_raw: bool = False,
    ) -> AsyncIterator[ConnectorResult]:
        return self.client.iter_query_from_input(
            self.input_name,
            action=action,
            params=params,
            include_raw=include_raw,
        )
