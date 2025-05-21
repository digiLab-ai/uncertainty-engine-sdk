# Uncertainty Engine SDK Examples

This directory contains example notebooks demonstrating the core functionality of the Uncertainty Engine Python SDK.

## Prerequisites

You will need to have a valid Uncertainty Engine account and deployment URL (these are used to configure the Uncertainty Engine client).

Before running any examples, install the SDK with the required extras:

```bash
pip install "uncertainty_engine[vis,notebook,data]"
```

Or, if installing from source using Poetry:

```bash
poetry install --extras "vis notebook data"
```

## Available Examples

1. **Basic Node Usage** ([demo_node.ipynb](./demo_node.ipynb))

   Learn the fundamentals of working with nodes in the Uncertainty Engine:

   - Setting up the Client
   - Listing available nodes
   - Executing basic node operations
   - Understanding node responses

2. **Building Workflows** ([demo_workflow.ipynb](./demo_workflow.ipynb))

   Discover how to create and execute workflows:

   - Constructing workflows
   - Connecting nodes together
   - Defining inputs and outputs
   - Visualising workflows
   - Executing multi-node workflows

3. **Model Training & Prediction** ([demo_train_predict.ipynb](./demo_train_predict.ipynb))

   A practical example showing how to:

   - Train a machine learning model
   - Make predictions on new data
   - Download your results
   - Visualise results

## Getting Started

You will need to make sure you have all the [prerequisites](#prerequisites) above before following these steps. Then, within your Jupyter Notebook you can start defining nodes as follows:

1. **Configure Your Client**

   ```python
   from uncertainty_engine.client import Client

   client = Client(
       email="<you-email>",  # Note: There must be token associated with this email.
       deployment="<a-deployment-url>",
   )
   ```

2. **Create Your First Node**

   There are two ways to create nodes:

   Using a specific node class (note that these only exist for `Add`, `Workflow` and the `SensorDesigner` nodes for now), of which the attributes are the input parameters of the node as well an optional attribute for the `label`:

   ```python
   from uncertainty_engine.nodes.basic import Add

   add_node = Add(lhs=1, rhs=2)
   result = client.run_node(add_node)
   ```

   Using the generic Node class which has the following attributes:

   - `node_name`: The name of the node.
   - `label`: A human-readable label for the node. Defaults to None.
   - `**kwargs`: Keyword arguments representing the input parameters of the node.

   ```python
   from uncertainty_engine.nodes.base import Node

   add_node = Node(
       node_name="Add",
       label="My Addition",
       lhs=1,
       rhs=2
   )
   result = client.run_node(add_node)
   ```

3. Start with [`demo_node.ipynb`](./demo_node.ipynb) to learn the basics
4. Progress to more complex examples as needed
