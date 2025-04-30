# GetWorkflowTemplateRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_template_records** | [**List[WorkflowTemplateRecordOutput]**](WorkflowTemplateRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_workflow_template_records_response import GetWorkflowTemplateRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowTemplateRecordsResponse from a JSON string
get_workflow_template_records_response_instance = GetWorkflowTemplateRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowTemplateRecordsResponse.to_json())

# convert the object into a dict
get_workflow_template_records_response_dict = get_workflow_template_records_response_instance.to_dict()
# create an instance of GetWorkflowTemplateRecordsResponse from a dict
get_workflow_template_records_response_from_dict = GetWorkflowTemplateRecordsResponse.from_dict(get_workflow_template_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


