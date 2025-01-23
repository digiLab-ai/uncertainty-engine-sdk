# SDK for the Uncertainty Engine

## Basic usage
 ```python
import time
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

# Queue the node for execution
job_id = client.queue_node(add)

# Wait for the job to complete
status = "STARTED"
while status not in ["SUCCESS", "FAILURE"]:
    response = client.job_status(job_id)
    status = response["status"]
    time.sleep(5)

# Get the result
result = response["output"]

pprint(result)
```