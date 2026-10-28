import json
from dataclasses import dataclass, fields
from typing import List, Optional, Union

from predictasearch.models import SearchResult
from predictasearch.sse import ServerSentEvent


@dataclass(frozen=True)
class ResultEvent:
    """A source found profiles."""

    id: int
    network: str
    data: List[SearchResult]


@dataclass(frozen=True)
class SourceErrorEvent:
    """A source could not answer, ``reason`` saying why (``timeout``...)."""

    id: int
    network: str
    reason: str


@dataclass(frozen=True)
class ProgressEvent:
    """Sent every few seconds while the search runs."""

    id: int
    done: int
    total: int
    found: int
    failed: int


@dataclass(frozen=True)
class DoneEvent:
    """The search is complete. Its credit is spent only if a source answered."""

    id: int
    found: int
    failed: int
    credit_debited: bool
    credit_balance: int


@dataclass(frozen=True)
class FailedEvent:
    """The search was interrupted on the API's side, and its credit refunded.

    ``reason`` is one of ``orphaned``, ``shutdown``, ``max_duration``,
    ``not_allowed`` or ``internal_error``.
    """

    id: int
    reason: str
    credit_refunded: bool
    credit_balance: int


SearchEvent = Union[
    ResultEvent, SourceErrorEvent, ProgressEvent, DoneEvent, FailedEvent
]

_BY_NAME = {
    "result": ResultEvent,
    "source_error": SourceErrorEvent,
    "progress": ProgressEvent,
    "done": DoneEvent,
    "failed": FailedEvent,
}


def parse_event(sse: ServerSentEvent) -> Optional[SearchEvent]:
    """The typed event, or None for an event this version does not know."""
    kind = _BY_NAME.get(sse.event)
    if kind is None or sse.id is None:
        return None
    data = json.loads(sse.data)
    # A field added by a newer API is dropped rather than refused.
    known = {f.name for f in fields(kind)} - {"id"}
    return kind(id=int(sse.id), **{k: v for k, v in data.items() if k in known})
