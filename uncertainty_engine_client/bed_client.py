# imports
from typing import Optional, Union

import pandas as pd

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.sensor_designer import (
    BuildSensorDesigner,
    ScoreSensorDesign,
    SuggestSensorDesign,
)


class Designer:
    def __init__(
        self,
        email: str,
        observables: pd.DataFrame,
        quantities_of_interest: Optional[pd.DataFrame] = None,
        sigma: Optional[Union[float, list[float]]] = None,
    ):
        self.client = Client(
            email=email,
            deployment="https://13qg20i4yc.execute-api.eu-west-2.amazonaws.com/dev/api",
        )
        observables = observables.to_dict(orient="list")

        if quantities_of_interest is not None:
            quantities_of_interest = quantities_of_interest.to_dict(orient="list")

        builder = BuildSensorDesigner(
            sensor_data=observables,
            quantities_of_interest_data=quantities_of_interest,
            sigma=sigma,
        )

        response = self.client.run_node(builder)

        self.designer = response["output"]["sensor_designer"]

    def suggest(self, num_sensors: int, num_eval: int):
        suggest_design = SuggestSensorDesign(
            sensor_designer=self.designer,
            num_sensors=num_sensors,
            num_eval=num_eval,
        )

        response = self.client.run_node(suggest_design)

        self.designer = response["output"]["sensor_designer"]

        return response["output"]["suggested_design"]

    def score(self, design: list):
        score_design = ScoreSensorDesign(
            sensor_designer=self.designer,
            design=design,
        )

        response = self.client.run_node(score_design)

        self.designer = response["output"]["sensor_designer"]

        return response["output"]["score"]
