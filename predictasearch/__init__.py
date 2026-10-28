import time
from typing import Dict, Iterator, List, Literal, Optional

import requests

from predictasearch.errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
    PredictaSearchError,
    RateLimitError,
    ServerError,
    error_from_response,
)
from predictasearch.events import (
    DoneEvent,
    FailedEvent,
    ProgressEvent,
    ResultEvent,
    SearchEvent,
    SourceErrorEvent,
    parse_event,
)
from predictasearch.models import (
    QueryType,
    RejectedNetwork,
    SearchJob,
    SearchResult,
    SearchStatus,
)
from predictasearch.sse import SSEDecoder

__all__ = [
    "PredictaSearch",
    "APIConnectionError",
    "APIError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "InvalidRequestError",
    "NotFoundError",
    "PermissionDeniedError",
    "PredictaSearchError",
    "RateLimitError",
    "ServerError",
    "DoneEvent",
    "FailedEvent",
    "ProgressEvent",
    "ResultEvent",
    "SearchEvent",
    "SourceErrorEvent",
    "QueryType",
    "RejectedNetwork",
    "SearchJob",
    "SearchResult",
    "SearchStatus",
]


class PredictaSearch:
    """
    Represents an API client for interacting with PredictaSearch's API. This class provides
    methods to perform various search operations and retrieve supported network data.

    The class is designed to initialize with an API key and create authenticated requests
    to the PredictaSearch service. It supports various query types such as email and phone
    searches, along with fetching the list of supported networks.

    :ivar BASE_URL: The base URL of the PredictaSearch API endpoint.
    :type BASE_URL: str
    """

    BASE_URL: str = "https://dev.predictasearch.com/"

    def __init__(self, api_key: str):
        """
        Represents a class that initializes an API integration with an API key and associated headers.

        Attributes
        ----------
        api_key : str
            The API key required for authentication with an external service.
        headers : dict
            HTTP headers including the API key for making authenticated requests.

        :param api_key: The API key used for accessing the relevant API.
        :type api_key: str
        """
        self.api_key: str = api_key
        self.headers: dict = {"x-api-key": self.api_key}

    def _search(
        self,
        query: str,
        query_type: Literal["email", "phone", "name", "username"],
        networks: Optional[list[str]] = None,
    ) -> list:
        """
        Executes a search query against the API with the provided parameters. This method allows querying
        based on a specific type and optionally limits the search scope to a set of networks.

        :param query: The search term to query for. It is required and represents the key phrase or identifier
            to look up in the system.
        :type query: str

        :param query_type: Specifies the type of the query. Accepted values are "email" or "phone".
            Determines the format and validation rules for the query parameter.
        :type query_type: Literal["email", "phone"]

        :param networks: A list of network names to constrain the query to. If not provided,
            defaults to querying all networks. This parameter is optional and can be None.
        :type networks: Optional[list[str]]

        :return: A list containing the search results returned from the API. This list captures all data
            matching the specified query parameters.
        :rtype: list
        """
        route: str = "api/search"
        response: requests.Response = requests.post(
            url=f"{self.BASE_URL}{route}",
            headers=self.headers,
            json={
                "networks": networks or ["all"],
                "query": query,
                "query_type": query_type,
            },
        )

        return response.json()

    def search_by_email(self, email: str, networks: Optional[list[str]] = None) -> list:
        """
        Search for records based on a given email address and optionally limited to a list
        of networks.

        This method performs a search operation using the provided email as the query. It
        allows filtering of the results by specifying a list of networks to limit the
        search scope. The results returned will be a list of records that match the
        search parameters.

        :param email: The email address to search for.
        :type email: str
        :param networks: A list of network names to limit the search to. Defaults to None
            if no specific networks are provided.
        :type networks: Optional[list[str]]
        :return: A list of records that match the provided email and optional network filters.
        :rtype: list
        """
        return self._search(query=email, query_type="email", networks=networks)

    def search_by_phone(self, phone: str, networks: Optional[list[str]] = None) -> list:
        """
        Search for records by phone number and optionally limited to a list
        of networks.

        This method performs a search operation using the provided phone number as the query. It
        allows filtering of the results by specifying a list of networks to limit the
        search scope. The results returned will be a list of records that match the
        search parameters.

        :param phone: The phone number to search for.
        :type phone: str
        :param networks: A list of network names to limit the search to. Defaults to None
            if no specific networks are provided.
        :type networks: Optional[list[str]]
        :return: A list of records that match the provided email and optional network filters.
        :rtype: list
        """
        return self._search(query=phone, query_type="phone", networks=networks)

    def search_by_name(self, name: str, networks: Optional[list[str]] = None) -> list:
        """
        Search for records by name and optionally limited to a list
        of networks.

        This method performs a search operation using the provided name as the query. It
        allows filtering of the results by specifying a list of networks to limit the
        search scope. The results returned will be a list of records that match the
        search parameters.

        :param name: The name to search for.
        :type name: str
        :param networks: A list of network names to limit the search to. Defaults to None
            if no specific networks are provided.
        :type networks: Optional[list[str]]
        :return: A list of records that match the provided name and optional network filters.
        :rtype: list
        """
        return self._search(query=name, query_type="name", networks=networks)

    def search_by_username(
        self, username: str, networks: Optional[list[str]] = None
    ) -> list:
        """
        Search for records by username and optionally limited to a list
        of networks.

        This method performs a search operation using the provided username as the query. It
        allows filtering of the results by specifying a list of networks to limit the
        search scope. The results returned will be a list of records that match the
        search parameters.

        :param username: The username to search for.
        :type username: str
        :param networks: A list of network names to limit the search to. Defaults to None
            if no specific networks are provided.
        :type networks: Optional[list[str]]
        :return: A list of records that match the provided username and optional network filters.
        :rtype: list
        """
        return self._search(query=username, query_type="username", networks=networks)

    def get_supported_networks(self) -> dict:
        """
        Fetch the list of supported networks from the API.

        This method sends a GET request to the specified API endpoint to retrieve
        a dictionary containing the details of all supported networks. The
        response data is parsed as JSON and returned as a Python dictionary.

        :return: A dictionary containing details of supported networks retrieved
            from the API.
        :rtype: dict
        """
        route: str = "api/networks"
        response: requests.Response = requests.get(
            url=f"{self.BASE_URL}{route}", headers=self.headers
        )

        return response.json()

    def start_search(
        self,
        query: str,
        query_type: QueryType,
        networks: Optional[List[str]] = None,
    ) -> SearchJob:
        """Start a v2 search and return at once; read it with :meth:`stream_search`.

        One credit is reserved, and refunded if no source could answer. Sending
        the same search while it runs returns that search, without another credit.

        :raises RateLimitError: Too many searches running for this key.
        :raises PredictaSearchError: The search was refused or could not be sent.
        """
        response = self._v2_request(
            "POST",
            "api/v2/search",
            json={
                "query": query,
                "query_type": query_type,
                "networks": networks or ["all"],
            },
        )
        body = response.json()
        return SearchJob(
            search_id=body["search_id"],
            status=body["status"],
            total=body["total"],
            networks_rejected=body["networks_rejected"],
            already_running=response.status_code == 200,
        )

    def stream_search(
        self,
        search_id: str,
        last_event_id: Optional[int] = None,
        max_retries: int = 5,
    ) -> Iterator[SearchEvent]:
        """Yield the events of a v2 search as they arrive, until it ends.

        The last event is a :class:`DoneEvent` or a :class:`FailedEvent`. A
        dropped connection is reopened where it stopped, after the delay the API
        asks for; ``max_retries`` reopenings in a row without a new event raise
        :class:`APIConnectionError`.

        :param last_event_id: Resume after this event, from a previous reading.
            Without it, the whole search is read from the start: within an hour
            after its end, a search can be read again.
        :raises NotFoundError: Unknown search, or results expired.
        :raises PredictaSearchError: The stream was refused or kept failing.
        """
        decoder = SSEDecoder()
        failures = 0
        while True:
            wait: Optional[float] = None
            last_error: PredictaSearchError
            try:
                with self._open_stream(search_id, last_event_id) as response:
                    lines = (line.decode("utf-8") for line in response.iter_lines())
                    for sse in decoder.iter_events(lines):
                        event = parse_event(sse)
                        if event is None:
                            continue
                        last_event_id, failures = event.id, 0
                        yield event
                        if isinstance(event, (DoneEvent, FailedEvent)):
                            return
            except RateLimitError as error:
                wait, last_error = error.retry_after, error
            except (APIConnectionError, ServerError) as error:
                last_error = error
            except requests.RequestException as error:
                last_error = APIConnectionError(str(error))
            else:
                last_error = APIConnectionError("The stream ended before the search")

            failures += 1
            if failures > max_retries:
                raise last_error
            time.sleep(wait if wait is not None else (decoder.retry or 3000) / 1000)

    def _open_stream(
        self, search_id: str, last_event_id: Optional[int]
    ) -> requests.Response:
        headers = {"Accept": "text/event-stream"}
        if last_event_id is not None:
            headers["Last-Event-ID"] = str(last_event_id)
        return self._v2_request(
            "GET", f"api/v2/search/{search_id}", headers=headers, stream=True
        )

    def _v2_request(
        self,
        method: str,
        route: str,
        json: Optional[Dict[str, object]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ) -> requests.Response:
        try:
            response = requests.request(
                method,
                url=f"{self.BASE_URL}{route}",
                headers={**self.headers, **(headers or {})},
                json=json,
                stream=stream,
                # The API pings a stream every 15 s: a minute of silence is a dead connection.
                timeout=(10, 60),
            )
        except requests.RequestException as error:
            raise APIConnectionError(str(error)) from error
        if not response.ok:
            with response:
                raise error_from_response(response)
        return response
