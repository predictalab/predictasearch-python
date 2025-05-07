# predictasearch: The official Python library and CLI for Predicta Search
predictasearch is a Python library that interacts with the PredictaSearch API to perform searches on emails and phone numbers, as well as retrieve the list of supported networks.

## Features
- Search by email address
- Search by phone number
- Retrieve the list of supported networks

## Quick Start

### Implementation
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
```

### Command-Line Utility

#### Search by email
```commandline
predictasearch email johndoe@gmail.com
```

#### Search by phone
```commandline
predictasearch phone +1234567890
```

#### Filter Search by Networks
```commandline
predictasearch email johndoe@gmail.com --filter facebook,linkedin
```

or 

```commandline
predictasearch phone +1234567890 --filter facebook,tiktok
```

#### List Supported Networks
```commandline
predictasearch networks
```

> The cli utility will read the API key from the PREDICTA_API_KEY environment variable, so ensure that is set before running any queries.
***
Grab your API key from https://www.predictasearch.com/

## Installation
### PyPI Package
To install the Predicta Search library, simply:
```bash
pip install predictasearch
```

### Build Docker Container
To build the Docker Container, run:
```commandline
docker build -t predictasearch .
```

**Tip**:
For non-Windows users, instead of running the container with `docker run` or `podman run` everytime, you can instead create an alias for the container CLI by running:
#### for Docker
```commandline 
alias predictasearch="docker run --rm -it -e PREDICTA_API_KEY=\$PREDICTA_API_KEY predictasearch"
```

#### for Podman
```commandline 
alias predictasearch="podman run --rm -it -e PREDICTA_API_KEY=\$PREDICTA_API_KEY predictasearch"
```

This will allow you to run the container by calling `predictasearch`
## Testing
To run the test suite:
```commandline
pip install .[dev]
pytest
```

> Tests are located in the tests/ directory and use pytest with mocked HTTP requests.
>> No real API key or live requests are required.

## Documentation
Documentation is available at https://dev.predictasearch.com/redoc