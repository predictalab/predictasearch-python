# predictasearch: The official Python library for Predicta Search
predictasearch is a Python library that interacts with the PredictaSearch API to search an email address, a phone number, a name or a username, as well as retrieve the list of supported networks.

## Features
- Search by email address
- Search by phone number
- Search by name
- Search by username
- Retrieve the list of supported networks
- Streaming search (API v2): start a search, then read each source's profiles the moment it answers

## Quick Start
```python
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
each source's profiles the moment it answers, in two calls that return the
API's `requests.Response` as it is:

- `start_search(query, query_type, networks=None)`: `POST /api/v2/search`. It
  answers at once, 202 with the `search_id` (200 if the same search is already
  running, without another credit).
- `stream_search(search_id, last_event_id=None)`: `GET /api/v2/search/{search_id}`,
  a Server-Sent Events stream: one `result` event per source that finds
  something, `source_error` per source that cannot answer, `progress` every
  5 seconds, then `done` or `failed`. Its body is left unread, to be read as it
  arrives.

The routes, the events and their fields are described in the API documentation:
https://www.predictasearch.com/api-docs.

### Handling the responses: a proof of concept
`start_search` and `stream_search` return the API's answer as it is: checking
its status, reading the stream and resuming it are up to the caller. The code
below does all three, and can be copied as a starting point: it stops on any
refusal with its status and the API's reason, and waits on a 429 as the API
asks. What each status means is described in the API documentation:
https://www.predictasearch.com/api-docs#errors.

A connection can also drop before the end. Keep the `id` of the last event read
and open the stream again with `last_event_id`: it resumes right after it.

```python
import json
import time

import requests


class SearchRefused(Exception):
    """The API refused the call: status_code and detail say why."""

    def __init__(self, status_code, detail):
        super().__init__(f"{status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


def refused(response):
    try:
        detail = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        detail = response.text  # a 500 answers in plain text
    return SearchRefused(response.status_code, detail)


def read_events(response):
    """Yields the (id, event, data) of a Server-Sent Events stream."""
    fields = {}
    for line in response.iter_lines():
        line = line.decode("utf-8")
        if line.startswith(":"):
            continue  # a ping, sent every 15 s
        if line:
            name, _, value = line.partition(": ")
            fields[name] = value
        elif "event" in fields:
            yield int(fields["id"]), fields["event"], json.loads(fields["data"])
            fields = {}


def search(client, query, query_type, networks=None):
    """Yields the (event, data) of a v2 search, until done or failed."""
    while True:
        started = client.start_search(query, query_type, networks)
        if started.status_code != 429:
            break
        time.sleep(int(started.headers.get("Retry-After", 30)))
    if started.status_code not in (200, 202):
        raise refused(started)
    search_id = started.json()["search_id"]

    last_id = None
    while True:
        try:
            with client.stream_search(search_id, last_event_id=last_id) as response:
                if response.status_code == 204:
                    return  # the search has ended: nothing after last_id
                if response.status_code == 429:
                    time.sleep(int(response.headers.get("Retry-After", 60)))
                    continue
                if response.status_code != 200:
                    raise refused(response)
                for last_id, event, data in read_events(response):
                    yield event, data
                    if event in ("done", "failed"):
                        return
        except requests.ConnectionError:
            pass  # dropped: reopen after the last event received
        time.sleep(3)
```

Using it:

```python
profiles, unanswered = {}, {}
try:
    for event, data in search(client, "example@email.com", "email"):
        if event == "result":
            profiles[data["network"]] = data["data"]
        elif event == "source_error":
            unanswered[data["network"]] = data["reason"]
        elif event == "done":
            print(f"{len(profiles)} sources found something, "
                  f"credit spent: {data['credit_debited']}")
        elif event == "failed":
            print(f"Interrupted on our side ({data['reason']}), credit refunded")
except SearchRefused as error:
    if error.status_code == 402:
        print("No credit left")
    else:
        print("Search refused:", error)
```

`stream_search` waits up to a minute for the next line: the API pings every
15 seconds, so a longer silence raises `requests.ConnectionError`, a dead
connection to reopen.

### The v1 search
The v1 methods return the JSON body: a list on success, `{"detail": "..."}`
when the API refuses. In the list, a network that could not run the query
appears as `{"platform": ..., "error": ...}`.

```python
results = client.search_by_email("example@email.com")
if isinstance(results, dict):  # refused: no credit, invalid key, bad query...
    print("Search refused:", results["detail"])
else:
    for item in results:
        if "error" in item:
            print(item["platform"], "skipped:", item["error"])
        else:
            print(item["platform"], item)
```

## Installation
To install the Predicta Search library, simply:
```bash
pip install predictasearch
```

## Documentation
The API documentation, for every route, event, status and credit rule, is at
https://www.predictasearch.com/api-docs. The API itself answers at
https://dev.predictasearch.com.