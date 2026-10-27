# Changelog

## 2.0.0

### Breaking

- An error status raises an exception, a subclass of `PredictaSearchError`
  (`AuthenticationError`, `InsufficientCreditsError`, `RateLimitError`...).
  1.x returned the error body, `{"detail": ...}`, in place of the results.
- Python 3.9 or later. 1.x declared 3.8, on which it failed to import.
- `PredictaSearch.BASE_URL` and `PredictaSearch.headers` are removed; use the
  `base_url` argument.

### Added

- `search(query, query_type, networks=None)`, the method the `search_by_*` shortcuts call.
- `timeout`, `base_url` and `session` arguments.
- `credit_balance`, the balance read on the last response.
- One connection pool per client, and `with PredictaSearch(...) as client:` to close it.
- Type hints shipped with the package (`py.typed`): `QueryType`, `SearchResult`, `NetworkInfo`.

## 1.0.1

- Search by name and by username.

## 1.0.0

- Search by email address and by phone number, and list the supported networks.
