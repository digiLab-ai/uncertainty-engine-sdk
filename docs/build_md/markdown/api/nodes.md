# Base

### *class* uncertainty_engine.nodes.base.Node(node_name: str, label: str | None = None, client: Client | None = None, \*\*kwargs: Any)

Bases: `object`

A generic representation of a node in the Uncertainty Engine.

* **Parameters:**
  * **node_name** – The name of the node.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.
  * **\*\*kwargs** – Arbitrary keyword arguments representing the input
    parameters of the node.

### Example

```pycon
>>> client = Client()
>>> add_node = Node(
...     node_name="Add",
...     lhs=1,
...     rhs=2,
...     client=client,
... )
>>> add_node()
('Add', {'lhs': 1, 'rhs': 2})
```

#### add_tool_input(handle_name: str, node_info: NodeInfo) → None

Mark an input on a node as to be used as a tool input

* **Parameters:**
  * **handle_name** – The name of the handle (input) to mark as a tool input
  * **node_info** – The NodeInfo of the node
* **Raises:**
  **KeyError** – If the handle_name does not exist on the inputs of the node

Example:
>>> add_node = Add(
…     label=”Add node”,
…     lhs=1,
…     rhs=2,
… )
>>> add_node_info = client.get_node_info(“Add”)
>>> add_node.add_tool_input(“lhs”, add_node_info)

#### add_tool_output(handle_name: str, node_info: NodeInfo) → None

Mark an output on a node as to be used as a tool output

* **Parameters:**
  * **handle_name** – The name of the handle (output) to mark as a tool output
  * **node_info** – The NodeInfo of the node
* **Raises:**
  **KeyError** – If the handle_name does not exist on the outputs of the node

Example:
>>> add_node = Add(
…     label=”Add node”,
…     lhs=1,
…     rhs=2,
… )
>>> add_node_info = client.get_node_info(“Add”)
>>> add_node.add_tool_output(“ans”, add_node_info)

#### client

The Uncertainty Engine client.

#### label

A human-readable label for the node.

#### make_handle(output_name: str) → Handle

Make a handle for the output of the node.

* **Parameters:**
  **output_name** – The name of the output.
* **Returns:**
  A string handle for the output.

#### node_info

The node information. This includes the input parameters.

#### node_name

The name of the node.

#### tool_metadata *: ToolMetadata*

The node input and output handles to be used as tools.

#### validate() → None

Validates the node parameters are correct according to the
node_info. The following checks are made:

- Check all required inputs are assigned a value or handle.
- Check all the given input names exist in the node info.

The error messages are collected and then re-raised once the
all checks have finished.

* **Raises:**
  * **ValueError** – If self.node_info is None.
  * **NodeValidationError** – If validation fails. The error message
        will contain reasons for failure.

# Resource Management

### *class* uncertainty_engine.nodes.resource_management.Download(file: S3Storage | Handle, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Download a resource from the Uncertainty Engine resource management
system.

Note that this is for downloading resources that are output by a
node.

* **Parameters:**
  * **file** – The ID of the file to download.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file *: S3Storage | Handle*

The ID of the file to download.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'Download'*

The node ID.

### *class* uncertainty_engine.nodes.resource_management.LoadChatHistory(project_id: str, file_id: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Load a chat history from the Uncertainty Engine resource management
system.

* **Parameters:**
  * **project_id** – The ID of the project containing the chat history.
  * **file_id** – The ID of the chat history file to load.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file_id *: dict[str, str]*

The ID of the chat history to load, as a serialised ResourceID.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'LoadChatHistory'*

The node ID.

#### project_id *: str*

The ID of the project containing the chat history.

### *class* uncertainty_engine.nodes.resource_management.LoadDataset(project_id: str, file_id: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Load a dataset from the Uncertainty Engine resource management
system.

* **Parameters:**
  * **project_id** – The ID of the project containing the dataset.
  * **file_id** – The ID of the dataset file to load.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file_id *: dict[str, str]*

The ID of the dataset to load, as a serialised ResourceID.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'LoadDataset'*

The node ID.

#### project_id *: str*

The ID of the project containing the dataset.

### *class* uncertainty_engine.nodes.resource_management.LoadDocument(project_id: str, file_id: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Load a document from the Uncertainty Engine resource management
system.

* **Parameters:**
  * **project_id** – The ID of the project containing the document.
  * **file_id** – The ID of the document file to load.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file_id *: dict[str, str]*

The ID of the document to load, as a serialised ResourceID.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'LoadDocument'*

The node ID.

#### project_id *: str*

The ID of the project containing the document.

### *class* uncertainty_engine.nodes.resource_management.LoadModel(project_id: str, file_id: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Load a model from the Uncertainty Engine resource management system.

* **Parameters:**
  * **project_id** – The ID of the project.
  * **file_id** – The ID of the model to load.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file_id *: dict[str, str]*

The ID of the model to load, as a serialised ResourceID.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'LoadModel'*

The node ID.

#### project_id *: str*

The ID of the project containing the model.

### *class* uncertainty_engine.nodes.resource_management.LoadMultiple(project_id: str, file_ids: list[str], file_type: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Load multiple datasets, models, chat histories or documents from the
Uncertainty Engine resource management system.

* **Parameters:**
  * **project_id** – The ID of the project.
  * **file_ids** – List of File IDs of the files to load.
  * **file_type** – The type of resource to load. One of ‘dataset’,
    ‘model’, ‘chat_history’, or ‘document’.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### file_ids *: list[dict[str, str]]*

The IDs of the resources to load, as serialised 

```
`
```

ResourceID\`s.

#### file_type *: str*

The type of resource to load. One of ‘dataset’, ‘model’,
‘chat_history’, or ‘document’.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'LoadMultiple'*

The node ID.

#### project_id *: str*

The ID of the project containing the resources.

### *class* uncertainty_engine.nodes.resource_management.Save(data: S3Storage | Handle, file_name: str, project_id: str, label: str | None = None, client: Client | None = None)

Bases: [`Node`](#uncertainty_engine.nodes.base.Node)

Save a resource in the Uncertainty Engine resource management
system.

Note that this is for saving resources that are output by a node.
If you wish to upload a file to use in your workflow then you should
use the resource provider (use client.resources.upload() to upload
a local resource to the Uncertainty Engine).

* **Parameters:**
  * **data** – A reference to the node output data to be saved.
  * **file_id** – The human-readable name for the saved resource. If a
    resource of the same type and name already exists, the save node
    will create a new version of that existing resource.
  * **project_id** – The ID of the project to save to.
  * **label** – A human-readable label for the node. Defaults to None.
  * **client** – An (optional) instance of the client being used. This is
    required for performing validation.

#### data *: S3Storage | Handle*

A reference to the node output data to be saved.

#### file_id *: str*

The human-readable name for the saved resource. If a resource of the
same type and name already exists, the save node will create a new
version of that existing resource.

#### label *: str | None*

A human-readable label for the node. This should be unique to all
other node labels in a workflow.

#### node_name *: str* *= 'Save'*

The node ID.

#### project_id *: str*

The ID of the project to save to.
