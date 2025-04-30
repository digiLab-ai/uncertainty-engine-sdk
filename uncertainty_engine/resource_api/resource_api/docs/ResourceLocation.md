# ResourceLocation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | 
**storage_type** | **str** | The storage provider to use. | 
**config** | **object** | The storage configuration for the provider. | 

## Example

```python
from resource_api.models.resource_location import ResourceLocation

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceLocation from a JSON string
resource_location_instance = ResourceLocation.from_json(json)
# print the JSON string representation of the object
print(ResourceLocation.to_json())

# convert the object into a dict
resource_location_dict = resource_location_instance.to_dict()
# create an instance of ResourceLocation from a dict
resource_location_from_dict = ResourceLocation.from_dict(resource_location_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


