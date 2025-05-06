from typing import Union
import json
import pytest

from typeguard import TypeCheckError, typechecked

from uncertainty_engine import utils as ue_utils
from uncertainty_engine_resource_client.exceptions import ApiException

# dict_to_csv_str


def test_dict_to_csv_str():
    """
    Test dict_to_csv_str function with ideal input.
    """

    # Define some arbitrary data.
    data = {
        "a": [1, 2, 3],
        "b": [4, 5, 6],
    }

    # Define the expected output.
    expected = "a,b\n1,4\n2,5\n3,6\n"

    assert ue_utils.dict_to_csv_str(data) == expected


def test_dict_to_csv_str_empty():
    """
    Verify that dict_to_csv_str returns an empty string when given an empty dictionary.
    """

    # Define some arbitrary data.
    data = {}

    # Define the expected output.
    expected = ""

    assert ue_utils.dict_to_csv_str(data) == expected


def test_dict_to_csv_str_mismatched_lengths():
    """
    Verify that dict_to_csv_str raises a ValueError when given columns of mismatched lengths.
    """

    # Define some arbitrary data.
    data = {
        "a": [1, 2, 3],
        "b": [4, 5],
    }

    with pytest.raises(ValueError) as e:
        ue_utils.dict_to_csv_str(data)

    assert str(e.value) == "All columns must have the same length."


# TODO: This will fail because typing is not strong enough.
# def test_dict_to_csv_str_types():
#     """
#     Test dict_to_csv_str
#     """

#     # Define some arbitrary data.
#     data = {
#         "a": [1, "apple", 3],
#     }

#     with pytest.raises(Exception):
#         ue_utils.dict_to_csv_str(data)


# HandleUnion


@typechecked
def generic_fn(
    a: ue_utils.HandleUnion[int],
    b: ue_utils.HandleUnion[float],
    c: ue_utils.HandleUnion[Union[float, list[float]]],
) -> None:
    pass


def test_handle_union():
    """
    Test HandleUnion type alias.
    """

    # Make sure the function can be called with the correct types.
    generic_fn(1, 1.0, 1.0)
    generic_fn(ue_utils.Handle("a.b"), 1.0, [1.0, 1.0])
    generic_fn(ue_utils.Handle("a.b"), ue_utils.Handle("a.b"), ue_utils.Handle("a.b"))

    with pytest.raises(TypeCheckError):
        generic_fn(1, 1.0, "a.b")


def test_format_api_error_with_detail():
    """
    Test format_api_error with an ApiException that has a body with a 'detail' field.
    """
    # Create a mock ApiException with a body containing a detail field
    error_body = json.dumps({"detail": "Resource not found"})
    mock_exception = ApiException(status=404, reason="Not Found", body=error_body)

    # Call the function
    result = ue_utils.format_api_error(mock_exception)

    # Verify the result
    assert result == "Resource not found"


def test_format_api_error_without_detail():
    """
    Test format_api_error with an ApiException that has a JSON body but no 'detail' field.
    """
    # Create a mock ApiException with a body without a detail field
    error_body = json.dumps({"error": "Something went wrong", "code": "ERR123"})
    mock_exception = ApiException(
        status=500, reason="Internal Server Error", body=error_body
    )

    # Call the function
    result = ue_utils.format_api_error(mock_exception)

    # Verify the result - should return "Unknown error" as fallback
    assert result == "Unknown error"


def test_format_api_error_invalid_json():
    """
    Test format_api_error with an ApiException that has a body which is not valid JSON.
    """
    # Create a mock ApiException with an invalid JSON body
    error_body = "This is not JSON"
    mock_exception = ApiException(status=400, reason="Bad Request", body=error_body)

    # Call the function
    result = ue_utils.format_api_error(mock_exception)

    # Verify the result - should fall back to str(e)
    assert result == str(mock_exception)
