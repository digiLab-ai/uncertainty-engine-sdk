from typing import Optional, Union

from typeguard import typechecked
from workflow_types import SensorDesigner, TabularData

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
        quantities_of_interest_data: Optional[dict[str, list[float]]] = None,
        sigma: Optional[Union[float, list[float]]] = None,
    ):
        super().__init__(
            node_name="sensor_designer.BuildSensorDesigner",
            sensor_data=TabularData(csv=dict_to_csv_str(sensor_data)).model_dump(),
            quantities_of_interest_data=(
                None
                if not quantities_of_interest_data
                else TabularData(
                    csv=dict_to_csv_str(quantities_of_interest_data)
                ).model_dump()
            ),
            sigma=sigma,
        )


@typechecked
class SuggestSensorDesign(Node):
    """
    Suggest a sensor design using a sensor designer.

    Args:
        sensor_designer: The sensor designer constructed by the BuildSensorDesigner node.
        num_sensors: The number of sensors to suggest.
        num_eval: The number of evaluations to perform.
    """

    def __init__(self, sensor_designer: dict, num_sensors: int, num_eval: int):
        super().__init__(
            node_name="sensor_designer.SuggestSensorDesign",
            sensor_designer=SensorDesigner(bed=sensor_designer).model_dump(),
            num_sensors=num_sensors,
            num_eval=num_eval,
        )


@typechecked
class ScoreSensorDesign(Node):
    """
    Score a given sensor design.

    Args:
        sensor_designer: The sensor designer constructed by the BuildSensorDesigner node.
        design: A list of sensors that make up the design.
    """

    def __init__(self, sensor_designer: dict, design: list):
        super().__init__(
            node_name="sensor_designer.SuggestSensorDesign",
            sensor_designer=SensorDesigner(bed=sensor_designer).model_dump(),
            design=design,
        )
