# ResourceRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**name** | **str** |  | 
**project_id** | **object** |  | [optional] 
**owner_id** | **object** |  | 
**versions** | **List[object]** |  | [optional] [default to []]
**created_at** | **datetime** |  | [optional] 
**is_locked** | **bool** |  | [optional] [default to False]

## Example

```python
from resource_api.models.resource_record_input import ResourceRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceRecordInput from a JSON string
resource_record_input_instance = ResourceRecordInput.from_json(json)
# print the JSON string representation of the object
print(ResourceRecordInput.to_json())

# convert the object into a dict
resource_record_input_dict = resource_record_input_instance.to_dict()
# create an instance of ResourceRecordInput from a dict
resource_record_input_from_dict = ResourceRecordInput.from_dict(resource_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


