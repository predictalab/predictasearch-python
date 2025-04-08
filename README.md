# predictasearch: The official Python library and CLI for Predicta Search
predictasearch is a Python library that interacts with the PredictaSearch API to perform searches on emails and phone numbers, as well as retrieve the list of supported networks.

## Features
- Search by email address
- Search by phone number
- Retrieve the list of supported networks

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
```
Grab your API key from https://www.predictasearch.com/

## Installation
To install the Predicta Search library, simply:
```bash
pip install predictasearch
```

## Documentation
Documentation is available at https://dev.predictasearch.com/redoc