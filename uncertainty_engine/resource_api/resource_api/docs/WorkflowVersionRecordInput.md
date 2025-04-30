# WorkflowVersionRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**name** | **str** |  | 
**project_id** | **object** |  | [optional] 
**workflow_id** | **object** |  | [optional] 
**owner_id** | **object** |  | 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**location** | [**ResourceLocation**](ResourceLocation.md) |  | [optional] 

## Example

```python
from resource_api.models.workflow_version_record_input import WorkflowVersionRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowVersionRecordInput from a JSON string
workflow_version_record_input_instance = WorkflowVersionRecordInput.from_json(json)
# print the JSON string representation of the object
print(WorkflowVersionRecordInput.to_json())

# convert the object into a dict
workflow_version_record_input_dict = workflow_version_record_input_instance.to_dict()
# create an instance of WorkflowVersionRecordInput from a dict
workflow_version_record_input_from_dict = WorkflowVersionRecordInput.from_dict(workflow_version_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


