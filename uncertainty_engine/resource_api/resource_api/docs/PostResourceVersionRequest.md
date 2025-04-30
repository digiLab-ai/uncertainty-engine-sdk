# PostResourceVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_version_record** | [**ResourceVersionRecordInput**](ResourceVersionRecordInput.md) |  | 
**resource_file_extension** | **str** |  | 

## Example

```python
from resource_api.models.post_resource_version_request import PostResourceVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostResourceVersionRequest from a JSON string
post_resource_version_request_instance = PostResourceVersionRequest.from_json(json)
# print the JSON string representation of the object
print(PostResourceVersionRequest.to_json())

# convert the object into a dict
post_resource_version_request_dict = post_resource_version_request_instance.to_dict()
# create an instance of PostResourceVersionRequest from a dict
post_resource_version_request_from_dict = PostResourceVersionRequest.from_dict(post_resource_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


