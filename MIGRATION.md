# Migrating from node classes to `client.nodes`

Earlier versions of the SDK had a Python class for each node, in `uncertainty_engine.nodes.basic`, `uncertainty_engine.nodes.machine_learning`, `uncertainty_engine.nodes.resource_management` and `uncertainty_engine.nodes.sensor_designer`. Those modules have been removed. Every node is now built through `client.nodes`, which looks the node up in the Uncertainty Engine when you use it.

`Workflow` (`uncertainty_engine.nodes.workflow`) and the generic `Node` (`uncertainty_engine.nodes.base`) are unchanged.

## Building nodes

Drop the import and build the node through the client, using the same name. There's no `client=` argument: `client.nodes` supplies it.

```python
# Before
from uncertainty_engine.nodes.basic import Add

add = Add(lhs=1, rhs=2, label="add", client=client)

# After
add = client.nodes.Add(lhs=1, rhs=2, label="add")
```

Every removed class has a node of the same name, so `X(...)` becomes `client.nodes.X(...)`:

| Removed module | Nodes |
| -------------- | ----- |
| `nodes.basic` | `Add` |
| `nodes.machine_learning` | `ExportTorchScript`, `ModelConfig`, `PredictModel`, `PredictPosteriorConditioning`, `Recommend`, `ScoreModel`, `TrainModel` |
| `nodes.resource_management` | `Download`, `LoadChatHistory`, `LoadDataset`, `LoadDocument`, `LoadModel`, `LoadMultiple`, `Save` |
| `nodes.sensor_designer` | `BuildSensorDesigner`, `ScoreSensorDesign`, `SuggestSensorDesign` |

## Versions

Every removed class was pinned to version `0.2.0`. `client.nodes` builds each node at the version the Uncertainty Engine considers its default, which may be newer and may behave differently. To keep the behaviour you had, pass `version`, or pin several nodes at once with `with_versions()`:

```python
add = client.nodes.Add(lhs=1, rhs=2, label="add", version="0.2.0")

pinned = client.nodes.with_versions(
    {"ModelConfig": "0.2.0", "TrainModel": "0.2.0", "PredictModel": "0.2.0"}
)
model_config = pinned.ModelConfig(label="Model Config")
```

For example, the latest `TrainModel` doesn't accept the configuration produced by the latest `ModelConfig`, so pin both, as [`examples/train_predict.ipynb`](./examples/train_predict.ipynb) does. `client.get_node_versions("TrainModel")` lists the versions available.

## Inputs the classes converted for you

`client.nodes` passes inputs exactly as the node declares them. A few classes converted an input for you, so you now pass the node's own shape.

**Resource IDs.** The load nodes take a resource ID as `{"id": ...}`, not a plain string:

```python
# Before
LoadDataset(project_id=project_id, file_id=dataset_id, label="x")

# After
client.nodes.LoadDataset(project_id=project_id, file_id={"id": dataset_id}, label="x")
```

The same applies to `LoadModel`, `LoadDocument` and `LoadChatHistory`, and to `LoadMultiple`, which takes `file_ids=[{"id": ...}, ...]`. A plain ID still builds, but the node rejects it when it runs.

**Datasets for `BuildSensorDesigner`.** `sensor_data` and `quantities_of_interest_data` take a CSV dataset, `{"csv": ...}`, not a dict of columns. `dict_to_csv_str` converts one:

```python
from uncertainty_engine.utils import dict_to_csv_str

client.nodes.BuildSensorDesigner(sensor_data={"csv": dict_to_csv_str(sensor_data)}, label="designer")
```

## Inputs the classes renamed

Use the node's own input names. `Save` took `file_name`, but the node's input is `file_id`:

```python
# Before
Save(data=..., project_id=project_id, file_name="my-model", label="save")

# After
client.nodes.Save(data=..., project_id=project_id, file_id="my-model", label="save")
```

`client.nodes` rejects an input name the node doesn't have when the node is built, so this fails straight away rather than when it runs. `client.nodes.describe("Save")` shows a node's real input names.

## Inspecting a node

`client.get_node_info()` needs a version. To inspect a node's default version, use `get_default_node_info()`:

```python
client.get_default_node_info("TrainModel")       # the default version
client.get_node_info("TrainModel", "0.2.0")      # a specific version
client.nodes.describe("TrainModel")              # the default, or a pinned version on a pinned view
```

## Finding nodes

Instead of browsing the class modules, ask the Uncertainty Engine:

```python
client.nodes.available()              # every node you can use
client.nodes.describe("Add")          # its description, inputs and outputs
client.nodes.describe("Add").inputs   # just the inputs it takes
client.nodes.describe("Add").outputs  # and what it produces
```

In Jupyter or IPython, type `client.nodes.` and press **Tab** to autocomplete node names.

See the [README](./README.md#building-nodes) and [`examples/dynamic_nodes.ipynb`](./examples/dynamic_nodes.ipynb) for more on `client.nodes`.
