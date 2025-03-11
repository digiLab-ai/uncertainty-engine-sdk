from typing import Optional, Union

from typeguard import typechecked
from uncertainty_engine_types import CSVDataset, Handle, SensorDesigner

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion, dict_to_csv_str

ListDict = dict[str, list[Union[float, int]]]


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

    node_name: str = "BuildSensorDesigner"

    def __init__(
        self,
        sensor_data: HandleUnion[ListDict],
        quantities_of_interest_data: Optional[HandleUnion[ListDict]] = None,
        sigma: Optional[HandleUnion[Union[float, list[float]]]] = None,
        label: Optional[str] = None,
    ):
        # Deal with the sensor data.
        if isinstance(sensor_data, Handle):
            sensor_data_processed = sensor_data
        else:
            sensor_data_processed = CSVDataset(
                csv=dict_to_csv_str(sensor_data)
            ).model_dump()

        # Deal with the QOI data.
        if quantities_of_interest_data is not None:
            if isinstance(quantities_of_interest_data, Handle):
                quantities_of_interest_data_processed = quantities_of_interest_data
            else:
                quantities_of_interest_data_processed = CSVDataset(
                    csv=dict_to_csv_str(quantities_of_interest_data)
                ).model_dump()
        else:
            quantities_of_interest_data_processed = None

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_data=sensor_data_processed,
            quantities_of_interest_data=quantities_of_interest_data_processed,
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

    node_name: str = "SuggestSensorDesign"

    def __init__(
        self,
        sensor_designer: HandleUnion[dict],
        num_sensors: HandleUnion[int],
        num_eval: HandleUnion[int],
        label: Optional[str] = None,
    ):
        # Deal with the sensor designer.
        if isinstance(sensor_designer, Handle):
            sensor_designer_processed = sensor_designer
        else:
            sensor_designer_processed = SensorDesigner(
                bed=sensor_designer["bed"]
            ).model_dump()

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_designer=sensor_designer_processed,
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

    node_name: str = "ScoreSensorDesign"

    def __init__(
        self,
        sensor_designer: HandleUnion[dict],
        design: HandleUnion[list],
        label: Optional[str] = None,
    ):
        # Deal with the sensor designer.
        if isinstance(sensor_designer, Handle):
            sensor_designer_processed = sensor_designer
        else:
            sensor_designer_processed = SensorDesigner(
                bed=sensor_designer["bed"]
            ).model_dump()

        super().__init__(
            node_name=self.node_name,
            label=label,
            sensor_designer=sensor_designer_processed,
            design=design,
        )
