# WorkflowVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_version_record** | [**WorkflowVersionRecordOutput**](WorkflowVersionRecordOutput.md) |  | 
**workflow** | **object** |  | 

## Example

```python
from resource_api.models.workflow_version_response import WorkflowVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowVersionResponse from a JSON string
workflow_version_response_instance = WorkflowVersionResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowVersionResponse.to_json())

# convert the object into a dict
workflow_version_response_dict = workflow_version_response_instance.to_dict()
# create an instance of WorkflowVersionResponse from a dict
workflow_version_response_from_dict = WorkflowVersionResponse.from_dict(workflow_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


