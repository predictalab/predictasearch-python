import pytest
import responses

from predictasearch import (
    APIError,
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
    PredictaSearch,
    RateLimitError,
    ServerError,
)

URL = "https://dev.predictasearch.com/api/v2/search"


def _search_answering(**response):
    with responses.RequestsMock() as api:
        api.post(URL, **response)
        PredictaSearch(api_key="key").start_search("johndoe", "username")


@pytest.mark.parametrize(
    "status, error",
    [
        (400, InvalidRequestError),
        (401, AuthenticationError),
        (402, InsufficientCreditsError),
        (403, PermissionDeniedError),
        (404, NotFoundError),
        (422, InvalidRequestError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
        (418, APIError),
    ],
)
def test_each_status_raises_its_error(status, error):
    with pytest.raises(error) as raised:
        _search_answering(status=status, json={"detail": "The reason"})

    assert raised.value.status_code == status
    assert raised.value.detail == "The reason"


def test_validation_errors_are_joined():
    detail = [{"loc": ["body", "query"], "msg": "Field required", "type": "missing"}]

    with pytest.raises(InvalidRequestError, match="Field required"):
        _search_answering(status=422, json={"detail": detail})


def test_rate_limit_gives_the_wait():
    with pytest.raises(RateLimitError) as raised:
        _search_answering(
            status=429, json={"detail": "Too many"}, headers={"Retry-After": "30"}
        )

    assert raised.value.retry_after == 30


def test_rate_limit_without_a_wait():
    with pytest.raises(RateLimitError) as raised:
        _search_answering(status=429, json={"detail": "Too many"})

    assert raised.value.retry_after is None


def test_plain_text_error_keeps_its_body():
    with pytest.raises(ServerError) as raised:
        _search_answering(status=500, body="boom", content_type="text/plain")

    assert raised.value.detail == "boom"
