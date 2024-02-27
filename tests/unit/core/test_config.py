from pathlib import Path

from empire.core.config import EmpireConfiguration


def test_complete_configuration():
    config = {
        "use_temporary_directory": True,
        "temporary_directory": "/tmp",
        "forecast_horizon_year": 2025,
        "number_of_scenarios": 10,
    }
    empire_config = EmpireConfiguration.from_dict(config)
    assert empire_config.use_temporary_directory
    assert empire_config.temporary_directory == Path("/tmp")


def test_incomplete_configuration():
    config = {
        # Only include some parameters
        "use_temporary_directory": True,
        "temporary_directory": "/tmp",
        "forecast_horizon_year": 2025,
        "number_of_scenarios": 10,
    }
    empire_config = EmpireConfiguration.from_dict(config)
    assert empire_config.use_temporary_directory
    assert empire_config.temporary_directory == Path("/tmp")
    # Assert that missing parameters are None or their default values
    assert empire_config.wacc is None
    assert empire_config.regular_seasons == ["winter", "spring", "summer", "fall"]
