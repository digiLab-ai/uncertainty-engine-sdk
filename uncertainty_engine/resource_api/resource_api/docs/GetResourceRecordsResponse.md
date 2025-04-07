# GetResourceRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_records** | [**List[ResourceRecordOutput]**](ResourceRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_resource_records_response import GetResourceRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetResourceRecordsResponse from a JSON string
get_resource_records_response_instance = GetResourceRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetResourceRecordsResponse.to_json())

# convert the object into a dict
get_resource_records_response_dict = get_resource_records_response_instance.to_dict()
# create an instance of GetResourceRecordsResponse from a dict
get_resource_records_response_from_dict = GetResourceRecordsResponse.from_dict(get_resource_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


