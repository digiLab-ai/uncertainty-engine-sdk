from typeguard import typechecked


@typechecked
def dict_to_csv_str(data: dict[str, list[float]]) -> str:
    """
    Convert a dictionary to a CSV string.

    Args:
        data: A dictionary. Keys are column names and values are lists of data.

    Returns:
        A CSV string.
    """
    csv_str = ",".join(data.keys()) + "\n"
    for row in zip(*data.values()):
        csv_str += ",".join(str(x) for x in row) + "\n"
    return csv_str
