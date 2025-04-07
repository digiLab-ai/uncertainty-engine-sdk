# GetResourceVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_version_record** | [**ResourceVersionRecordOutput**](ResourceVersionRecordOutput.md) |  | 
**url** | **str** |  | 

## Example

```python
from resource_api.models.get_resource_version_response import GetResourceVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetResourceVersionResponse from a JSON string
get_resource_version_response_instance = GetResourceVersionResponse.from_json(json)
# print the JSON string representation of the object
print(GetResourceVersionResponse.to_json())

# convert the object into a dict
get_resource_version_response_dict = get_resource_version_response_instance.to_dict()
# create an instance of GetResourceVersionResponse from a dict
get_resource_version_response_from_dict = GetResourceVersionResponse.from_dict(get_resource_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


