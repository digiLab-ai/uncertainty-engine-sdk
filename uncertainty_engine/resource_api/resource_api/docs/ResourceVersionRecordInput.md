# ResourceVersionRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**name** | **str** |  | 
**project_id** | **object** |  | [optional] 
**resource_id** | **object** |  | [optional] 
**owner_id** | **object** |  | 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**location** | [**ResourceLocation**](ResourceLocation.md) |  | [optional] 

## Example

```python
from resource_api.models.resource_version_record_input import ResourceVersionRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceVersionRecordInput from a JSON string
resource_version_record_input_instance = ResourceVersionRecordInput.from_json(json)
# print the JSON string representation of the object
print(ResourceVersionRecordInput.to_json())

# convert the object into a dict
resource_version_record_input_dict = resource_version_record_input_instance.to_dict()
# create an instance of ResourceVersionRecordInput from a dict
resource_version_record_input_from_dict = ResourceVersionRecordInput.from_dict(resource_version_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


