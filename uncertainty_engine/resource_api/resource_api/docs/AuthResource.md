# resource_api.AuthResource

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_tokens**](AuthResource.md#get_tokens) | **POST** /api/auth/token | Get Tokens
[**refresh_token**](AuthResource.md#refresh_token) | **POST** /api/auth/refresh | Refresh Token


# **get_tokens**
> TokenResponse get_tokens()

Get Tokens

Exchange Cognito tokens for API tokens

### Example

* Bearer Authentication (HTTPBearer):

```python
import resource_api
from resource_api.models.token_response import TokenResponse
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = resource_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.AuthResource(api_client)

    try:
        # Get Tokens
        api_response = api_instance.get_tokens()
        print("The response of AuthResource->get_tokens:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthResource->get_tokens: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **refresh_token**
> TokenResponse refresh_token()

Refresh Token

Get new access token using refresh token

### Example

* Bearer Authentication (HTTPBearer):

```python
import resource_api
from resource_api.models.token_response import TokenResponse
from resource_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = resource_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = resource_api.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with resource_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = resource_api.AuthResource(api_client)

    try:
        # Refresh Token
        api_response = api_instance.refresh_token()
        print("The response of AuthResource->refresh_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthResource->refresh_token: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

