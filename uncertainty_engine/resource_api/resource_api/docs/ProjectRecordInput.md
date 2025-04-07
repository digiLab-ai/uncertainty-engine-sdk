# ProjectRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**name** | **str** |  | 
**owner_id** | **object** |  | 
**description** | **str** |  | [optional] 
**members** | [**Dict[str, ProjectRoles]**](ProjectRoles.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from resource_api.models.project_record_input import ProjectRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectRecordInput from a JSON string
project_record_input_instance = ProjectRecordInput.from_json(json)
# print the JSON string representation of the object
print(ProjectRecordInput.to_json())

# convert the object into a dict
project_record_input_dict = project_record_input_instance.to_dict()
# create an instance of ProjectRecordInput from a dict
project_record_input_from_dict = ProjectRecordInput.from_dict(project_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


