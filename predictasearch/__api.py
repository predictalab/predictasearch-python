import requests
from typing import Literal, Optional, List, Dict


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

    def search(self, query: str, query_type: Literal["email", "phone"], networks: Optional[list[str]] = None) -> List:
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
                "query_type": query_type
            }
        )

        return response.json()

    def search_by_email(self, email: str, networks: Optional[list[str]] = None) -> List:
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
        return self.search(query=email, query_type="email", networks=networks)

    def search_by_phone(self, phone: str, networks: Optional[list[str]] = None) -> List:
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
        return self.search(query=phone, query_type="phone", networks=networks)

    def get_supported_networks(self) -> Dict:
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
            url=f"{self.BASE_URL}{route}",
            headers=self.headers
        )

        return response.json()
