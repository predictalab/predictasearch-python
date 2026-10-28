# predictasearch: The official Python library and CLI for Predicta Search
predictasearch is a Python library that interacts with the PredictaSearch API to perform searches on emails and phone numbers, as well as retrieve the list of supported networks.

## Features
- Search by email address
- Search by phone number
- Search by name
- Search by username
- Retrieve the list of supported networks
- Streaming search (API v2): start a search, then read each source's profiles the moment it answers

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

The routes and their status codes are described at
https://dev.predictasearch.com/redoc.

### Reading a stream, and resuming it
A connection can drop before the end. Keep the `id` of the last event read and
open the stream again with `last_event_id`: it resumes right after it. Once the
search has ended, the API answers 204 when no event follows.

```python
import json
import time

import requests


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


def search(client, query, query_type):
    started = client.start_search(query, query_type)
    started.raise_for_status()
    search_id = started.json()["search_id"]

    last_id = None
    while True:
        try:
            with client.stream_search(search_id, last_event_id=last_id) as response:
                if response.status_code == 204:
                    return  # the search has ended: nothing after last_id
                response.raise_for_status()
                for last_id, event, data in read_events(response):
                    yield event, data
                    if event in ("done", "failed"):
                        return
        except requests.ConnectionError:
            pass  # dropped: reopen after the last event received
        time.sleep(3)


for event, data in search(client, "example@email.com", "email"):
    if event == "result":
        print(data["network"], data["data"])
```

`stream_search` waits up to a minute for the next line: the API pings every
15 seconds, so a longer silence raises `requests.ConnectionError`, a dead
connection to reopen.

## Installation
To install the Predicta Search library, simply:
```bash
pip install predictasearch
```

## Documentation
Documentation is available at https://dev.predictasearch.com/redoc