### *class* uncertainty_engine.client.Client(env: Environment | str = 'prod')

Bases: `object`

#### auth

Resource Service Authorisation API client.

#### authenticate(account_id: str | None = None) → None

Authenticate the user with the Uncertainty Engine.

* **Parameters:**
  **account_id** – **DEPRECATED** This parameter is no longer used
  and will be removed in the next release. Defaults to
  None. The account ID is now obtained from HTTP
  headers.

#### core_api *: ApiInvoker*

Core API interaction.

#### *property* email *: str*

The user’s username, which is expected to be their email address.

* **Raises:**
  **IncompleteCredentials** – Raised if the UE_USERNAME environment
      variable is not set.

#### env

Uncertainty Engine environment.

#### get_node_info(node: str) → NodeInfo

Get information about a specific node.

* **Parameters:**
  **node** – The ID of the node to get information about.
* **Returns:**
  Information about the node as a NodeInfo object.
* **Raises:**
  **HTTPError** – If the node does not exist (404) or another
      HTTP error occurs.

#### job_status(job: Job) → JobInfo

Check the status of a job.

* **Parameters:**
  **job** – The job to check.
* **Returns:**
  A JobInfo object containing the response data of the job.
  .. rubric:: Example

  JobInfo(
  status=<JobStatus.COMPLETED: ‘completed’>,
  message=’Job completed at 2025-07-23 09:10:59.146669’,
  inputs={‘lhs’: 1, ‘rhs’: 2},
  outputs={‘ans’: 3.0}
  )

#### list_nodes(category: str | None = None) → list

List all available nodes in the specified deployment.

* **Parameters:**
  **category** – The category of nodes to list. If not specified, all nodes are listed.
  Defaults to `None`.
* **Returns:**
  List of available nodes. Each list item is a dictionary of information about the node.

#### queue_node(node: str | [Node](nodes.md#uncertainty_engine.nodes.base.Node), inputs: dict[str, Any] | None = None, input: dict[str, Any] | None = None) → Job

Queue a node for execution.

* **Parameters:**
  * **node** – The name of the node to execute or the node object itself.
  * **inputs** – The input data for the node. If the node is defined by its name,
    this is required. Defaults to `None`.
  * **input** – **DEPRECATED** The input data for the node. Use inputs instead.
    Will be removed in a future version.
* **Returns:**
  A Job object representing the queued job.

#### queue_workflow(project_id: str, workflow_id: str, inputs: list[OverrideWorkflowInput] | list[dict[str, Any]] | None = None, outputs: list[OverrideWorkflowOutput] | list[dict[str, Any]] | None = None) → Job

Queue a workflow for execution

* **Parameters:**
  * **project_id** – The ID of the project where the workflow is saved
  * **workflow_id** – The ID of the workflow you want to run
  * **inputs** – Optional list of inputs to override within the workflow
  * **outputs** – Optional list of outputs to override. If passed previous outputs are overridden
* **Returns:**
  A Job object representing the queued job.

### Example

```pycon
>>> # Basic workflow execution
>>> job = client.queue_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id"
... )
```

```pycon
>>> # With input overrides
>>> override_inputs = [
...     OverrideWorkflowInput(
...         node_label="input_node_label",
...         input_handle="input_parameter_name",
...         value="new_value"
...     )
... ]
>>> job = client.queue_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id",
...     inputs=override_inputs
... )
```

```pycon
>>> # With output overrides
>>> override_outputs = [
...     OverrideWorkflowOutput(
...         node_label="output_node_label",
...         output_handle="output_parameter_name",
...         output_label="custom_output_name"
...     )
... ]
>>> job = client.queue_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id",
...     outputs=override_outputs
... )
```

#### run_node(node: str | [Node](nodes.md#uncertainty_engine.nodes.base.Node), inputs: dict[str, Any] | None = None, input: dict[str, Any] | None = None) → JobInfo

Run a node synchronously.

* **Parameters:**
  * **node** – The name of the node to execute or the node object itself.
  * **inputs** – The input data for the node. If the node is defined by its name,
    this is required. Defaults to `None`.
  * **input** – **DEPRECATED** The input data for the node. Use inputs instead.
    Will be removed in a future version.
* **Returns:**
  A JobInfo object containing the response data of the job.

#### run_workflow(project_id: str, workflow_id: str, inputs: list[OverrideWorkflowInput] | list[dict[str, Any]] | None = None, outputs: list[OverrideWorkflowOutput] | list[dict[str, Any]] | None = None) → JobInfo

Run a workflow synchronously.

* **Parameters:**
  * **project_id** – The ID of the project where the workflow is saved
  * **workflow_id** – The ID of the workflow you want to run
  * **inputs** – Optional list of inputs to override within the workflow
  * **outputs** – Optional list of outputs to override. If passed previous outputs are overridden
* **Returns:**
  A JobInfo object containing the response data of the job.

### Example

```pycon
>>> # Basic workflow execution
>>> job_info = client.run_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id"
... )
```

```pycon
>>> # With input overrides
>>> override_inputs = [
...     OverrideWorkflowInput(
...         node_label="input_node_label",
...         input_handle="input_parameter_name",
...         value="new_value"
...     )
... ]
>>> job_info = client.run_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id",
...     inputs=override_inputs
... )
```

```pycon
>>> # With output overrides
>>> override_outputs = [
...     OverrideWorkflowOutput(
...         node_label="output_node_label",
...         output_handle="output_parameter_name",
...         output_label="custom_output_name"
...     )
... ]
>>> job_info = client.run_workflow(
...     project_id="your_project_id",
...     workflow_id="your_workflow_id",
...     outputs=override_outputs
... )
```

#### view_tokens() → int

View the number of tokens currently available to the user’s
organisation.

* **Returns:**
  The number of tokens currently available to the user’s
  organisation.
