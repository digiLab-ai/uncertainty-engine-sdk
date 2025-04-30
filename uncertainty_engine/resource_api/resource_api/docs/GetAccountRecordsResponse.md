# GetAccountRecordsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_records** | [**List[AccountRecordOutput]**](AccountRecordOutput.md) |  | 

## Example

```python
from resource_api.models.get_account_records_response import GetAccountRecordsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountRecordsResponse from a JSON string
get_account_records_response_instance = GetAccountRecordsResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountRecordsResponse.to_json())

# convert the object into a dict
get_account_records_response_dict = get_account_records_response_instance.to_dict()
# create an instance of GetAccountRecordsResponse from a dict
get_account_records_response_from_dict = GetAccountRecordsResponse.from_dict(get_account_records_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


