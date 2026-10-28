from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional


@dataclass(frozen=True)
class ServerSentEvent:
    event: str
    data: str
    id: Optional[str] = None


@dataclass
class _Pending:
    event: Optional[str] = None
    id: Optional[str] = None
    data: List[str] = field(default_factory=list)


class SSEDecoder:
    """Reads a text/event-stream line by line, as the HTML spec describes.

    :ivar retry: The reconnection delay, in milliseconds, last sent by the server.
    """

    def __init__(self) -> None:
        self.retry: Optional[int] = None

    def iter_events(self, lines: Iterable[str]) -> Iterator[ServerSentEvent]:
        pending = _Pending()
        for line in lines:
            if line == "":
                if pending.data or pending.event:
                    yield ServerSentEvent(
                        event=pending.event or "message",
                        data="\n".join(pending.data),
                        id=pending.id,
                    )
                pending = _Pending()
            elif not line.startswith(":"):
                self._read_field(line, pending)

    def _read_field(self, line: str, pending: _Pending) -> None:
        name, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if name == "event":
            pending.event = value
        elif name == "data":
            pending.data.append(value)
        elif name == "id":
            pending.id = value
        elif name == "retry" and value.isdigit():
            self.retry = int(value)
