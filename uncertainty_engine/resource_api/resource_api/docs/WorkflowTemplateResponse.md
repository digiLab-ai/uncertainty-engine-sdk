# WorkflowTemplateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_template_record** | [**WorkflowTemplateRecordOutput**](WorkflowTemplateRecordOutput.md) |  | 
**workflow_template** | **object** |  | 

## Example

```python
from resource_api.models.workflow_template_response import WorkflowTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateResponse from a JSON string
workflow_template_response_instance = WorkflowTemplateResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateResponse.to_json())

# convert the object into a dict
workflow_template_response_dict = workflow_template_response_instance.to_dict()
# create an instance of WorkflowTemplateResponse from a dict
workflow_template_response_from_dict = WorkflowTemplateResponse.from_dict(workflow_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


