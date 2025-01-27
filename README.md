# SDK for the Uncertainty Engine

## Basic usage
 ```python
from pprint import pprint

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.demo import Add

# Set up the client
client = Client(
    email="<user-email>",  # Must have tokens!
    deployment="<uncertainty-engine-api-url>",
)

# Create a node
add = Add(lhs=1, rhs=2)

# Queue the node for execution and wait for it to run
response = client.queue_node(add, wait=True)

# Get the result
result = response["output"]

pprint(result)
```