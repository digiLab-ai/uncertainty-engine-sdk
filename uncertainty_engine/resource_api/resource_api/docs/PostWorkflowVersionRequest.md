# PostWorkflowVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_version_record** | [**WorkflowVersionRecordInput**](WorkflowVersionRecordInput.md) |  | 
**workflow** | **object** |  | 

## Example

```python
from resource_api.models.post_workflow_version_request import PostWorkflowVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkflowVersionRequest from a JSON string
post_workflow_version_request_instance = PostWorkflowVersionRequest.from_json(json)
# print the JSON string representation of the object
print(PostWorkflowVersionRequest.to_json())

# convert the object into a dict
post_workflow_version_request_dict = post_workflow_version_request_instance.to_dict()
# create an instance of PostWorkflowVersionRequest from a dict
post_workflow_version_request_from_dict = PostWorkflowVersionRequest.from_dict(post_workflow_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


