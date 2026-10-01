# Uncertainty Engine SDK Examples

This directory contains example notebooks demonstrating the core functionality of the Uncertainty Engine Python SDK.

## Prerequisites

Follow the instructions in [README.md](../README.md) to install and configure the SDK.

For these examples, install the SDK with all of its optional extras.

## Available Examples

1. **Basic Usage** ([add.ipynb](./add.ipynb))

   Learn the fundamentals of working the Uncertainty Engine:

   - Setting up the Client
   - Listing available nodes
   - Executing basic node operations (using the add node)

2. **Basic Node Usage** ([node.ipynb](./node.ipynb))

   Learn the fundamentals of working with nodes in the Uncertainty Engine:

   - Creating any type of node
   - Executing nodes
   - Understanding node responses

3. **Building Workflows** ([workflow.ipynb](./workflow.ipynb))

   Discover how to create and execute workflows:

   - Constructing workflows
   - Connecting nodes together
   - Defining inputs and outputs
   - Visualising workflows
   - Executing multi-node workflows

4. **Model Training & Prediction** ([train_predict.ipynb](./train_predict.ipynb))

   A practical example showing how to:

   - Train a machine learning model
   - Make predictions on new data
   - Download your results
   - Visualise results

5. **Handling Resources** ([resource.ipynb](./resource.ipynb))

   Learn how to manage resources in the Uncertainty Engine:

   - Authenticate your account
   - Upload files as resources
   - View available resources
   - Download resources
   - Work with projects

6. **Building Nodes with `client.nodes`** ([dynamic_nodes.ipynb](./dynamic_nodes.ipynb))

   Learn how to find, inspect and build any node from the registry:

   - Discovering nodes and inspecting their inputs and outputs
   - Building nodes, and the errors you get as you build them
   - Building a specific version, or pinning versions for several nodes
   - Wiring dynamically built nodes into a workflow
   - Passing structured inputs, such as resource IDs
   - Caching, and picking up newly deployed nodes
