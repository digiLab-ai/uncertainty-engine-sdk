import json
from typing import TypeAlias, TypeVar, Union, Any
from warnings import warn

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


def handle_input_deprecation(
    input: dict[str, Any] | None, inputs: dict[str, Any] | None, stacklevel: int = 3
) -> dict[str, Any] | None:
    """
    Handle deprecation of 'input' parameter in favor of 'inputs'.

    Args:
        input: The deprecated parameter value
        inputs: The new parameter value
        stacklevel: Stack level for the warning (default 3 to account for helper call)

    Returns:
        The resolved inputs value

    Raises:
        ValueError: If both parameters are provided
    """
    if input is not None and inputs is not None:
        raise ValueError("Cannot specify both 'input' and 'inputs'. Use 'inputs' only.")

    if input is not None:
        warn(
            "The 'input' parameter is deprecated and will be removed in the next "
            "release. Use 'inputs' instead.",
            DeprecationWarning,
            stacklevel=stacklevel,
        )
        return input

    return inputs
