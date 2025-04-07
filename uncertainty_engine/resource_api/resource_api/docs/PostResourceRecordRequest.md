# PostResourceRecordRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_record** | [**ResourceRecordInput**](ResourceRecordInput.md) |  | 

## Example

```python
from resource_api.models.post_resource_record_request import PostResourceRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostResourceRecordRequest from a JSON string
post_resource_record_request_instance = PostResourceRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PostResourceRecordRequest.to_json())

# convert the object into a dict
post_resource_record_request_dict = post_resource_record_request_instance.to_dict()
# create an instance of PostResourceRecordRequest from a dict
post_resource_record_request_from_dict = PostResourceRecordRequest.from_dict(post_resource_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


