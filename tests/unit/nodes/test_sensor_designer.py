from typing import Any

import pytest

from uncertainty_engine.nodes.sensor_designer import (
    BuildSensorDesigner,
    ScoreSensorDesign,
    SuggestSensorDesign,
)


@pytest.fixture
def mock_sensor_designer():
    """
    A mock sensor designer object that mimics the structure of a sensor designer object
    returned by the BuildSensorDesigner node.
    """
    sensor_designer = {
        "bed": {
            "key": "I am a bed"
        }  # bed is typed as a dict in workflow_types so we need to match that here
    }

    return sensor_designer


def test_build_sensor_designer():
    """
    Verify result for arbitrary test input.
    """

    sensor_data = {
        "sensor_1": [1, 2],
        "sensor_2": [4, 5],
    }

    qoi_data = {
        "qoi_1": [7, 8],
        "qoi_2": [10, 11],
    }

    sigma = 0.1

    node = BuildSensorDesigner(
        sensor_data=sensor_data,
        quantities_of_interest_data=qoi_data,
        sigma=sigma,
    )

    assert node() == (
        "BuildSensorDesigner",
        {
            "sensor_data": {"csv": "sensor_1,sensor_2\n1,4\n2,5\n"},
            "quantities_of_interest_data": {"csv": "qoi_1,qoi_2\n7,10\n8,11\n"},
            "sigma": sigma,
        },
    )


def test_build_sensor_designer_no_sigma():
    """
    Verify result for arbitrary test input with no sigma.
    """

    sensor_data = {
        "sensor_1": [1, 2],
        "sensor_2": [4, 5],
    }

    qoi_data = {
        "qoi_1": [7, 8],
        "qoi_2": [10, 11],
    }

    node = BuildSensorDesigner(
        sensor_data=sensor_data, quantities_of_interest_data=qoi_data
    )

    assert node() == (
        "BuildSensorDesigner",
        {
            "sensor_data": {"csv": "sensor_1,sensor_2\n1,4\n2,5\n"},
            "quantities_of_interest_data": {"csv": "qoi_1,qoi_2\n7,10\n8,11\n"},
            "sigma": None,
        },
    )


def test_build_sensor_designer_no_qoi():
    """
    Verify result for arbitrary test input with no quantities of interest data.
    """

    sensor_data = {
        "sensor_1": [1, 2],
        "sensor_2": [4, 5],
    }

    sigma = 0.1

    node = BuildSensorDesigner(sensor_data=sensor_data, sigma=sigma)

    assert node() == (
        "BuildSensorDesigner",
        {
            "sensor_data": {"csv": "sensor_1,sensor_2\n1,4\n2,5\n"},
            "quantities_of_interest_data": None,
            "sigma": sigma,
        },
    )


def test_build_sensor_designer_list_sigma():
    """
    Verify result for arbitrary test input with no quantities of interest data.
    """

    sensor_data = {
        "sensor_1": [1, 2],
        "sensor_2": [4, 5],
    }

    sigma = [0.1, 0.2]

    node = BuildSensorDesigner(sensor_data=sensor_data, sigma=sigma)

    assert node() == (
        "BuildSensorDesigner",
        {
            "sensor_data": {"csv": "sensor_1,sensor_2\n1,4\n2,5\n"},
            "quantities_of_interest_data": None,
            "sigma": sigma,
        },
    )


def test_suggest_sensor_design(mock_sensor_designer: dict[str, Any]):
    """
    Verify result for arbitrary test input.
    """

    num_sensors = 3
    num_eval = 4

    node = SuggestSensorDesign(
        sensor_designer=mock_sensor_designer,
        num_sensors=num_sensors,
        num_eval=num_eval,
    )

    assert node() == (
        "SuggestSensorDesign",
        {
            "sensor_designer": mock_sensor_designer,
            "num_sensors": num_sensors,
            "num_eval": num_eval,
        },
    )


def test_score_sensor_design(mock_sensor_designer: dict[str, Any]):
    """
    Verify result for arbitrary test input.
    """

    design = ["sensor_1", "sensor_2"]

    node = ScoreSensorDesign(
        sensor_designer=mock_sensor_designer,
        design=design,
    )

    assert node() == (
        "ScoreSensorDesign",
        {
            "sensor_designer": mock_sensor_designer,
            "design": design,
        },
    )
