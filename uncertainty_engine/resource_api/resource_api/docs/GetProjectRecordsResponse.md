# GetProjectRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_records** | [**List[ProjectRecordOutput]**](ProjectRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_project_records_response import GetProjectRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProjectRecordsResponse from a JSON string
get_project_records_response_instance = GetProjectRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetProjectRecordsResponse.to_json())

# convert the object into a dict
get_project_records_response_dict = get_project_records_response_instance.to_dict()
# create an instance of GetProjectRecordsResponse from a dict
get_project_records_response_from_dict = GetProjectRecordsResponse.from_dict(get_project_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


