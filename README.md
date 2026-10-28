# predictasearch: The official Python library and CLI for Predicta Search
predictasearch is a Python library that interacts with the PredictaSearch API to perform searches on emails and phone numbers, as well as retrieve the list of supported networks.

## Features
- Search by email address
- Search by phone number
- Search by name
- Search by username
- Retrieve the list of supported networks
- Streaming search (API v2): receive each source's profiles the moment it answers

## Quick Start
```bash
import os
from predictasearch import PredictaSearch

client = PredictaSearch(api_key=os.environ["PREDICTA_API_KEY"])

networks = client.get_supported_networks()
print(networks)

email_results = client.search_by_email("example@email.com")
print(email_results)

phone_results = client.search_by_phone("+33612345678")
print(phone_results)

name_results = client.search_by_name("John Doe")
print(name_results)

username_results = client.search_by_username("Johndoe")
print(username_results)
```
Grab your API key from https://www.predictasearch.com/

## Streaming search (API v2)
The methods above wait for every source before answering. The v2 search gives
each source's profiles the moment it answers:
```python
from predictasearch import DoneEvent, FailedEvent, ResultEvent

job = client.start_search("example@email.com", "email")

for event in client.stream_search(job.search_id):
    if isinstance(event, ResultEvent):
        print(event.network, event.data)
    elif isinstance(event, DoneEvent):
        print(f"Done: {event.found} sources found something")
    elif isinstance(event, FailedEvent):
        print(f"Interrupted ({event.reason}), credit refunded")
```

`start_search(query, query_type, networks=None)` answers at once with a
`SearchJob`: its `search_id`, the number of sources queried (`total`), and
`networks_rejected`. Sending the same search while it runs gives back that
search, with `already_running` set and no credit used.

`stream_search(search_id)` yields, until the search ends:

| Event | When |
|---|---|
| `ResultEvent(id, network, data)` | a source found profiles |
| `SourceErrorEvent(id, network, reason)` | a source could not answer |
| `ProgressEvent(id, done, total, found, failed)` | every few seconds |
| `DoneEvent(id, found, failed, credit_debited, credit_balance)` | the search is complete, always last |
| `FailedEvent(id, reason, credit_refunded, credit_balance)` | the search was interrupted on our side, always last |

The credit is spent only if a source answered, and refunded when the search is
interrupted. If the connection drops, `stream_search` reopens it where it
stopped; after `max_retries` reopenings in a row (5 by default) without a new
event, it raises `APIConnectionError`. To resume in another process, keep the
last `event.id` and pass it as `last_event_id`; past the final event of an
ended search, nothing is yielded. A search can be read again, from the start,
for an hour after its end.

### Errors
The v2 methods raise an exception when the API refuses, each one deriving from
`PredictaSearchError` and carrying `status_code` and `detail`:

| Exception | When |
|---|---|
| `AuthenticationError` | 401: the API key is missing or invalid |
| `InsufficientCreditsError` | 402: no credit left |
| `PermissionDeniedError` | 403: the account is locked, or the search is not allowed |
| `NotFoundError` | 404: unknown search, or its results expired |
| `InvalidRequestError` | 400 or 422: the query does not match its type, or no network can run it |
| `RateLimitError` | 429: too many searches running at once; `retry_after` gives the wait in seconds |
| `ServerError` | 5xx: the API failed or is under maintenance |
| `APIConnectionError` | the API could not be reached, or did not answer in time |

The methods above, on the v1 search, are unchanged: they return the API's
answer as it is, `{"detail": ...}` included.

## Installation
To install the Predicta Search library, simply:
```bash
pip install predictasearch
```

## Documentation
Documentation is available at https://dev.predictasearch.com/redoc