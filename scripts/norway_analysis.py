from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from empire.config import EmpireConfiguration, read_config_file
from empire.input_client.client import EmpireInputClient
from empire.input_data_manager import (
    AvailabilityManager,
    CapitalCostManager,
    MaxInstalledCapacityManager,
)
from empire.logger import get_empire_logger
from empire.model_runner import run_empire_model, setup_run_paths


def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise ArgumentTypeError(f"{x} not in range [0.0, 1.0]")
    return x


parser = ArgumentParser(description="A CLI script to run the Empire model.")

parser.add_argument("-ncc", "--nuclear-capital-cost", help="Nuclear capacity cost", type=float, required=True)
parser.add_argument("-na", "--nuclear-availability", help="Nuclear availability", type=restricted_float, required=True)
parser.add_argument(
    "-w",
    "--max-onshore-wind-norway",
    help="Maximum installed onshore wind in Norwegian areas. If lower than initial, initial will be used.",
    type=float,
    required=True,
)
parser.add_argument(
    "-wg",
    "--max-offshore-wind-grounded-norway",
    help="Maximum installed offshore grounded wind in Norwegian areas. If lower than initial, initial will be used.",
    type=float,
    required=True,
)

parser.add_argument("-t", "--test-run", help="Test run without optimization", action="store_true")

args = parser.parse_args()

capital_cost = args.nuclear_capital_cost
nuclear_availability = args.nuclear_availability
max_onshore_wind_norway = args.max_onshore_wind_norway
max_offshore_wind_grounded_norway = args.max_offshore_wind_grounded_norway
version = "europe_v51"

## Read config and setup folders ##
config = read_config_file(Path("config/myrun.yaml"))
empire_config = EmpireConfiguration.from_dict(config=config)

run_path = Path.cwd() / "Results/norway_analysis/ncc{ncc}_na{na}_w{w}_wog{wog}".format(
    ncc=capital_cost, na=nuclear_availability, w=max_onshore_wind_norway, wog=max_offshore_wind_grounded_norway
)
run_config = setup_run_paths(version=version, empire_config=empire_config, run_path=run_path)
logger = get_empire_logger(run_config=run_config)

client = EmpireInputClient(dataset_path=run_config.dataset_path)

data_managers = [
    AvailabilityManager(client=client, generator="Nuclear", availability=nuclear_availability),
    CapitalCostManager(client=client, generator_technology="Nuclear", capital_cost=capital_cost),
    MaxInstalledCapacityManager(
        client=client,
        nodes=["NO1", "NO2", "NO3", "NO4", "NO5"],
        generator_technology="Wind_onshr",
        max_installed_capacity=max_onshore_wind_norway,
    ),
]

if max_offshore_wind_grounded_norway is not None:
    data_managers.append(
        MaxInstalledCapacityManager(
            client=client,
            nodes=["NO1", "NO2", "NO3", "NO4", "NO5"],
            generator_technology="Wind_offshr_grounded",
            max_installed_capacity=max_offshore_wind_grounded_norway,
        )
    )

logger.info("Running norway analysis with:")
logger.info(f"Nuclear capital cost: {capital_cost}")
logger.info(f"Nuclear availability: {nuclear_availability}")
logger.info(f"Max installed onshore wind per elspot area in Norway: {max_onshore_wind_norway}")
logger.info(f"Max installed grounded offshore wind per elspot area in Norway: {max_offshore_wind_grounded_norway}")
logger.info(f"Dataset version: {version}")

## Run empire model
run_empire_model(
    empire_config=empire_config, run_config=run_config, data_managers=data_managers, test_run=args.test_run
)
