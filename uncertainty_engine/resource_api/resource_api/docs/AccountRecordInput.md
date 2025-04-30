# AccountRecordInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **object** |  | [optional] 
**email** | **str** |  | 
**name** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 

## Example

```python
from resource_api.models.account_record_input import AccountRecordInput

# TODO update the JSON string below
json = "{}"
# create an instance of AccountRecordInput from a JSON string
account_record_input_instance = AccountRecordInput.from_json(json)
# print the JSON string representation of the object
print(AccountRecordInput.to_json())

# convert the object into a dict
account_record_input_dict = account_record_input_instance.to_dict()
# create an instance of AccountRecordInput from a dict
account_record_input_from_dict = AccountRecordInput.from_dict(account_record_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


