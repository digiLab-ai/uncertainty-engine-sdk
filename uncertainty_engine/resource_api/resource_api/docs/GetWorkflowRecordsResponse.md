# GetWorkflowRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_records** | [**List[WorkflowRecordOutput]**](WorkflowRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_workflow_records_response import GetWorkflowRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowRecordsResponse from a JSON string
get_workflow_records_response_instance = GetWorkflowRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowRecordsResponse.to_json())

# convert the object into a dict
get_workflow_records_response_dict = get_workflow_records_response_instance.to_dict()
# create an instance of GetWorkflowRecordsResponse from a dict
get_workflow_records_response_from_dict = GetWorkflowRecordsResponse.from_dict(get_workflow_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


