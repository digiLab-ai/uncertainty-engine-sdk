# resource_api.ProjectRecordsResource

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_project_record**](ProjectRecordsResource.md#delete_project_record) | **DELETE** /api/projects/{project_id} | Delete Project Record
[**get_project_record_id**](ProjectRecordsResource.md#get_project_record_id) | **GET** /api/projects/{project_id} | Get Project Record Id
[**get_project_records**](ProjectRecordsResource.md#get_project_records) | **GET** /api/projects | Get Project Records
[**post_project_record**](ProjectRecordsResource.md#post_project_record) | **POST** /api/projects | Post Project Record


# **delete_project_record**
> object delete_project_record(project_id)

Delete Project Record

Delete a project using the project id.

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
    api_instance = resource_api.ProjectRecordsResource(api_client)
    project_id = 'project_id_example' # str | 

    try:
        # Delete Project Record
        api_response = api_instance.delete_project_record(project_id)
        print("The response of ProjectRecordsResource->delete_project_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectRecordsResource->delete_project_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 

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

# **get_project_record_id**
> ProjectResponse get_project_record_id(project_id)

Get Project Record Id

Get a single project using the project id.

### Example


```python
import resource_api
from resource_api.models.project_response import ProjectResponse
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
    api_instance = resource_api.ProjectRecordsResource(api_client)
    project_id = 'project_id_example' # str | 

    try:
        # Get Project Record Id
        api_response = api_instance.get_project_record_id(project_id)
        print("The response of ProjectRecordsResource->get_project_record_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectRecordsResource->get_project_record_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_id** | **str**|  | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

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

# **get_project_records**
> GetProjectRecordsResponse get_project_records()

Get Project Records

Get all projects.

### Example


```python
import resource_api
from resource_api.models.get_project_records_response import GetProjectRecordsResponse
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
    api_instance = resource_api.ProjectRecordsResource(api_client)

    try:
        # Get Project Records
        api_response = api_instance.get_project_records()
        print("The response of ProjectRecordsResource->get_project_records:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectRecordsResource->get_project_records: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetProjectRecordsResponse**](GetProjectRecordsResponse.md)

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

# **post_project_record**
> ProjectResponse post_project_record(post_project_record_request)

Post Project Record

Create a new project.

### Example


```python
import resource_api
from resource_api.models.post_project_record_request import PostProjectRecordRequest
from resource_api.models.project_response import ProjectResponse
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
    api_instance = resource_api.ProjectRecordsResource(api_client)
    post_project_record_request = resource_api.PostProjectRecordRequest() # PostProjectRecordRequest | 

    try:
        # Post Project Record
        api_response = api_instance.post_project_record(post_project_record_request)
        print("The response of ProjectRecordsResource->post_project_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectRecordsResource->post_project_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_project_record_request** | [**PostProjectRecordRequest**](PostProjectRecordRequest.md)|  | 

### Return type

[**ProjectResponse**](ProjectResponse.md)

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

