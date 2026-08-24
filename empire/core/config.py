from inspect import Parameter, signature
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
        load_change_module: bool,
        filter_make: bool,
        filter_use: bool,
        n_cluster: int,
        moment_matching: bool,
        copula_clusters_make: bool,
        copula_clusters_use: bool,
        copulas_to_use: list[str],
        n_tree_compare: int,
        use_emission_cap: bool,
        compute_operational_duals: bool,
        print_in_iamc_format: bool,
        write_in_lp_format: bool,
        serialize_instance: bool,
        north_sea: bool,
        voronoi_sgr_make: bool = False,
        voronoi_sgr_use: bool = False,
        voronoi_mu_percentile: int = 80,
        regular_seasons: list[str] = ["winter", "spring", "summer", "fall"],
        n_peak_seasons: int = 2,
        len_peak_season: int = 24,
        leap_years_investment: int = 5,
        time_format: str = "%d/%m/%Y %H:%M",
        use_ramping: bool = True,
        solver_method: int = 2,
        solver_crossover: int | None = None,
        solver_presolve: int | None = -1,
        solver_threads: int | None = None,
        solver_scaleflag: int | None = None,
        solver_numericfocus: int | None = None,
        solver_barhomogeneous: int | None = None,
        **kwargs,
    ):
        """
        Class containing configurations for running Empire simulations.

        :param use_temporary_directory: Specifies whether to use a temporary directory for operations.
        :param temporary_directory: Path to the temporary directory used for certain operations.
        :param forecast_horizon_year: The last strategic (investment) period used in the optimization run. NB! Must correspond with data for version.
        :param number_of_scenarios: The number of scenarios in every investment period.
        :param length_of_regular_season: The number of chronological time steps in a regular season. NB! Must correspond with data for version.
        :param discount_rate: Rate used to discount future cash flows to present value.
        :param wacc: The Weighted Average Cost of Capital (WACC).
        :param optimization_solver: Mathematical solver used for optimization tasks. Options: “Xpress”, “Gurobi”, “CPLEX”.
        :param use_scenario_generation: If true, new operational scenarios will be generated. NB! If false, .tab-files or sampling key must be manually added to the ‘ScenarioData’-folder in the version.
        :param use_fixed_sample: If true, operational scenarios will be generated according to a fixed sampling key located in the ‘Scenario Data’ folder to ensure the same operational scenarios are generated.
        :param load_change_module:
        :param filter_make:
        :param filter_use:
        :param n_cluster:
        :param moment_matching:
        :param n_tree_compare:
        :param use_emission_cap: If true, emissions in every scenario are capped according to the specified cap in ‘General.xlsx’. If false, the CO2-price specified in ‘General.xlsx’ applies.
        :param compute_operational_duals: If true, investment decisions are fixed and resolved to compute operational duals
        :param print_in_iamc_format: OIf true, selected results are printed on the standard IAMC-format in addition to the normal EMPIRE print.
        :param write_in_lp_format: Problem should be written in Linear Programming format.
        :param serialize_instance: Serialize the data structure or model for later use.
        :param use_north_sea: Whether north-sea is modelled or not.
        :param regular_seasons: Regular seasons.
        :param n_peak_seasons:  Peak seasons.
        :param leap_years_investment: Years between investment decisions
        :param time_format: Time format
        :param use_ramping: If true (default), thermal generator ramp-rate constraints are included. Setting it to
            false removes the inter-hour ramping constraints (fewer rows, less temporal coupling for thermal units);
            only do this if ramping is non-binding at your time resolution, as it is a physical modelling assumption.
        :param solver_method: Gurobi 'Method' parameter (algorithm). 2 = barrier, best for large LPs.
        :param solver_crossover: Gurobi 'Crossover' parameter. 0 skips the crossover tail for faster
            barrier solves (interior-point solution only; duals/prices become approximate). None leaves the solver default.
        :param solver_presolve: Gurobi 'Presolve' parameter. -1 = automatic (default), 0 = off,
            1 = conservative, 2 = aggressive. None leaves the option unset.
        :param solver_threads: Gurobi 'Threads' parameter (max threads). Cap at physical core count to avoid
            hyperthread/NUMA contention on multi-socket machines. None leaves the solver default (all logical cores).
        :param solver_scaleflag: Gurobi 'ScaleFlag' parameter (matrix scaling). 0=off, 1/2/3 increasingly aggressive,
            -1=auto. Scaling is internal; results are returned in original units. None leaves the solver default.
        :param solver_numericfocus: Gurobi 'NumericFocus' parameter. 0=auto, 1-3 spend more effort on numerical
            accuracy (recommended when reading interior-point duals with crossover off). None leaves the solver default.
        :param solver_barhomogeneous: Gurobi 'BarHomogeneous' parameter. 1 enables the homogeneous barrier variant,
            more robust on ill-conditioned models. None leaves the solver default (-1, auto).
        """
        # Model parameters
        self.use_temporary_directory = use_temporary_directory
        self.temporary_directory = Path(temporary_directory).absolute()
        self.forecast_horizon_year = forecast_horizon_year
        self.number_of_scenarios = number_of_scenarios
        self.length_of_regular_season = length_of_regular_season
        self.discount_rate = discount_rate
        self.wacc = wacc
        self.optimization_solver = optimization_solver
        self.use_scenario_generation = use_scenario_generation
        self.use_fixed_sample = use_fixed_sample
        self.load_change_module = load_change_module
        self.filter_make = filter_make
        self.filter_use = filter_use
        self.copulas_to_use = copulas_to_use
        self.copula_clusters_make = copula_clusters_make
        self.copula_clusters_use = copula_clusters_use
        self.n_cluster = n_cluster
        self.moment_matching = moment_matching
        self.n_tree_compare = n_tree_compare
        self.use_emission_cap = use_emission_cap
        self.compute_operational_duals = compute_operational_duals
        self.print_in_iamc_format = print_in_iamc_format
        self.write_in_lp_format = write_in_lp_format
        self.serialize_instance = serialize_instance
        self.north_sea = north_sea
        self.voronoi_sgr_make = voronoi_sgr_make
        self.voronoi_sgr_use = voronoi_sgr_use
        self.voronoi_mu_percentile = voronoi_mu_percentile

        # Optional parameters
        self.regular_seasons = regular_seasons
        self.n_peak_seasons = n_peak_seasons
        self.len_peak_season = len_peak_season
        self.leap_years_investment = leap_years_investment
        self.time_format = time_format
        self.use_ramping = use_ramping

        # Solver (Gurobi) performance options
        self.solver_method = solver_method
        self.solver_crossover = solver_crossover
        self.solver_presolve = solver_presolve
        self.solver_threads = solver_threads
        self.solver_scaleflag = solver_scaleflag
        self.solver_numericfocus = solver_numericfocus
        self.solver_barhomogeneous = solver_barhomogeneous

        # Computed attributes
        self.n_reg_season = len(regular_seasons)
        self.periods = [i + 1 for i in range(int((self.forecast_horizon_year - 2025) / self.leap_years_investment))]
        self.n_periods = len(self.periods)

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

        If constructor arguments are missing and they don't have default values,
        they are added with None value to handle earlier versions of the configuration.

        :param config: Dictionary with configurations.
        :returns: An instance of EmpireConfiguration.
        """
        # Get the signature of the __init__ method
        init_signature = signature(cls.__init__)

        # Prepare a dictionary of arguments
        # Set to None if there is no default value
        init_args = {}
        for param_name, param in init_signature.parameters.items():
            if param_name != "self":
                # Check if the parameter has a default value
                if param.default is Parameter.empty:
                    init_args[param_name] = None
                else:
                    init_args[param_name] = param.default

        # Update the dictionary with values from the config
        init_args.update({k: v for k, v in config.items() if k in init_args})

        # Create an instance of the class with the arguments
        return cls(**init_args)
    
    def to_dict(self) -> dict:
        """
        Used for serialization.

        :return: dictionary
        """
        my_dict = self.__dict__
        for k in my_dict:
            if isinstance(my_dict[k], Path):
                my_dict[k] = str(my_dict[k])
                
        return my_dict


class EmpireRunConfiguration:
    def __init__(
        self,
        run_name: str,
        dataset_path: Path | str,
        tab_path: Path | str,
        scenario_data_path: Path | str,
        results_path: Path | str,
        empire_path: Path | str = Path.cwd(),
    ):
        """
        Class containing configurations for running Empire simulations.

        :param run_name: Name of the run
        :param dataset_path: Folder containing the dataset.
        :param tab_path: Folder containing the .tab files.
        :param scenario_data_path: Folder containing the scenario data.
        :param results_path: Folder where the results should reside.
        :param empire_path: Path to empire project, default is current working directory.
        """

        self.run_name = run_name
        self.dataset_path = Path(dataset_path)
        self.tab_file_path = Path(tab_path)
        self.scenario_data_path = Path(scenario_data_path)
        self.results_path = Path(results_path)
        self.empire_path = Path(empire_path)

        # Validate the configuration
        self.validate()

    def validate(self):
        """
        Validates the configuration. Raises an error if the configuration is invalid.
        """
        if not self.empire_path.exists():
            raise ValueError(f"{self.empire_path} does not exists.")

    @classmethod
    def from_dict(cls, config: dict) -> "EmpireRunConfiguration":
        """
        Constructs EmpireRunConfiguration object from a dictionary.

        :param config: Dictionary with configurations.
        :returns: An instance of EmpireRunConfiguration.
        """
        return cls(**config)
