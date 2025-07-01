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

    for part in parts[1:]:
        uri = uri.rstrip("/") + "/" + part.lstrip("/")

    return uri
