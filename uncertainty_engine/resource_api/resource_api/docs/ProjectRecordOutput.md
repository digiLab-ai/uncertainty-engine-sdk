# ProjectRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**owner_id** | **str** |  | 
**description** | **str** |  | [optional] 
**members** | [**Dict[str, ProjectRoles]**](ProjectRoles.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from resource_api.models.project_record_output import ProjectRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectRecordOutput from a JSON string
project_record_output_instance = ProjectRecordOutput.from_json(json)
# print the JSON string representation of the object
print(ProjectRecordOutput.to_json())

# convert the object into a dict
project_record_output_dict = project_record_output_instance.to_dict()
# create an instance of ProjectRecordOutput from a dict
project_record_output_from_dict = ProjectRecordOutput.from_dict(project_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


