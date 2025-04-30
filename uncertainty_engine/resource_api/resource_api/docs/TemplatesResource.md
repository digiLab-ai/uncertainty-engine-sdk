# resource_api.TemplatesResource

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_workflow_template**](TemplatesResource.md#delete_workflow_template) | **DELETE** /api/templates/workflows/{workflow_template_id} | Delete Workflow Template
[**get_workflow_template_record**](TemplatesResource.md#get_workflow_template_record) | **GET** /api/templates/workflows/{workflow_template_id} | Get Workflow Template
[**get_workflow_template_records**](TemplatesResource.md#get_workflow_template_records) | **GET** /api/templates/workflows | Get Workflow Templates
[**workflow_template**](TemplatesResource.md#workflow_template) | **POST** /api/template/workflows | Workflow Template


# **delete_workflow_template**
> object delete_workflow_template(workflow_template_id)

Delete Workflow Template

### Example


```python
import resource_api
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.TemplatesResource(api_client)
    workflow_template_id = 'workflow_template_id_example' # str | 

    try:
        # Delete Workflow Template
        api_response = api_instance.delete_workflow_template(workflow_template_id)
        print("The response of TemplatesResource->delete_workflow_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TemplatesResource->delete_workflow_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_template_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_template_record**
> WorkflowTemplateResponse get_workflow_template_record(workflow_template_id)

Get Workflow Template

### Example


```python
import resource_api
from resource_api.models.workflow_template_response import WorkflowTemplateResponse
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.TemplatesResource(api_client)
    workflow_template_id = 'workflow_template_id_example' # str | 

    try:
        # Get Workflow Template
        api_response = api_instance.get_workflow_template_record(workflow_template_id)
        print("The response of TemplatesResource->get_workflow_template_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TemplatesResource->get_workflow_template_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_template_id** | **str**|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_template_records**
> GetWorkflowTemplateRecordsResponse get_workflow_template_records()

Get Workflow Templates

### Example


```python
import resource_api
from resource_api.models.get_workflow_template_records_response import GetWorkflowTemplateRecordsResponse
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.TemplatesResource(api_client)

    try:
        # Get Workflow Templates
        api_response = api_instance.get_workflow_template_records()
        print("The response of TemplatesResource->get_workflow_template_records:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TemplatesResource->get_workflow_template_records: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetWorkflowTemplateRecordsResponse**](GetWorkflowTemplateRecordsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **workflow_template**
> WorkflowTemplateResponse workflow_template(post_workflow_template_record_request)

Workflow Template

### Example


```python
import resource_api
from resource_api.models.post_workflow_template_record_request import PostWorkflowTemplateRecordRequest
from resource_api.models.workflow_template_response import WorkflowTemplateResponse
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.TemplatesResource(api_client)
    post_workflow_template_record_request = resource_api.PostWorkflowTemplateRecordRequest() # PostWorkflowTemplateRecordRequest | 

    try:
        # Workflow Template
        api_response = api_instance.workflow_template(post_workflow_template_record_request)
        print("The response of TemplatesResource->workflow_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TemplatesResource->workflow_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_workflow_template_record_request** | [**PostWorkflowTemplateRecordRequest**](PostWorkflowTemplateRecordRequest.md)|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

