# GetResourceVersionRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_version_records** | [**List[ResourceVersionRecordOutput]**](ResourceVersionRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_resource_version_records_response import GetResourceVersionRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetResourceVersionRecordsResponse from a JSON string
get_resource_version_records_response_instance = GetResourceVersionRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetResourceVersionRecordsResponse.to_json())

# convert the object into a dict
get_resource_version_records_response_dict = get_resource_version_records_response_instance.to_dict()
# create an instance of GetResourceVersionRecordsResponse from a dict
get_resource_version_records_response_from_dict = GetResourceVersionRecordsResponse.from_dict(get_resource_version_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


