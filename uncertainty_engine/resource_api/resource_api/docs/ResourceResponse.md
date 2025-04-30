# ResourceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_record** | [**ResourceRecordOutput**](ResourceRecordOutput.md) |  | 

## Example

```python
from resource_api.models.resource_response import ResourceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceResponse from a JSON string
resource_response_instance = ResourceResponse.from_json(json)
# print the JSON string representation of the object
print(ResourceResponse.to_json())

# convert the object into a dict
resource_response_dict = resource_response_instance.to_dict()
# create an instance of ResourceResponse from a dict
resource_response_from_dict = ResourceResponse.from_dict(resource_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


