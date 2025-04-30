# AccountRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**email** | **str** |  | 
**name** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 

## Example

```python
from resource_api.models.account_record_output import AccountRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of AccountRecordOutput from a JSON string
account_record_output_instance = AccountRecordOutput.from_json(json)
# print the JSON string representation of the object
print(AccountRecordOutput.to_json())

# convert the object into a dict
account_record_output_dict = account_record_output_instance.to_dict()
# create an instance of AccountRecordOutput from a dict
account_record_output_from_dict = AccountRecordOutput.from_dict(account_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


