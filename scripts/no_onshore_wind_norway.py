from pathlib import Path

from Empire.config import EmpireConfiguration, read_config_file
from Empire.input_client.client import EmpireInputClient
from Empire.input_data_manager import (
    AvailabilityManager,
    CapitalCostManager,
    MaxInstalledCapacityManager,
)
from Empire.model_runner import run_empire_model, setup_run_paths

## Read config and setup folders ##
capital_cost = 3000
version = "europe_v51"
config = read_config_file(Path("config/myrun.yaml"))

empire_config = EmpireConfiguration.from_dict(config=config)
run_config = setup_run_paths(version=version, empire_config=empire_config)

client = EmpireInputClient(dataset_path=run_config.dataset_path)

data_managers = [
    AvailabilityManager(client=client, generator="Nuclear", availability=0.95),
    CapitalCostManager(
        client=client, generator_technology="Nuclear", capital_cost=capital_cost
    ),
    MaxInstalledCapacityManager(
        client=client,
        nodes=["NO1", "NO2", "NO3", "NO4", "NO5"],
        generator_technology="Wind_offshr_grounded",
        max_installed_capacity=0.0,
    ),
    MaxInstalledCapacityManager(
        client=client,
        nodes=["NO1", "NO2", "NO3", "NO4", "NO5"],
        generator_technology="Wind_onshr",
        max_installed_capacity=0.0, # No more than already built
    ),
]

## Run empire model
run_empire_model(
    empire_config=empire_config, run_config=run_config, data_managers=data_managers
)

