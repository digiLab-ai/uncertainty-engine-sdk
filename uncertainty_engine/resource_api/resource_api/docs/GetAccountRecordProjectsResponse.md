# GetAccountRecordProjectsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_records** | [**List[ProjectRecordOutput]**](ProjectRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_account_record_projects_response import GetAccountRecordProjectsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountRecordProjectsResponse from a JSON string
get_account_record_projects_response_instance = GetAccountRecordProjectsResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountRecordProjectsResponse.to_json())

# convert the object into a dict
get_account_record_projects_response_dict = get_account_record_projects_response_instance.to_dict()
# create an instance of GetAccountRecordProjectsResponse from a dict
get_account_record_projects_response_from_dict = GetAccountRecordProjectsResponse.from_dict(get_account_record_projects_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


