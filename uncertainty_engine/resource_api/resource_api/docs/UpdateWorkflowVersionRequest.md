# UpdateWorkflowVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_version_record_updates** | **object** |  | [optional] 
**workflow** | **object** |  | [optional] 

## Example

```python
from resource_api.models.update_workflow_version_request import UpdateWorkflowVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateWorkflowVersionRequest from a JSON string
update_workflow_version_request_instance = UpdateWorkflowVersionRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateWorkflowVersionRequest.to_json())

# convert the object into a dict
update_workflow_version_request_dict = update_workflow_version_request_instance.to_dict()
# create an instance of UpdateWorkflowVersionRequest from a dict
update_workflow_version_request_from_dict = UpdateWorkflowVersionRequest.from_dict(update_workflow_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


