import json
from typing import TypeAlias, TypeVar, Union

from typeguard import typechecked
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_types import Handle

# Define a type alias for a union of a type and a Handle.
T = TypeVar("T")
HandleUnion: TypeAlias = Union[T, Handle]


# TODO: Enforce that all columns are exclusively floats or ints.
#  Currently typeguard does not support this.
@typechecked
def dict_to_csv_str(data: dict[str, list[float]]) -> str:
    """
    Convert a dictionary to a CSV string.

    Args:
        data: A dictionary. Keys are column names and values are lists of data.

    Returns:
        A CSV string.
    """
    if len(data) == 0:
        # If the dictionary is empty, return an empty string rather than "\n".
        return ""

    # Verify that all columns have the same length.
    column_lengths = [len(column) for column in data.values()]
    if len(set(column_lengths)) != 1:
        raise ValueError("All columns must have the same length.")

    csv_str = ",".join(data.keys()) + "\n"
    for row in zip(*data.values()):
        csv_str += ",".join(str(x) for x in row) + "\n"
    return csv_str


@typechecked
def format_api_error(e: ApiException) -> str:
    """
    Load an API error message from a JSON string.

    Args:
        e: An exception object.

    Returns:
        A string containing the error message.
    """

    reason = getattr(e, "reason", None)
    reason = reason if reason else "No error reason"
    try:
        detail = json.loads(e.body).get("detail", "No error message")
    except Exception:
        detail = "No error message"

    return f"API Error: {reason}\nDetails: {detail}"
