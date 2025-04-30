# ResourceRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**project_id** | **str** |  | [optional] 
**owner_id** | **str** |  | 
**versions** | **List[str]** |  | [optional] [default to []]
**created_at** | **datetime** |  | [optional] 
**is_locked** | **bool** |  | [optional] [default to False]

## Example

```python
from resource_api.models.resource_record_output import ResourceRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of ResourceRecordOutput from a JSON string
resource_record_output_instance = ResourceRecordOutput.from_json(json)
# print the JSON string representation of the object
print(ResourceRecordOutput.to_json())

# convert the object into a dict
resource_record_output_dict = resource_record_output_instance.to_dict()
# create an instance of ResourceRecordOutput from a dict
resource_record_output_from_dict = ResourceRecordOutput.from_dict(resource_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


