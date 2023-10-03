from pathlib import Path
from typing import Dict

import yaml


def read_config_file(path: Path) -> Dict:
    with open(path) as file:
        config = yaml.safe_load(file)

    return config


class EmpireConfiguration:
    def __init__(
        self,
        use_temporary_directory: bool,
        temporary_directory: str | Path,
        forecast_horizon_year: int,
        number_of_scenarios: int,
        length_of_regular_season: int,
        discount_rate: float,
        wacc: float,
        optimization_solver: str,
        use_scenario_generation: bool,
        use_fixed_sample: bool,
        use_emission_cap: bool,
        print_in_iamc_format: bool,
        write_in_lp_format: bool,
        serialize_instance: bool,
        north_sea: bool,
    ):
        """
        Class containing configurations for running Empire simulations.

        :param use_temporary_directory: Specifies whether to use a temporary directory for operations
        :param temporary_directory: Path to the temporary directory used for certain operations
        :param forecast_horizon_year: Target or end year for a simulation or forecast
        :param number_of_scenarios: Number of scenarios to consider in the simulation or modeling
        :param length_of_regular_season: Length of a regulatory or regular season (e.g., in hours)
        :param discount_rate: Rate used to discount future cash flows to present value
        :param wacc: Weighted Average Cost of Capital (WACC)
        :param optimization_solver: Mathematical solver used for optimization tasks
        :param use_scenario_generation: Indicates if scenarios should be generated dynamically
        :param use_fixed_sample: Specifies if a certain sample or set of data is fixed
        :param use_emission_cap: Indicates if there's a cap on emissions
        :param print_in_iamc_format: Output should be printed in a specific format (e.g., IAMC-compatible)
        :param write_in_lp_format: Problem should be written in Linear Programming format
        :param serialize_instance: Serialize the data structure or model for later use
        :param use_north_sea: Whether north-sea is modelled or not
        """
        # Model parameters
        self.use_temporary_directory = use_temporary_directory
        self.temporary_directory = Path(temporary_directory)
        self.forecast_horizon_year = forecast_horizon_year
        self.number_of_scenarios = number_of_scenarios
        self.length_of_regular_season = length_of_regular_season
        self.discount_rate = discount_rate
        self.wacc = wacc
        self.optimization_solver = optimization_solver
        self.use_scenario_generation = use_scenario_generation
        self.use_fixed_sample = use_fixed_sample
        self.use_emission_cap = use_emission_cap
        self.print_in_iamc_format = print_in_iamc_format
        self.write_in_lp_format = write_in_lp_format
        self.serialize_instance = serialize_instance
        self.north_sea = north_sea

        # Fixed configuration
        self.n_reg_season = 4
        self.regular_seasons = ["winter", "spring", "summer", "fall"]
        self.n_peak_seasons = 2
        self.len_peak_season = 24
        self.leap_years_investment = 5
        self.time_format = "%d/%m/%Y %H:%M"

        # Validate the configuration
        self.validate()

    def validate(self):
        """
        Validates the configuration. Raises an error if the configuration is invalid.
        """
        pass

    @classmethod
    def from_dict(cls, config: Dict) -> "EmpireConfiguration":
        """
        Constructs EmpireConfiguration object from a dictionary.

        :param config: Dictionary with configurations.
        :returns: An instance of EmpireConfiguration.
        """
        return cls(**config)


class EmpireRunConfiguration:
    def __init__(
        self,
        run_name: str,
        dataset_path: Path | str,
        tab_path: Path | str,
        scenario_data_path: Path | str,
        results_path: Path | str,
    ):
        """
        Class containing configurations for running Empire simulations.

        :param run_name: Name of the run
        :param dataset_path: Folder containing the dataset.
        :param tab_path: Folder containing the .tab files.
        :param scenario_data_path: Folder containing the scenario data.
        :param results_path: Folder where the results should reside.
        """

        self.run_name = run_name
        self.dataset_path = dataset_path
        self.tab_file_path = tab_path
        self.scenario_data_path = scenario_data_path
        self.results_path = results_path

        # Validate the configuration
        self.validate()

    def validate(self):
        """
        Validates the configuration. Raises an error if the configuration is invalid.
        """
        pass

    @classmethod
    def from_dict(cls, config: Dict) -> "EmpireRunConfiguration":
        """
        Constructs EmpireRunConfiguration object from a dictionary.

        :param config: Dictionary with configurations.
        :returns: An instance of EmpireRunConfiguration.
        """
        return cls(**config)
