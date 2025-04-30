# PostWorkflowTemplateRecordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_template_record** | [**WorkflowTemplateRecordInput**](WorkflowTemplateRecordInput.md) |  | 
**workflow_template** | **object** |  | 

## Example

```python
from resource_api.models.post_workflow_template_record_request import PostWorkflowTemplateRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkflowTemplateRecordRequest from a JSON string
post_workflow_template_record_request_instance = PostWorkflowTemplateRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PostWorkflowTemplateRecordRequest.to_json())

# convert the object into a dict
post_workflow_template_record_request_dict = post_workflow_template_record_request_instance.to_dict()
# create an instance of PostWorkflowTemplateRecordRequest from a dict
post_workflow_template_record_request_from_dict = PostWorkflowTemplateRecordRequest.from_dict(post_workflow_template_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


