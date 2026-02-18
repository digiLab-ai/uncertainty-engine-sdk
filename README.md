![Uncertainty Engine banner](https://github.com/digiLab-ai/uncertainty-engine-types/raw/main/assets/images/uncertainty-engine-logo.png)

# Python SDK for the Uncertainty Engine

[![PyPI](https://badge.fury.io/py/uncertainty-engine.svg)](https://badge.fury.io/py/uncertainty-engine) [![Python Versions](https://img.shields.io/pypi/pyversions/uncertainty-engine.svg)](https://pypi.org/project/uncertainty-engine/)

> ⚠️ **Pre-Release Notice:** This SDK is currently in pre-release development. Please ensure you are reading documentation that corresponds to the specific version of the SDK you have installed, as features and APIs may change between versions.

## Requirements

- Python >=3.10, <3.13
- Valid Uncertainty Engine account

## Installation

```bash
pip install uncertainty-engine
```

With optional dependencies:

```bash
pip install "uncertainty_engine[vis,notebook,data]"
```

## Usage

### Setting your username and password

To run and queue workflows you must have your Uncertainty Engine username and password set up. To do this you can run the following in your terminal:

```bash
export UE_USERNAME="your_username"
export UE_PASSWORD="your_password"
```

### Creating a client

All interactions with the Uncertainty Engine API are performed via a `Client`. The client can be defined as follows:

```python
from uncertainty_engine import Client

client = Client()
```

With an instantiated `Client` object, and username and password set as environmental variables, authentication can be carried via the following:

```
client.authenticate()
```

### Running a node

```python
from pprint import pprint

from uncertainty_engine import Client, Environment
from uncertainty_engine.nodes.basic import Add

# Set up the client
client = Client()
client.authenticate()

# Create a node
add = Add(lhs=1, rhs=2)

# Run the node on the server
response = client.run_node(add)

# Get the result
result = response.outputs

pprint(result)
```

For more some more in-depth examples checkout our [example notebooks](https://github.com/digiLab-ai/uncertainty-engine-sdk/tree/main/examples).
