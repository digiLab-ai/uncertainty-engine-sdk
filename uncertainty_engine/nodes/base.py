from typeguard import typechecked


@typechecked
class Node:
    """
    A generic representation of a node in the Uncertainty Engine.

    Args:
        node_name: The name of the node.
        **kwargs: Arbitrary keyword arguments representing the input parameters of the node.
    """

    def __init__(self, node_name: str, **kwargs):
        self.name = node_name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self) -> tuple[str, dict]:
        """
        Make the node callable. Simply creates a dictionary of the input parameters that can
        be passed to the Uncertainty Engine.

        Returns:
            A tuple containing the name of the node and the input parameters.
        """
        input = {key: getattr(self, key) for key in self.__dict__ if key != "name"}
        return self.name, input
