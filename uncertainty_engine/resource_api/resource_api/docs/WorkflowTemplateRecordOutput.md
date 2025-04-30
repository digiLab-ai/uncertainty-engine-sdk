# WorkflowTemplateRecordOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | 
**description** | **str** |  | 
**complexity** | **str** |  | [optional] [default to 'simple']
**is_new** | **bool** |  | [optional] [default to False]
**image_src** | **str** |  | [optional] [default to '']
**location** | [**ResourceLocation**](ResourceLocation.md) |  | [optional] 

## Example

```python
from resource_api.models.workflow_template_record_output import WorkflowTemplateRecordOutput

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateRecordOutput from a JSON string
workflow_template_record_output_instance = WorkflowTemplateRecordOutput.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateRecordOutput.to_json())

# convert the object into a dict
workflow_template_record_output_dict = workflow_template_record_output_instance.to_dict()
# create an instance of WorkflowTemplateRecordOutput from a dict
workflow_template_record_output_from_dict = WorkflowTemplateRecordOutput.from_dict(workflow_template_record_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


