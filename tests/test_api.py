import pytest
from unittest.mock import patch, MagicMock
from predictasearch.__api import PredictaSearch


@pytest.fixture
def api_key() -> str:
    return "sk_test_dummy"


@pytest.fixture
def client(api_key) -> PredictaSearch:
    return PredictaSearch(api_key=api_key)


@pytest.fixture
def sample_email_results() -> list:
    return [
        {
            "platform": "google",
            "email": "elon.musk@gmail.com",
            "user_id": "114461178896543099856",
            "link": "https://www.google.com/maps/contrib/114461178896543099856/reviews",
            "pfp_image": "https://lh3.googleusercontent.com/a-/..."
        },
        {
            "username": "elonmusk9001042",
            "platform": "picsart",
            "link": "https://picsart.com/u/elonmusk9001042",
            "user_id": "395141841033101",
            "is_verified": False,
            "followers_count": 0
        }
    ]


@pytest.fixture
def sample_networks_response() -> dict:
    return {
        "google": {
            "type": "social",
            "actions": [
                {
                    "inputs": ["email"],
                    "outputs": ["users"]
                }
            ]
        },
        "hibp": {
            "type": "leak",
            "actions": [
                {
                    "inputs": ["email", "phone"],
                    "outputs": ["breaches"]
                }
            ]
        }
    }


def test_search_by_email_returns_sample_data(client, sample_email_results):
    with patch("predictasearch.__api.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_email_results
        mock_post.return_value = mock_response

        results = client.search_by_email("elon.musk@gmail.com", networks=["google"])
        assert isinstance(results, list)
        assert results[0]["platform"] == "google"
        assert results[1]["platform"] == "picsart"


def test_search_by_phone_returns_data(client):
    with patch("predictasearch.__api.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"platform": "chess", "user_id": "12345"}]
        mock_post.return_value = mock_response

        results = client.search_by_phone("+123456789")
        assert isinstance(results, list)
        assert results[0]["platform"] == "chess"


def test_get_supported_networks_returns_expected_dict(client, sample_networks_response):
    with patch("predictasearch.__api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_networks_response
        mock_get.return_value = mock_response

        networks = client.get_supported_networks()
        assert "google" in networks
        assert networks["google"]["type"] == "social"
        assert networks["hibp"]["type"] == "leak"
