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

| Name       | Description                                               |
| ---------- | --------------------------------------------------------- |
| `data`     | Installs data processing packages                         |
| `notebook` | Installs support for running the SDK in Jupyter notebooks |
| `vis`      | Installs support for visualising graphs                   |

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

### Building nodes

Every node registered with the Uncertainty Engine can be built through `client.nodes`. There are no per-node classes to import: the SDK looks each node up when you use it, so new nodes, and nodes you register yourself, work straight away.

#### Finding nodes

```python
client.nodes.available()              # the names of every node you can use
client.nodes.describe("Add")          # a node's description, inputs and outputs
client.nodes.describe("Add").inputs   # just the inputs it takes
client.nodes.describe("Add").outputs  # and what it produces
```

In Jupyter or IPython you can also type `client.nodes.` and press **Tab** to autocomplete node names.

#### Building and running a node

```python
from pprint import pprint

add = client.nodes.Add(lhs=1, rhs=2, label="add")

response = client.run_node(add)
pprint(response.outputs)
```

If the node's name is in a variable, call `client.nodes` with it instead: `client.nodes("Add", lhs=1, rhs=2, label="add")`.

Inputs are checked against the node's schema as the node is built. A missing or unknown input raises a `NodeValidationError`, and a node that doesn't exist raises a `NodeNotFoundError`; both are in `uncertainty_engine.exceptions`. Inputs are passed exactly as the node declares them, so a node that takes a resource ID, for example, expects `{"id": ...}`.

#### Versions

By default a node is built at the version the Uncertainty Engine considers its default: `"latest"` if there is one, otherwise the highest version. To build a specific version, pass `version`, or pin several nodes at once with `with_versions()`:

```python
add = client.nodes.Add(lhs=1, rhs=2, label="add", version="0.2.0")

pinned = client.nodes.with_versions({"TrainModel": "0.2.0", "PredictModel": "0.2.0"})
train = pinned.TrainModel(...)  # built at 0.2.0; nodes not in the mapping use their default
```

`client.get_node_versions("Add")` lists the versions available.

#### Caching

A node's schema is fetched the first time you build it, then kept for the life of the client, as is the list from `available()`. To pick up a node or version deployed since, clear the cache:

```python
client.clear_node_cache()
```

See [`examples/dynamic_nodes.ipynb`](./examples/dynamic_nodes.ipynb) for a full walkthrough, and our [example notebooks](https://github.com/digiLab-ai/uncertainty-engine-sdk/tree/main/examples) for more in-depth examples.

### Upgrading from node classes

Earlier versions of the SDK had a Python class for each node, such as `from uncertainty_engine.nodes.basic import Add`. Those classes have been removed in favour of `client.nodes`; see [MIGRATION.md](./MIGRATION.md) for how to update your code.
