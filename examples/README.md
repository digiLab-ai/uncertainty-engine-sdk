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

1. **Basic Usage** ([demo_add.ipynb](./demo_add.ipynb))

   Learn the fundamentals of working the Uncertainty Engine:

   - Setting up the Client
   - Listing available nodes
   - Executing basic node operations (using the add node)

2. **Basic Node Usage** ([demo_node.ipynb](./demo_node.ipynb))

   Learn the fundamentals of working with nodes in the Uncertainty Engine:

   - Creating any type of node
   - Executing nodes
   - Understanding node responses

3. **Building Workflows** ([demo_workflow.ipynb](./demo_workflow.ipynb))

   Discover how to create and execute workflows:

   - Constructing workflows
   - Connecting nodes together
   - Defining inputs and outputs
   - Visualising workflows
   - Executing multi-node workflows

4. **Model Training & Prediction** ([demo_train_predict.ipynb](./demo_train_predict.ipynb))

   A practical example showing how to:

   - Train a machine learning model
   - Make predictions on new data
   - Download your results
   - Visualise results

5. **Handling Resources** ([demo_resource.ipynb](./demo_resource.ipynb))

   Learn how to manage resources in the Uncertainty Engine:

   - Authenticate your account
   - Upload files as resources
   - View available resources
   - Download resources
   - Work with projects

## Basic Usage

You will need to make sure you have all the [prerequisites](#prerequisites) above before following these steps. Then, within your Jupyter Notebook you can start defining nodes as follows:

1. **Configure Your Client**

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
    ```

1. **Setting Your Username and Password**

   To run and queue workflows you must have your Uncertainty Engine username and password set up. To do this you can run the following in your terminal:

    ```bash
    export UE_USERNAME="your_username"
    export UE_PASSWORD="your_password"
    ```

1. **Create Your First Node**

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

1. **Run Your First Node**

   Run your node and view your results.

   ```python
   response = client.run_node(add)
   result = response["output"]

   pprint(result)
   ```

1. Start with [`demo_node.ipynb`](./demo_node.ipynb) to learn the basics
1. Progress to more complex examples as needed
