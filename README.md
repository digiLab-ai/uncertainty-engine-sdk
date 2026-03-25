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

The SDK has optional extras that provide additional functionality:

| Name       | Description                             |
| ---------- | --------------------------------------- |
| `data`     | Installs data processing packages       |
| `notebook` | Installs support for Jupyter notebooks  |
| `vis`      | Installs support for visualising graphs |

Install one or more of these via `pip` by providing them as a comma-separated list:

```bash
pip install "uncertainty-engine[data,notebook,vis]"
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

### Using different environments

The `Client` defaults to using the Uncertainty Engine production environment. To use a different named environment, pass it as the `env` argument:

```python
client = Client(env="dev")
```

If a custom environment has been provided for you, pass an `Environment` that describes the details:

```python
from uncertainty_engine import Client, Environment

client = Client(
    env=Environment(
        cognito_user_pool_client_id="…",
        core_api="…",
        region="…",
        resource_api="…",
    ),
)
```

| Argument                      | Format                                        | Example                                                  |
| ----------------------------- | --------------------------------------------- | -------------------------------------------------------- |
| `cognito_user_pool_client_id` | Alphanumeric string                           | `3vj5pe253j4v070euqjdk38a24`                             |
| `core_api`                    | Starts with `https://`, does not end with `/` | `https://de1v75vvk6.execute-api.eu-west-2.amazonaws.com` |
| `region`                      | Geographic region code                        | `eu-west-2`                                              |
| `resource_api`                | Starts with `https://`, does not end with `/` | `https://m90q55iux6.execute-api.eu-west-2.amazonaws.com` |

**Note:** Every password is tied to a specific environment. A password for the production environment, for example, won't grant access to the development environment. Ensure you set the correct `UE_PASSWORD` value for the environment you configure.

### Troubleshooting

Authorisation tokens are cached in `.ue_auth` in your home directory. If the SDK fails to authenticate you (for example, after switching from one environment to another), delete `.ue_auth` to generate and cache new tokens.

To delete the cache in macOS or Linux:

```bash
rm ~/.ue_auth
```

To delete the cache in Windows:

```bat
del "%USERPROFILE%\.ue_auth"
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
