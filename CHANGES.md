## Summary of Improvements

This document outlines the changes and additions I made to the `predictasearch-python` project.

Hopefully these changes are helpful to other users and contributors :)

---

## Added CLI Support

- Implemented a command-line interface using `click` (with `rich_click` for styled help output).
- Added the following commands:
  - `email <address>` — Search using an email.
  - `phone <number>` — Search using a phone number.
  - `networks` — List all supported networks.
- Included global options:
  - `--filter` — Limit searches to specific networks (e.g., `--filter facebook,linkedin`).
  - `--pretty` — Return results in raw JSON instead of styled tree format.

---

## Restructured Codebase

- Split the code into private modules:
  - `__api.py` — PredictaSearch API client.
  - `__cli.py` — CLI commands and logic.
  - `__lib.py` — Utility functions (e.g., rendering and argument parsing).
  - `__init__.py` — Clean import access.

---

## Rich Output (Optional)

- Added a tree-style renderer using `rich.tree` for better readability of nested results.
- Automatically detects list or dict responses.
- Keeps descriptions readable by printing them last.
- The goal was to present data clearly without overwhelming the user.

---
## Testing Setup

- Added basic tests to validate the behavior of email and phone searches as well as network listings.
- Used mocked responses based on documented examples from the PredictaSearch API — so no real API key is required to run them.
- Tests focus on verifying parsing, formatting, and CLI behavior with various inputs.

This should make it easier to test contributions locally and keep things stable even without live API access.

---

## Docker/Podman Support

- Added a `Dockerfile` so the CLI can be run in a container.
- Included example aliases for Docker/Podman so you can run it like a local command:
  ```bash
  alias predictasearch="podman run predictasearch -it"
