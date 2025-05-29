![Uncertainty Engine banner](https://github.com/digiLab-ai/uncertainty-engine-types/raw/main/assets/images/uncertainty-engine-logo.png)

# Python SDK for the Uncertainty Engine

## Basic usage

```python
from pprint import pprint

from uncertainty_engine import Client, Environment
from uncertainty_engine.nodes.demo import Add

# Set up the client
client = Client(
   email="<user-email>",  # Must have tokens!
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
