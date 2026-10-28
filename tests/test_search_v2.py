import json

import pytest
import responses

from predictasearch import PredictaSearch

URL = "https://dev.predictasearch.com"
STREAM_URL = f"{URL}/api/v2/search/abc"
JOB = {"search_id": "abc", "status": "running", "total": 3, "networks_rejected": []}


@pytest.fixture
def client():
    return PredictaSearch(api_key="key")


@pytest.fixture
def api():
    with responses.RequestsMock() as mock:
        yield mock


def test_start_search_posts_the_query_and_returns_the_response(client, api):
    api.post(f"{URL}/api/v2/search", json=JOB, status=202)

    response = client.start_search("johndoe", "username", ["github"])

    assert response.status_code == 202 and response.json() == JOB
    request = api.calls[0].request
    assert request.headers["x-api-key"] == "key"
    assert json.loads(request.body) == {
        "networks": ["github"],
        "query": "johndoe",
        "query_type": "username",
    }


def test_start_search_covers_every_network_by_default(client, api):
    api.post(f"{URL}/api/v2/search", json=JOB, status=202)

    client.start_search("johndoe", "username")

    assert json.loads(api.calls[0].request.body)["networks"] == ["all"]


def test_an_error_is_returned_as_it_is(client, api):
    api.post(f"{URL}/api/v2/search", json={"detail": "No credit"}, status=402)

    response = client.start_search("johndoe", "username")

    assert response.status_code == 402 and response.json() == {"detail": "No credit"}


def test_stream_search_returns_the_stream_unread(client, api):
    body = 'retry: 3000\n\nid: 0\nevent: done\ndata: {"found": 0}\n\n'
    api.get(STREAM_URL, body=body, content_type="text/event-stream")

    with client.stream_search("abc") as response:
        assert response.status_code == 200
        assert b"".join(response.iter_content()).decode() == body

    request = api.calls[0].request
    assert request.headers["x-api-key"] == "key"
    assert "Last-Event-ID" not in request.headers
    assert request.req_kwargs["stream"] is True
    assert request.req_kwargs["timeout"] == (10, 60)


def test_stream_search_resumes_after_an_event(client, api):
    api.get(STREAM_URL, status=204)

    response = client.stream_search("abc", last_event_id=4)

    assert response.status_code == 204
    assert api.calls[0].request.headers["Last-Event-ID"] == "4"


def test_v1_still_returns_the_error_body(client, api):
    detail = {"detail": "No enough API quota"}
    api.post(f"{URL}/api/search", json=detail, status=402)

    assert client.search_by_email("john.doe@gmail.com") == detail
