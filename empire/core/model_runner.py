#!/usr/bin/env python
import json
import logging
import pprint
from pathlib import Path

from empire import run_empire
from empire.core.config import EmpireConfiguration, EmpireRunConfiguration, read_config_file
from empire.core.reader import generate_tab_files
from empire.core.scenario_random import check_scenarios_exist_and_copy, generate_random_scenario
from empire.input_data_manager import IDataManager
from empire.utils import copy_dataset, copy_scenario_data, create_if_not_exist, get_run_name

logger = logging.getLogger(__name__)


def run_empire_model(
    empire_config: EmpireConfiguration,
    run_config: EmpireRunConfiguration,
    data_managers: list[IDataManager],
    test_run: bool,
):
    for manager in data_managers:
        manager.apply()

    horizon = empire_config.forecast_horizon_year
    NoOfScenarios = empire_config.number_of_scenarios
    len_reg_season = empire_config.length_of_regular_season
    discountrate = empire_config.discount_rate
    use_scen_generation = empire_config.use_scenario_generation

    #############################
    ##Non configurable settings##
    #############################

    NoOfRegSeason = empire_config.n_reg_season
    regular_seasons = empire_config.regular_seasons
    NoOfPeakSeason = empire_config.n_peak_seasons
    len_peak_season = empire_config.len_peak_season
    discountrate = empire_config.discount_rate
    LeapYearsInvestment = empire_config.leap_years_investment

    workbook_path = run_config.dataset_path
    tab_file_path = run_config.tab_file_path
    scenario_data_path = run_config.scenario_data_path
    result_file_path = run_config.results_path

    #######
    ##RUN##
    #######

    FirstHoursOfRegSeason = [len_reg_season * i + 1 for i in range(NoOfRegSeason)]
    FirstHoursOfPeakSeason = [len_reg_season * NoOfRegSeason + len_peak_season * i + 1 for i in range(NoOfPeakSeason)]
    Period = [i + 1 for i in range(int((horizon - 2020) / LeapYearsInvestment))]
    Scenario = ["scenario" + str(i + 1) for i in range(NoOfScenarios)]
    peak_seasons = ["peak" + str(i + 1) for i in range(NoOfPeakSeason)]
    Season = regular_seasons + peak_seasons
    Operationalhour = [i + 1 for i in range(FirstHoursOfPeakSeason[-1] + len_peak_season - 1)]
    HoursOfRegSeason = [
        (s, h)
        for s in regular_seasons
        for h in Operationalhour
        if h
        in list(
            range(
                regular_seasons.index(s) * len_reg_season + 1,
                regular_seasons.index(s) * len_reg_season + len_reg_season + 1,
            )
        )
    ]
    HoursOfPeakSeason = [
        (s, h)
        for s in peak_seasons
        for h in Operationalhour
        if h
        in list(
            range(
                len_reg_season * len(regular_seasons) + peak_seasons.index(s) * len_peak_season + 1,
                len_reg_season * len(regular_seasons) + peak_seasons.index(s) * len_peak_season + len_peak_season + 1,
            )
        )
    ]
    HoursOfSeason = HoursOfRegSeason + HoursOfPeakSeason
    with open(run_config.empire_path / "config/countries.json", "r", encoding="utf-8") as file:
        dict_countries = json.load(file)

    logger.info("++++++++")
    logger.info("+EMPIRE+")
    logger.info("++++++++")
    logger.info("Load Change Module: %s", str(empire_config.load_change_module))
    logger.info("Solver: %s", empire_config.optimization_solver)
    logger.info("Scenario Generation: %s", str(use_scen_generation))
    logger.info("++++++++")
    logger.info("ID: %s", run_config.run_name)
    logger.info("++++++++")

    if use_scen_generation:
        if empire_config.use_fixed_sample and not (scenario_data_path / "sampling_key.csv").exists():
            raise ValueError("Missing 'sampling_key.csv' in ScenarioData folder.")
        else:
            generate_random_scenario(
                empire_config=empire_config,
                dict_countries=dict_countries,
                scenario_data_path=scenario_data_path,
                tab_file_path=tab_file_path,
            )

    else:
        if not empire_config.use_fixed_sample:
            logger.warning(
                "Both 'use_scen_generation' and 'use_fixed_sample' are set to False. "
                "Existing scenarios will be used, thus 'use_fixed_sample' should be True."
            )
        check_scenarios_exist_and_copy(run_config)

    generate_tab_files(file_path=workbook_path, tab_file_path=tab_file_path)

    if not test_run:
        run_empire(
            name=run_config.run_name,
            tab_file_path=tab_file_path,
            result_file_path=result_file_path,
            scenario_data_path=scenario_data_path,
            solver=empire_config.optimization_solver,
            temp_dir=empire_config.temporary_directory,
            FirstHoursOfRegSeason=FirstHoursOfRegSeason,
            FirstHoursOfPeakSeason=FirstHoursOfPeakSeason,
            lengthRegSeason=len_reg_season,
            lengthPeakSeason=len_peak_season,
            Period=Period,
            Operationalhour=Operationalhour,
            Scenario=Scenario,
            Season=Season,
            HoursOfSeason=HoursOfSeason,
            discountrate=discountrate,
            WACC=empire_config.wacc,
            LeapYearsInvestment=LeapYearsInvestment,
            IAMC_PRINT=empire_config.print_in_iamc_format,
            WRITE_LP=empire_config.write_in_lp_format,
            PICKLE_INSTANCE=empire_config.serialize_instance,
            EMISSION_CAP=empire_config.use_emission_cap,
            USE_TEMP_DIR=empire_config.use_temporary_directory,
            LOADCHANGEMODULE=empire_config.load_change_module,
            OPERATIONAL_DUALS=empire_config.compute_operational_duals,
        )

    config_path = run_config.dataset_path / "config.txt"
    logger.info("Writing config to: %s", config_path)
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(empire_config.to_dict(), file, ensure_ascii=False, indent=4)


