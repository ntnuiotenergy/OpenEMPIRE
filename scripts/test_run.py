from argparse import ArgumentParser
from pathlib import Path

from empire.config import EmpireConfiguration, read_config_file
from empire.logger import get_empire_logger
from empire.model_runner import run_empire_model, setup_run_paths

parser = ArgumentParser(description="A CLI script to run a test dataset of the Empire model.")

parser.add_argument("-t", "--test-run", help="Test run without optimization", action="store_true")

args = parser.parse_args()

version = "test"

## Read config and setup folders ##
config = read_config_file(Path("config/testmyrun.yaml"))
empire_config = EmpireConfiguration.from_dict(config=config)

run_path = Path.cwd() / "Results/test"
run_config = setup_run_paths(version=version, empire_config=empire_config, run_path=run_path)
logger = get_empire_logger(run_config=run_config)

logger.info("Running test run.")

## Run empire model
run_empire_model(empire_config=empire_config, run_config=run_config, data_managers=[], test_run=args.test_run)
