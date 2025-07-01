def join_uri(*parts: str) -> str:
    """
    Joins parts of a URI with a single forward-slash.

    Args:
        parts: URI parts.

    Returns:
        URI.
    """

    if len(parts) == 0:
        return ""

    uri = parts[0].rstrip("/")

    for index in range(1, len(parts)):
        uri = uri.rstrip("/") + "/" + parts[index].lstrip("/")

    return uri
