from argparse import ArgumentParser
from pathlib import Path

from empire.core.config import EmpireConfiguration, read_config_file
from empire.core.model_runner import run_empire_model, setup_run_paths
from empire.logger import get_empire_logger

parser = ArgumentParser(description="A CLI script to run the Empire model.")

parser.add_argument(
    "-d",
    "--dataset",
    help="Specify the required dataset",
    default="europe_v51",
)

parser.add_argument("-f", "--force", help="Force new run if old exist.", action="store_true")
parser.add_argument("-c", "--config-file", help="Path to config file.", default="config/run.yaml")

# SGR: 'basic', 'filter', 'moment'
parser.add_argument("-r", "--routine", help="Scenario generation routine ('basic', 'filter', 'moment')", required=True)

# Tree size
parser.add_argument("-ns", "--num-scenarios", help="Number of scenarios/tree size", type=int, required=True)

# How many instances to solve to obtain mean and SD
parser.add_argument("-ni", "--num-instances", help="Number of instances", type=int, default=30)

args = parser.parse_args()
dataset=args.dataset

## Read config and setup folders ##
config = read_config_file(Path(args.config_file))
empire_config = EmpireConfiguration.from_dict(config=config)

routine = args.routine
num_scenarios = args.num_scenarios
num_instances = args.num_instances

# For SGR routines add extra detail to output-folder / name
routine_detail = ""
if routine == "moment":
    routine_detail = f"moment{empire_config.n_tree_compare}"
elif routine == "filter":
    routine_detail = f"filter{empire_config.n_cluster}"
else:
    routine_detail = "basic"

# Modifications to config
empire_config.use_scenario_generation = True
empire_config.use_fixed_sample = False
empire_config.number_of_scenarios = num_scenarios

if routine == "filter":
    empire_config.moment_matching = False
    empire_config.filter_use = True
elif routine == "moment":
    empire_config.moment_matching = True
    empire_config.filter_use = False
else: 
    empire_config.moment_matching = False
    empire_config.filter_use = False

# Run script
for i in range(1, num_instances + 1):
    run_path = Path.cwd() / "Results/run_in_sample/dataset_{ds}/{r}_sce{ns}_{i}".format(
                ds=dataset,
                r=routine_detail,
                ns=num_scenarios,
                i=i
            )

    if (run_path / "Output/results_objective.csv").exists() and not args.force:
        raise ValueError("There already exists results for this analysis run.")

    run_config = setup_run_paths(version=dataset, empire_config=empire_config, run_path=run_path)
    logger = get_empire_logger(run_config=run_config)
    logger.info("Running EMPIRE Model")

    ## Run empire model
    run_empire_model(
        empire_config=empire_config, run_config=run_config, data_managers=[], test_run=False
    )
