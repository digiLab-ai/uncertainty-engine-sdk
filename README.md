![Uncertainty Engine banner](https://github.com/digiLab-ai/uncertainty-engine-types/raw/main/assets/images/uncertainty-engine-logo.png)

# Python SDK for the Uncertainty Engine

[![PyPI](https://badge.fury.io/py/uncertainty-engine.svg)](https://badge.fury.io/py/uncertainty-engine) [![Python Versions](https://img.shields.io/pypi/pyversions/uncertainty-engine.svg)](https://pypi.org/project/uncertainty-engine/)

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

### Creating a client

All interactions with the Uncertainty Engine API are performed via a `Client`.

To create a `Client` for a named environment:

```python
from uncertainty_engine import Client

client = Client(env="<NAME>")

# For example:
client = Client(env="dev")
```

To create a `Client` for a custom environment:

```python
from uncertainty_engine import Client, Environment

client = Client(
   env=Environment(
        cognito_user_pool_client_id="<COGNITO USER POOL APPLICATION CLIENT ID>",
        core_api="<UNCERTAINTY ENGINE CORE API URL>",
        region="<REGION>",
        resource_api="<UNCERTAINTY ENGINE RESOURCE SERVICE API URL>",
   ),
)

# For example:
client = Client(
   env=Environment(
        cognito_user_pool_client_id="3n437fei4uhp4ouj8b4mmt09l9",
        core_api="https://s0r8fczyag.execute-api.eu-west-2.amazonaws.com",
        region="eu-west-2",
        resource_api="https://hmqdnx48x6.execute-api.eu-west-2.amazonaws.com",
   ),
)
```

### Running a node

```python
from pprint import pprint

from uncertainty_engine import Client, Environment
from uncertainty_engine.nodes.demo import Add

# Set up the client
client = Client(
   env=Environment(
        cognito_user_pool_client_id="<COGNITO USER POOL APPLICATION CLIENT ID>",
        core_api="<UNCERTAINTY ENGINE CORE API URL>",
        region="<REGION>",
        resource_api="<UNCERTAINTY ENGINE RESOURCE SERVICE API URL>",
   ),
)

# Create a node
add = Add(lhs=1, rhs=2)

# Run the node on the server
response = client.run_node(add)

# Get the result
result = response["output"]

pprint(result)
```

For more some more in-depth examples checkout our [example notebooks](https://github.com/digiLab-ai/uncertainty-engine-sdk/tree/dev/examples).

## Support

For any support needs please visit our [support page](https://support.uncertaintyengine.ai).
