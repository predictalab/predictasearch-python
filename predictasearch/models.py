from dataclasses import dataclass
from typing import Any, Dict, List, Literal, TypedDict

QueryType = Literal["email", "phone", "name", "username"]
SearchStatus = Literal["running", "done", "failed"]

# A profile's fields depend on the source that found it; "platform" names that source.
SearchResult = Dict[str, Any]


class RejectedNetwork(TypedDict):
    platform: str
    error: str


@dataclass(frozen=True)
class SearchJob:
    """A v2 search, as started by :meth:`PredictaSearch.start_search`.

    :ivar total: The number of sources queried.
    :ivar networks_rejected: The networks asked for that cannot run the query.
    :ivar already_running: The same search was running: this is that search, and
        no credit was used.
    """

    search_id: str
    status: SearchStatus
    total: int
    networks_rejected: List[RejectedNetwork]
    already_running: bool
