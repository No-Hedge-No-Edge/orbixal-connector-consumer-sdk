"""Pagination helpers for cursor-based connector queries."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import TypeVar

from connector_consumer_sdk.results import ConnectorResult


TResult = TypeVar("TResult", bound=ConnectorResult)


def iter_cursor_pages(fetch_page: Callable[[str | None], TResult]) -> Iterator[TResult]:
    """Yield cursor-linked result pages until the runtime stops returning a cursor."""

    cursor: str | None = None
    while True:
        page = fetch_page(cursor)
        yield page
        if page.cursor is None:
            break
        cursor = page.cursor


async def aiter_cursor_pages(
    fetch_page: Callable[[str | None], Awaitable[TResult]]
) -> AsyncIterator[TResult]:
    """Yield cursor-linked result pages asynchronously until no cursor remains."""

    cursor: str | None = None
    while True:
        page = await fetch_page(cursor)
        yield page
        if page.cursor is None:
            break
        cursor = page.cursor
