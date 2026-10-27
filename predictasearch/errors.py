from typing import Dict, Optional, Type

import requests


class PredictaSearchError(Exception):
    """Base class of every error the client raises."""


class APIConnectionError(PredictaSearchError):
    """The API could not be reached, or did not answer within the timeout."""


class APIError(PredictaSearchError):
    """The API answered with an error status.

    :ivar status_code: The HTTP status of the response.
    :ivar detail: The reason given by the API.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class InvalidRequestError(APIError):
    """400 or 422: the query does not match its type, or no network can run it."""


class AuthenticationError(APIError):
    """401: the API key is missing or invalid."""


class InsufficientCreditsError(APIError):
    """402: no credit left on the account."""


class PermissionDeniedError(APIError):
    """403: the account is locked, or the search is not allowed."""


class NotFoundError(APIError):
    """404: the resource does not exist."""


class RateLimitError(APIError):
    """429: too many requests.

    :ivar retry_after: Seconds to wait before trying again, when the API says so.
    """

    def __init__(
        self, status_code: int, detail: str, retry_after: Optional[int] = None
    ) -> None:
        super().__init__(status_code, detail)
        self.retry_after = retry_after


class ServerError(APIError):
    """5xx: the API failed, or is under maintenance. Try again later."""


_BY_STATUS: Dict[int, Type[APIError]] = {
    400: InvalidRequestError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: InvalidRequestError,
}


def _detail(response: requests.Response) -> str:
    try:
        detail = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        return response.text or response.reason
    # FastAPI's own validation errors give a list of {"loc", "msg", ...}.
    if isinstance(detail, list):
        return "; ".join(str(error.get("msg", error)) for error in detail)
    return str(detail)


def _retry_after(response: requests.Response) -> Optional[int]:
    try:
        return int(response.headers["Retry-After"])
    except (KeyError, ValueError):
        return None


def error_from_response(response: requests.Response) -> APIError:
    status_code, detail = response.status_code, _detail(response)
    if status_code == 429:
        return RateLimitError(status_code, detail, _retry_after(response))
    if status_code >= 500:
        return ServerError(status_code, detail)
    return _BY_STATUS.get(status_code, APIError)(status_code, detail)
