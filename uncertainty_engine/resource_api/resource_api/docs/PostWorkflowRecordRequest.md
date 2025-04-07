# PostWorkflowRecordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_record** | [**WorkflowRecordInput**](WorkflowRecordInput.md) |  | 

## Example

```python
from resource_api.models.post_workflow_record_request import PostWorkflowRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkflowRecordRequest from a JSON string
post_workflow_record_request_instance = PostWorkflowRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PostWorkflowRecordRequest.to_json())

# convert the object into a dict
post_workflow_record_request_dict = post_workflow_record_request_instance.to_dict()
# create an instance of PostWorkflowRecordRequest from a dict
post_workflow_record_request_from_dict = PostWorkflowRecordRequest.from_dict(post_workflow_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


