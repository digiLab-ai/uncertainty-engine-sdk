# WorkflowRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 
**owner_id** | **str** |  | 
**versions** | **List[str]** |  | [optional] [default to []]
**created_at** | **datetime** |  | [optional] 
**is_locked** | **bool** |  | [optional] [default to False]

## Example

```python
from resource_api.models.workflow_record_output import WorkflowRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowRecordOutput from a JSON string
workflow_record_output_instance = WorkflowRecordOutput.from_json(json)
# print the JSON string representation of the object
print(WorkflowRecordOutput.to_json())

# convert the object into a dict
workflow_record_output_dict = workflow_record_output_instance.to_dict()
# create an instance of WorkflowRecordOutput from a dict
workflow_record_output_from_dict = WorkflowRecordOutput.from_dict(workflow_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


