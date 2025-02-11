from typing import Optional, Union

from typeguard import typechecked
from uncertainty_engine_types import Handle, SensorDesigner, TabularData

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import OldHandle, dict_to_csv_str

ListDict = dict[str, list[float]]


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

    node_name: str = "sensor_designer.BuildSensorDesigner"

    def __init__(
        self,
        sensor_data: Union[ListDict, Handle],
        quantities_of_interest_data: Optional[Union[ListDict, Handle]] = None,
        sigma: Optional[Union[float, list[float], Handle]] = None,
        label: Optional[str] = None,
    ):
        # Deal with the sensor data.
        if isinstance(sensor_data, Handle):
            sensor_data = OldHandle(sensor_data)
        else:
            sensor_data = TabularData(csv=dict_to_csv_str(sensor_data)).model_dump()

        # Deal with the QOI data.
        if quantities_of_interest_data is not None:
            if isinstance(quantities_of_interest_data, Handle):
                quantities_of_interest_data = OldHandle(quantities_of_interest_data)
            else:
                quantities_of_interest_data = TabularData(
                    csv=dict_to_csv_str(quantities_of_interest_data)
                ).model_dump()

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_data=sensor_data,
            quantities_of_interest_data=quantities_of_interest_data,
            sigma=OldHandle(sigma) if isinstance(sigma, Handle) else sigma,
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

    node_name: str = "sensor_designer.SuggestSensorDesign"

    def __init__(
        self,
        sensor_designer: Union[dict, Handle],
        num_sensors: int,
        num_eval: int,
        label: Optional[str] = None,
    ):
        # Deal with the sensor designer.
        if isinstance(sensor_designer, Handle):
            sensor_designer = OldHandle(sensor_designer)
        else:
            sensor_designer = SensorDesigner(bed=sensor_designer["bed"]).model_dump()

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_designer=sensor_designer,
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

    node_name: str = "sensor_designer.ScoreSensorDesign"

    def __init__(
        self,
        sensor_designer: Union[dict, Handle],
        design: Union[list, Handle],
        label: Optional[str] = None,
    ):
        # Deal with the sensor designer.
        if isinstance(sensor_designer, Handle):
            sensor_designer = OldHandle(sensor_designer)
        else:
            sensor_designer = SensorDesigner(bed=sensor_designer["bed"]).model_dump()

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_designer=sensor_designer,
            design=OldHandle(design) if isinstance(design, Handle) else design,
        )
