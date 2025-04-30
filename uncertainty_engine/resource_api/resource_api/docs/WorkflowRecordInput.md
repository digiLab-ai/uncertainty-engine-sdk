# WorkflowRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**name** | **str** |  | 
**project_id** | **object** |  | [optional] 
**owner_id** | **object** |  | 
**versions** | **List[object]** |  | [optional] [default to []]
**created_at** | **datetime** |  | [optional] 
**is_locked** | **bool** |  | [optional] [default to False]

## Example

```python
from resource_api.models.workflow_record_input import WorkflowRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowRecordInput from a JSON string
workflow_record_input_instance = WorkflowRecordInput.from_json(json)
# print the JSON string representation of the object
print(WorkflowRecordInput.to_json())

# convert the object into a dict
workflow_record_input_dict = workflow_record_input_instance.to_dict()
# create an instance of WorkflowRecordInput from a dict
workflow_record_input_from_dict = WorkflowRecordInput.from_dict(workflow_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


