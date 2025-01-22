from uncertainty_engine.nodes.sensor_designer import BuildSensorDesigner


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
        sensor_data=sensor_data, quantities_of_interest_data=qoi_data, sigma=sigma
    )

    assert node() == (
        "sensor_designer.BuildSensorDesigner",
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
        "sensor_designer.BuildSensorDesigner",
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
        "sensor_designer.BuildSensorDesigner",
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
        "sensor_designer.BuildSensorDesigner",
        {
            "sensor_data": {"csv": "sensor_1,sensor_2\n1,4\n2,5\n"},
            "quantities_of_interest_data": None,
            "sigma": sigma,
        },
    )
