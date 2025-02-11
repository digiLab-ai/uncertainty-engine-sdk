from typing import TypeAlias, TypeVar, Union

from typeguard import typechecked
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


# TODO: Remove on switch to new backend.
@typechecked
class OldHandle:
    def __init__(self, new_handle: Handle):
        self.node_name = new_handle.node_name
        self.node_handle = new_handle.node_handle

    def __call__(self):
        return (self.node_name, self.node_handle)
