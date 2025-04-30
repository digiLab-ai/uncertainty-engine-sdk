# WorkflowVersionRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 
**workflow_id** | **str** |  | [optional] 
**owner_id** | **str** |  | 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**location** | [**ResourceLocation**](ResourceLocation.md) |  | [optional] 

## Example

```python
from resource_api.models.workflow_version_record_output import WorkflowVersionRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowVersionRecordOutput from a JSON string
workflow_version_record_output_instance = WorkflowVersionRecordOutput.from_json(json)
# print the JSON string representation of the object
print(WorkflowVersionRecordOutput.to_json())

# convert the object into a dict
workflow_version_record_output_dict = workflow_version_record_output_instance.to_dict()
# create an instance of WorkflowVersionRecordOutput from a dict
workflow_version_record_output_from_dict = WorkflowVersionRecordOutput.from_dict(workflow_version_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


