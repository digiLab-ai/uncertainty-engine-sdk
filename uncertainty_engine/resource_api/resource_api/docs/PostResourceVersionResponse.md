# PostResourceVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**pending_record_id** | **str** |  | 

## Example

```python
from resource_api.models.post_resource_version_response import PostResourceVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PostResourceVersionResponse from a JSON string
post_resource_version_response_instance = PostResourceVersionResponse.from_json(json)
# print the JSON string representation of the object
print(PostResourceVersionResponse.to_json())

# convert the object into a dict
post_resource_version_response_dict = post_resource_version_response_instance.to_dict()
# create an instance of PostResourceVersionResponse from a dict
post_resource_version_response_from_dict = PostResourceVersionResponse.from_dict(post_resource_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


