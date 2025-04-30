# resource_api.AccountRecordsResource

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_account_record**](AccountRecordsResource.md#delete_account_record) | **DELETE** /api/accounts/{account_id} | Delete Account Record
[**get_account_record**](AccountRecordsResource.md#get_account_record) | **GET** /api/accounts/{account_id} | Get Account Record Id
[**get_account_record_email**](AccountRecordsResource.md#get_account_record_email) | **GET** /api/accounts/email/{email} | Get Account Record Email
[**get_account_record_projects**](AccountRecordsResource.md#get_account_record_projects) | **GET** /api/accounts/{account_id}/projects | Get Account Record Projects
[**get_account_records**](AccountRecordsResource.md#get_account_records) | **GET** /api/accounts | Get Account Records
[**post_account_record**](AccountRecordsResource.md#post_account_record) | **POST** /api/accounts | Post Account Record


# **delete_account_record**
> object delete_account_record(account_id)

Delete Account Record

Delete an account.

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
    api_instance = resource_api.AccountRecordsResource(api_client)
    account_id = 'account_id_example' # str | 

    try:
        # Delete Account Record
        api_response = api_instance.delete_account_record(account_id)
        print("The response of AccountRecordsResource->delete_account_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->delete_account_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account_id** | **str**|  | 

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

# **get_account_record**
> AccountResponse get_account_record(account_id)

Get Account Record Id

Get a single account record.

### Example


```python
import resource_api
from resource_api.models.account_response import AccountResponse
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
    api_instance = resource_api.AccountRecordsResource(api_client)
    account_id = 'account_id_example' # str | 

    try:
        # Get Account Record Id
        api_response = api_instance.get_account_record(account_id)
        print("The response of AccountRecordsResource->get_account_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->get_account_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account_id** | **str**|  | 

### Return type

[**AccountResponse**](AccountResponse.md)

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

# **get_account_record_email**
> AccountResponse get_account_record_email(email)

Get Account Record Email

Get a single account using the account email.

### Example


```python
import resource_api
from resource_api.models.account_response import AccountResponse
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
    api_instance = resource_api.AccountRecordsResource(api_client)
    email = 'email_example' # str | 

    try:
        # Get Account Record Email
        api_response = api_instance.get_account_record_email(email)
        print("The response of AccountRecordsResource->get_account_record_email:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->get_account_record_email: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **str**|  | 

### Return type

[**AccountResponse**](AccountResponse.md)

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

# **get_account_record_projects**
> GetAccountRecordProjectsResponse get_account_record_projects(account_id)

Get Account Record Projects

Get all projects for an account.

### Example


```python
import resource_api
from resource_api.models.get_account_record_projects_response import GetAccountRecordProjectsResponse
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
    api_instance = resource_api.AccountRecordsResource(api_client)
    account_id = 'account_id_example' # str | 

    try:
        # Get Account Record Projects
        api_response = api_instance.get_account_record_projects(account_id)
        print("The response of AccountRecordsResource->get_account_record_projects:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->get_account_record_projects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **account_id** | **str**|  | 

### Return type

[**GetAccountRecordProjectsResponse**](GetAccountRecordProjectsResponse.md)

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

# **get_account_records**
> GetAccountRecordsResponse get_account_records()

Get Account Records

Get all accounts.

### Example


```python
import resource_api
from resource_api.models.get_account_records_response import GetAccountRecordsResponse
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
    api_instance = resource_api.AccountRecordsResource(api_client)

    try:
        # Get Account Records
        api_response = api_instance.get_account_records()
        print("The response of AccountRecordsResource->get_account_records:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->get_account_records: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetAccountRecordsResponse**](GetAccountRecordsResponse.md)

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

# **post_account_record**
> AccountResponse post_account_record(post_account_record_request)

Post Account Record

Create a new account.

### Example


```python
import resource_api
from resource_api.models.account_response import AccountResponse
from resource_api.models.post_account_record_request import PostAccountRecordRequest
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
    api_instance = resource_api.AccountRecordsResource(api_client)
    post_account_record_request = resource_api.PostAccountRecordRequest() # PostAccountRecordRequest | 

    try:
        # Post Account Record
        api_response = api_instance.post_account_record(post_account_record_request)
        print("The response of AccountRecordsResource->post_account_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountRecordsResource->post_account_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **post_account_record_request** | [**PostAccountRecordRequest**](PostAccountRecordRequest.md)|  | 

### Return type

[**AccountResponse**](AccountResponse.md)

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

