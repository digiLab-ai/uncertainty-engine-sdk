from pydantic import BaseModel


class NodeQueryRequest(BaseModel):
    """
    Represents a query for a specific node and version.
    """

    node_id: str
    version: str

    def __str__(self):
        return f"{self.node_id}@{self.version}"


class NodeQueryListRequest(BaseModel):
    """
    List of node queries for batch operations.
    """

    nodes: list[NodeQueryRequest]
