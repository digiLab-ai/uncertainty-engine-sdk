# PostAccountRecordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_record** | [**AccountRecordInput**](AccountRecordInput.md) |  | 

## Example

```python
from resource_api.models.post_account_record_request import PostAccountRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostAccountRecordRequest from a JSON string
post_account_record_request_instance = PostAccountRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PostAccountRecordRequest.to_json())

# convert the object into a dict
post_account_record_request_dict = post_account_record_request_instance.to_dict()
# create an instance of PostAccountRecordRequest from a dict
post_account_record_request_from_dict = PostAccountRecordRequest.from_dict(post_account_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


