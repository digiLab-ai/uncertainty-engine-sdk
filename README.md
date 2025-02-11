<div style="color: black; background-color: #edf497;">
    <img src="./assets/images/uncertainty-engine-logo.png">
</div>

# Python SDK for the Uncertainty Engine

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

# Run the node on the server
response = client.run_node(add)

# Get the result
result = response["output"]

pprint(result)
```

For more some more in-depth examples checkout our [example notebooks](https://github.com/digiLab-ai/uncertainty-engine-sdk/tree/dev/examples).
