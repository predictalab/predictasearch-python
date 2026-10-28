# Changelog

## 1.1.0

- Python 3.11 or later, and requests 2.33.0 or later: the releases that fix
  the vulnerabilities of 2.32.x, and require Python 3.10 themselves.
- The streaming search of the API v2: `start_search()` starts a search and
  `stream_search()` yields its events (`ResultEvent`, `SourceErrorEvent`,
  `ProgressEvent`, then `DoneEvent` or `FailedEvent`), reopening a dropped
  connection where it stopped.
- The v2 methods raise a `PredictaSearchError` subclass when the API refuses
  (`AuthenticationError`, `InsufficientCreditsError`, `RateLimitError`...).
  The v1 methods are unchanged.

## 1.0.2

- Python 3.9 or later. 1.0.1 declared 3.8, on which it failed to import.
- Packaging moves to `pyproject.toml`; `setup.py` is removed. The package
  itself is unchanged.

## 1.0.1

- Search by name and by username.

## 1.0.0

- Search by email address and by phone number, and list the supported networks.
