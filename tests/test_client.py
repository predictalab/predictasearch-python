import json

import pytest
import requests
import responses

from predictasearch import APIConnectionError, InsufficientCreditsError, PredictaSearch

URL = "https://dev.predictasearch.com"
PROFILES = [{"platform": "github", "username": "johndoe"}]


@pytest.fixture
def client():
    return PredictaSearch(api_key="key")


@pytest.fixture
def api():
    with responses.RequestsMock() as mock:
        yield mock


def _body(api):
    return json.loads(api.calls[0].request.body)


def test_search_sends_the_key_and_the_query(client, api):
    api.post(f"{URL}/api/search", json=PROFILES)

    assert client.search("johndoe", "username", ["github"]) == PROFILES

    request = api.calls[0].request
    assert request.headers["x-api-key"] == "key"
    assert _body(api) == {
        "query": "johndoe",
        "query_type": "username",
        "networks": ["github"],
    }


def test_search_covers_every_network_by_default(client, api):
    api.post(f"{URL}/api/search", json=[])

    client.search("johndoe", "username")

    assert _body(api)["networks"] == ["all"]


@pytest.mark.parametrize(
    "method, query_type",
    [
        ("search_by_email", "email"),
        ("search_by_phone", "phone"),
        ("search_by_name", "name"),
        ("search_by_username", "username"),
    ],
)
def test_each_shortcut_sends_its_query_type(client, api, method, query_type):
    api.post(f"{URL}/api/search", json=PROFILES)

    assert getattr(client, method)("x", networks=["github"]) == PROFILES

    assert _body(api) == {
        "query": "x",
        "query_type": query_type,
        "networks": ["github"],
    }


def test_get_supported_networks(client, api):
    networks = {"github": {"type": "social", "actions": []}}
    api.get(f"{URL}/api/networks", json=networks)

    assert client.get_supported_networks() == networks


def test_credit_balance_follows_the_last_response(client, api):
    api.post(f"{URL}/api/search", json=[], headers={"x-credit-balance": "41"})
    api.post(
        f"{URL}/api/search",
        json={"detail": "No credit left"},
        status=402,
        headers={"x-credit-balance": "0"},
    )
    assert client.credit_balance is None

    client.search("johndoe", "username")
    assert client.credit_balance == 41

    with pytest.raises(InsufficientCreditsError):
        client.search("johndoe", "username")
    assert client.credit_balance == 0


def test_base_url_may_end_with_a_slash(api):
    api.get("https://staging.example.com/api/networks", json={})

    PredictaSearch(
        api_key="key", base_url="https://staging.example.com/"
    ).get_supported_networks()

    assert api.calls[0].request.url == "https://staging.example.com/api/networks"


def test_timeout_bounds_the_wait_for_an_answer(api):
    api.get(f"{URL}/api/networks", json={})

    PredictaSearch(api_key="key", timeout=30).get_supported_networks()

    assert api.calls[0].request.req_kwargs["timeout"] == (10, 30)


def test_no_timeout_by_default(client, api):
    api.get(f"{URL}/api/networks", json={})

    client.get_supported_networks()

    assert api.calls[0].request.req_kwargs["timeout"] == (10, None)


def test_unreachable_api_is_a_connection_error(client, api):
    api.get(f"{URL}/api/networks", body=requests.ConnectionError("refused"))

    with pytest.raises(APIConnectionError, match="refused"):
        client.get_supported_networks()


def test_a_given_session_is_used(api):
    session = requests.Session()
    session.headers["X-Trace"] = "1"
    api.get(f"{URL}/api/networks", json={})

    with PredictaSearch(api_key="key", session=session) as client:
        client.get_supported_networks()

    assert api.calls[0].request.headers["X-Trace"] == "1"
