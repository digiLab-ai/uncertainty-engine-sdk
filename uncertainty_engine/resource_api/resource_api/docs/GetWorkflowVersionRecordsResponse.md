# GetWorkflowVersionRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_version_records** | [**List[WorkflowVersionRecordOutput]**](WorkflowVersionRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_workflow_version_records_response import GetWorkflowVersionRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowVersionRecordsResponse from a JSON string
get_workflow_version_records_response_instance = GetWorkflowVersionRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowVersionRecordsResponse.to_json())

# convert the object into a dict
get_workflow_version_records_response_dict = get_workflow_version_records_response_instance.to_dict()
# create an instance of GetWorkflowVersionRecordsResponse from a dict
get_workflow_version_records_response_from_dict = GetWorkflowVersionRecordsResponse.from_dict(get_workflow_version_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


