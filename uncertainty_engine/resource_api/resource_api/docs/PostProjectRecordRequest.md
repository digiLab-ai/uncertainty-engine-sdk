# PostProjectRecordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_record** | [**ProjectRecordInput**](ProjectRecordInput.md) |  | 

## Example

```python
from resource_api.models.post_project_record_request import PostProjectRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostProjectRecordRequest from a JSON string
post_project_record_request_instance = PostProjectRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PostProjectRecordRequest.to_json())

# convert the object into a dict
post_project_record_request_dict = post_project_record_request_instance.to_dict()
# create an instance of PostProjectRecordRequest from a dict
post_project_record_request_from_dict = PostProjectRecordRequest.from_dict(post_project_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


