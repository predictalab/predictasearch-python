from typing import Any, Dict, List, Literal, TypedDict

QueryType = Literal["email", "phone", "name", "username"]

# A profile's fields depend on the source that found it; "platform" names that source.
SearchResult = Dict[str, Any]


class NetworkAction(TypedDict):
    inputs: List[QueryType]
    outputs: List[str]


class NetworkInfo(TypedDict):
    type: str
    actions: List[NetworkAction]