def setup_run_paths(
    version: str,
    empire_config: EmpireConfiguration,
    run_path: Path,
    empire_path: Path = Path.cwd(),
) -> EmpireRunConfiguration:
    """
    Setup run paths for Empire.

    :param version: dataset version.
    :param empire_config: Empire configuration.
    :param run_path: Path containing input and output to the empire run.
    :param empire_path: Path to empire project, optional.
    :return: Empire run configuration.
    """

    # Original dataset
    base_dataset = empire_path / f"Data handler/{version}"

    # Input folders
    run_name = get_run_name(empire_config=empire_config, version=version)
    input_path = create_if_not_exist(run_path / "Input")
    xlsx_path = create_if_not_exist(input_path / "Xlsx")
    tab_path = create_if_not_exist(input_path / "Tab")
    scenario_data_path = create_if_not_exist(xlsx_path / "ScenarioData")

    # Copy base dataset to input folder
    copy_dataset(base_dataset, xlsx_path)
    copy_scenario_data(
        base_dataset=base_dataset,
        scenario_data_path=scenario_data_path,
        use_scenario_generation=empire_config.use_scenario_generation,
        use_fixed_sample=empire_config.use_fixed_sample,
    )

    # Output folders
    results_path = create_if_not_exist(run_path / "Output")

    return EmpireRunConfiguration(
        run_name=run_name,
        dataset_path=xlsx_path,
        tab_path=tab_path,
        scenario_data_path=scenario_data_path,
        results_path=results_path,
        empire_path=empire_path,
    )


def runner(data_managers):
    ## Read config and setup folders ##
    version = "europe_v51"
    # version = "test"

    if version == "test":
        config = read_config_file(Path("config/testmyrun.yaml"))
    else:
        config = read_config_file(Path("config/myrun.yaml"))

    empire_config = EmpireConfiguration.from_dict(config=config)

    run_config = setup_run_paths(version=version, empire_config=empire_config)

    ## Edit input data
    for manager in data_managers:
        manager.apply()

    ## Run empire
    run_empire_model(empire_config=empire_config, run_config=run_config)


if __name__ == "__main__":
    pass
