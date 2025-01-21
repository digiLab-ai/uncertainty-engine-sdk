from typing import Optional, Union

from typeguard import typechecked

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import dict_to_csv_str


@typechecked
class BuildSensorDesigner(Node):
    """
    Construct a sensor designer.

    Args:
        sensor_data: A dictionary of sensor data. Keys are sensor names and values are lists of sensor data.
        quantities_of_interest_data: A dictionary of quantities of interest data. Keys are quantities of
            interest names and values are lists of quantities of interest data.
        sigma: The uncertainty of the sensor data. If a float, the same uncertainty is applied to all sensors.
    """

    def __init__(
        self,
        sensor_data: dict[str, list[float]],
        quantities_of_interest_data: dict[str, list[float]],
        sigma: Optional[Union[float, list[float]]] = None,
    ):
        super().__init__(
            node_name="BuildSensorDesigner",
            sensor_data=dict_to_csv_str(sensor_data),
            quantities_of_interest_data=dict_to_csv_str(quantities_of_interest_data),
            sigma=sigma,
        )
