import json

import pytest
import requests
import responses

from predictasearch import (
    APIConnectionError,
    DoneEvent,
    FailedEvent,
    NotFoundError,
    PredictaSearch,
    ProgressEvent,
    RateLimitError,
    ResultEvent,
    SearchJob,
)

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


JOB = {"search_id": "abc", "status": "running", "total": 3, "networks_rejected": []}
STREAM_URL = f"{URL}/api/v2/search/abc"


def _sse(*events):
    blocks = ["retry: 3000\n\n"]
    for id, name, data in events:
        blocks.append(f"id: {id}\nevent: {name}\ndata: {json.dumps(data)}\n\n")
    return "".join(blocks)


RESULT = (0, "result", {"network": "github", "data": PROFILES})
PROGRESS = (1, "progress", {"done": 1, "total": 3, "found": 1, "failed": 0})
DONE = (
    2,
    "done",
    {"found": 1, "failed": 1, "credit_debited": True, "credit_balance": 4},
)


@pytest.fixture
def sleeps(monkeypatch):
    waited = []
    monkeypatch.setattr("predictasearch.time.sleep", waited.append)
    return waited


def test_start_search_reserves_a_new_search(client, api):
    api.post(f"{URL}/api/v2/search", json=JOB, status=202)

    job = client.start_search("johndoe", "username")

    assert job == SearchJob("abc", "running", 3, [], already_running=False)
    assert _body(api) == {
        "query": "johndoe",
        "query_type": "username",
        "networks": ["all"],
    }


def test_start_search_gives_the_search_already_running(client, api):
    api.post(f"{URL}/api/v2/search", json=JOB, status=200)

    assert client.start_search("johndoe", "username").already_running


def test_too_many_searches_at_once(client, api):
    api.post(
        f"{URL}/api/v2/search",
        json={"detail": "Too many"},
        status=429,
        headers={"Retry-After": "30"},
    )

    with pytest.raises(RateLimitError) as raised:
        client.start_search("johndoe", "username")

    assert raised.value.retry_after == 30


def test_stream_gives_every_event_until_done(client, api):
    api.get(STREAM_URL, body=_sse(RESULT, PROGRESS, DONE))

    events = list(client.stream_search("abc"))

    assert [type(e) for e in events] == [ResultEvent, ProgressEvent, DoneEvent]
    assert events[0].data == PROFILES
    assert events[-1].credit_balance == 4
    assert api.calls[0].request.headers["Accept"] == "text/event-stream"
    assert "Last-Event-ID" not in api.calls[0].request.headers


def test_stream_resumes_after_a_given_event(client, api):
    api.get(STREAM_URL, body=_sse(DONE))

    list(client.stream_search("abc", last_event_id=1))

    assert api.calls[0].request.headers["Last-Event-ID"] == "1"


def test_a_dropped_stream_is_reopened_where_it_stopped(client, api, sleeps):
    api.get(STREAM_URL, body=_sse(RESULT, PROGRESS))
    api.get(STREAM_URL, body=_sse(DONE))

    events = list(client.stream_search("abc"))

    assert [e.id for e in events] == [0, 1, 2]
    assert api.calls[1].request.headers["Last-Event-ID"] == "1"
    assert sleeps == [3.0]


def test_a_broken_connection_is_reopened(client, api, sleeps):
    api.get(STREAM_URL, body=requests.ConnectionError("reset"))
    api.get(STREAM_URL, body=_sse(RESULT, PROGRESS, DONE))

    assert len(list(client.stream_search("abc"))) == 3
    assert sleeps == [3.0]


def test_a_rate_limited_reopening_waits_as_asked(client, api, sleeps):
    api.get(
        STREAM_URL,
        json={"detail": "Too many"},
        status=429,
        headers={"Retry-After": "60"},
    )
    api.get(STREAM_URL, body=_sse(DONE))

    list(client.stream_search("abc"))

    assert sleeps == [60]


def test_an_expired_search_is_not_retried(client, api, sleeps):
    api.get(STREAM_URL, json={"detail": "Not found"}, status=404)

    with pytest.raises(NotFoundError):
        list(client.stream_search("abc"))

    assert sleeps == []


def test_a_stream_that_keeps_dropping_gives_up(client, api, sleeps):
    api.get(STREAM_URL, body=_sse())

    with pytest.raises(APIConnectionError):
        list(client.stream_search("abc", max_retries=2))

    assert len(api.calls) == 3


def test_a_failed_search_ends_the_stream(client, api):
    failed = (
        0,
        "failed",
        {"reason": "shutdown", "credit_refunded": True, "credit_balance": 5},
    )
    api.get(STREAM_URL, body=_sse(failed))

    events = list(client.stream_search("abc"))

    assert events == [FailedEvent(0, "shutdown", True, 5)]


def test_v1_still_returns_the_error_body(client, api):
    detail = {"detail": "No enough API quota"}
    api.post(f"{URL}/api/search", json=detail, status=402)

    assert client.search_by_email("john.doe@gmail.com") == detail


def test_resuming_after_the_end_yields_nothing(client, api, sleeps):
    api.get(STREAM_URL, status=204)

    assert list(client.stream_search("abc", last_event_id=2)) == []
    assert len(api.calls) == 1 and sleeps == []
