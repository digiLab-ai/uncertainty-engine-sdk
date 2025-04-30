# ResourceVersionRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 
**resource_id** | **str** |  | [optional] 
**owner_id** | **str** |  | 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**location** | [**ResourceLocation**](ResourceLocation.md) |  | [optional] 

## Example

```python
from resource_api.models.resource_version_record_output import ResourceVersionRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceVersionRecordOutput from a JSON string
resource_version_record_output_instance = ResourceVersionRecordOutput.from_json(json)
# print the JSON string representation of the object
print(ResourceVersionRecordOutput.to_json())

# convert the object into a dict
resource_version_record_output_dict = resource_version_record_output_instance.to_dict()
# create an instance of ResourceVersionRecordOutput from a dict
resource_version_record_output_from_dict = ResourceVersionRecordOutput.from_dict(resource_version_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


