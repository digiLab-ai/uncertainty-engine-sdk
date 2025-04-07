# PatchResourceVersionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_update** | **object** |  | 

## Example

```python
from resource_api.models.patch_resource_version_request import PatchResourceVersionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchResourceVersionRequest from a JSON string
patch_resource_version_request_instance = PatchResourceVersionRequest.from_json(json)
# print the JSON string representation of the object
print(PatchResourceVersionRequest.to_json())

# convert the object into a dict
patch_resource_version_request_dict = patch_resource_version_request_instance.to_dict()
# create an instance of PatchResourceVersionRequest from a dict
patch_resource_version_request_from_dict = PatchResourceVersionRequest.from_dict(patch_resource_version_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


