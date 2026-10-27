# predictasearch

The official Python client of the [Predicta Search](https://www.predictasearch.com/) API.
Search an email address, a phone number, a name or a username across 1,800+ sources.

## Installation

```bash
pip install predictasearch
```

Python 3.9 or later. Get your API key from your account on https://www.predictasearch.com/.

## Quick start

```python
import os

from predictasearch import PredictaSearch

with PredictaSearch(api_key=os.environ["PREDICTA_API_KEY"]) as client:
    for profile in client.search_by_email("john.doe@gmail.com"):
        print(profile["platform"], profile)

    print("Credits left:", client.credit_balance)
```

| Method | Searches |
|---|---|
| `search_by_email(email, networks=None)` | an email address |
| `search_by_phone(phone, networks=None)` | a phone number, international format: `+33612345678` |
| `search_by_name(name, networks=None)` | a full name, two words or more |
| `search_by_username(username, networks=None)` | a username |
| `search(query, query_type, networks=None)` | any of the above, `query_type` being `"email"`, `"phone"`, `"name"` or `"username"` |
| `get_supported_networks()` | the networks you can search, and the query types each accepts |

Each search costs one credit. It returns a list: the profiles found, each with a
`platform` field naming its source, and `{"platform": ..., "error": ...}` for a
network that could not run the query.

### Choosing the networks

Without `networks`, a search covers every network and can take several minutes.
Pass names from `get_supported_networks()` to search only some of them:

```python
client.search_by_email("john.doe@gmail.com", networks=["google", "hibp"])
```

## Errors

Every error derives from `PredictaSearchError`:

| Exception | When |
|---|---|
| `AuthenticationError` | 401: the API key is missing or invalid |
| `InsufficientCreditsError` | 402: no credit left |
| `PermissionDeniedError` | 403: the account is locked, or the search is not allowed |
| `InvalidRequestError` | 400 or 422: the query does not match its type |
| `RateLimitError` | 429: too many requests; `retry_after` gives the wait in seconds |
| `ServerError` | 5xx: the API failed or is under maintenance |
| `APIConnectionError` | the API could not be reached, or did not answer within `timeout` |

`APIError` and its subclasses carry `status_code` and `detail`, the reason given by the API.

```python
from predictasearch import InsufficientCreditsError, PredictaSearchError

try:
    profiles = client.search_by_username("johndoe")
except InsufficientCreditsError:
    print("Top up your credits")
except PredictaSearchError as error:
    print("Search failed:", error)
```

## Configuration

```python
PredictaSearch(
    api_key="...",
    base_url="https://dev.predictasearch.com",
    timeout=None,       # seconds to wait for an answer; None waits as long as the search takes
    session=None,       # your own requests.Session, for proxies or retries
)
```

`client.credit_balance` holds the balance read on the last response, `None` before the first call.

## Upgrading from 1.x

- Errors now raise an exception. 1.x returned the error body, `{"detail": ...}`, in place of the results.
- Python 3.9 or later is required.
- `BASE_URL` and `headers` are gone: pass `base_url=` to the constructor if you need another environment.

See [CHANGELOG.md](CHANGELOG.md).

## Documentation

The API reference is at https://dev.predictasearch.com/redoc.

## Development

```bash
pip install -r requirements-dev.txt -e .
pre-commit install
pytest
```
