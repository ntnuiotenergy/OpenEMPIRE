from argparse import ArgumentParser
from pathlib import Path

from empire.config import EmpireConfiguration, read_config_file
from empire.input_client.client import EmpireInputClient
from empire.logger import get_empire_logger
from empire.model_runner import run_empire_model, setup_run_paths

parser = ArgumentParser(description="A CLI script to run the Empire model.")

parser.add_argument("-t", "--test-run", help="Test run without optimization", action="store_true")
parser.add_argument(
    "-d",
    "--dataset",
    help="Specify the required dataset",
    default="europe_v51",
    choices=["europe_v50", "europe_v51", "test"],
)

args = parser.parse_args()

## Read config and setup folders ##
if args.dataset == "test":
    config = read_config_file(Path("config/testrun.yaml"))
else:
    config = read_config_file(Path("config/run.yaml"))

empire_config = EmpireConfiguration.from_dict(config=config)

run_path = Path.cwd() / "Results/basic_run/dataset_{args.dataset}"

if (run_path / "Output/results_objective.csv").exists():
    raise ValueError("There already exists results for this analysis run.")

run_config = setup_run_paths(version=args.dataset, empire_config=empire_config, run_path=run_path)
logger = get_empire_logger(run_config=run_config)

logger.info("Running EMPIRE Model")

client = EmpireInputClient(dataset_path=run_config.dataset_path)

data_managers = [
    # Add input data managers to alter the dataset
]

## Run empire model
run_empire_model(
    empire_config=empire_config, run_config=run_config, data_managers=data_managers, test_run=args.test_run
)
