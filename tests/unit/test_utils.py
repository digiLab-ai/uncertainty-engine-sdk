from typing import Union

import pytest
from typeguard import TypeCheckError, typechecked

from uncertainty_engine import utils as ue_utils

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
