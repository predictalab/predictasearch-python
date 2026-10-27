from types import TracebackType
from typing import Dict, List, Optional, Type

import requests

from predictasearch.errors import APIConnectionError, error_from_response
from predictasearch.models import NetworkInfo, QueryType, SearchResult

DEFAULT_BASE_URL = "https://dev.predictasearch.com"


class PredictaSearch:
    """Client of the Predicta Search API.

    :param api_key: Your API key, from https://www.predictasearch.com/.
    :param base_url: The API to call. Change it only to target another environment.
    :param timeout: Seconds to wait for an answer. ``None``, the default, waits as
        long as the search takes: a search on every network can last minutes.
    :param session: A ``requests.Session`` to send the requests through, for your
        own proxies or retries. The client creates one when none is given.

    :ivar credit_balance: The balance read on the last response, ``None`` before
        the first call.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.credit_balance: Optional[int] = None
        self._session = session or requests.Session()

    def search(
        self,
        query: str,
        query_type: QueryType,
        networks: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Search ``query`` on ``networks``, every network when none is given.

        The list holds the profiles found. A network that could not run the query
        appears as ``{"platform": ..., "error": ...}``.

        :raises PredictaSearchError: The search was refused or could not be sent.
        """
        response = self._request(
            "POST",
            "/api/search",
            json={
                "query": query,
                "query_type": query_type,
                "networks": networks or ["all"],
            },
        )
        return response.json()

    def search_by_email(
        self, email: str, networks: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search an email address. See :meth:`search`."""
        return self.search(email, "email", networks)

    def search_by_phone(
        self, phone: str, networks: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search a phone number in international format (``+33612345678``).
        See :meth:`search`."""
        return self.search(phone, "phone", networks)

    def search_by_name(
        self, name: str, networks: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search a full name, two words or more. See :meth:`search`."""
        return self.search(name, "name", networks)

    def search_by_username(
        self, username: str, networks: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search a username. See :meth:`search`."""
        return self.search(username, "username", networks)

    def get_supported_networks(self) -> Dict[str, NetworkInfo]:
        """The networks you can search, by name, with the query types each accepts.

        :raises PredictaSearchError: The request was refused or could not be sent.
        """
        return self._request("GET", "/api/networks").json()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "PredictaSearch":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def _request(
        self, method: str, path: str, json: Optional[Dict[str, object]] = None
    ) -> requests.Response:
        try:
            response = self._session.request(
                method,
                f"{self.base_url}{path}",
                headers={"x-api-key": self.api_key},
                json=json,
                timeout=(10, self.timeout),
            )
        except requests.RequestException as error:
            raise APIConnectionError(str(error)) from error

        balance = response.headers.get("x-credit-balance")
        if balance is not None and balance.lstrip("-").isdigit():
            self.credit_balance = int(balance)
        if not response.ok:
            raise error_from_response(response)
        return response
