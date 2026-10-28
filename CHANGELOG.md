# Changelog

## 1.1.0

- The API v2: `start_search()` and `stream_search()` call its two routes and
  return the `requests.Response` as it is; the stream is left unread, and
  `last_event_id` resumes it after a dropped connection. The v1 methods are
  unchanged.
- Python 3.11 or later, and requests 2.33.0 or later: the releases that fix
  the vulnerabilities of 2.32.x, and require Python 3.10 themselves.

## 1.0.2

- Python 3.9 or later. 1.0.1 declared 3.8, on which it failed to import.
- Packaging moves to `pyproject.toml`; `setup.py` is removed. The package
  itself is unchanged.

## 1.0.1

- Search by name and by username.

## 1.0.0

- Search by email address and by phone number, and list the supported networks.
