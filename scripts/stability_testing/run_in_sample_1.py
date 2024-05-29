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
    default="europe_agg_v50",
)

parser.add_argument("-f", "--force", help="Force new run if old exist.", action="store_true")
parser.add_argument("-c", "--config-file", help="Path to config file.", default="config/aggrun.yaml")

args = parser.parse_args()
dataset = args.dataset

## Read config and setup folders ##
config = read_config_file(Path(args.config_file))
empire_config = EmpireConfiguration.from_dict(config=config)

routine = "copula"
num_scenarios = 100
num_instances = 5
start_instance = 1

# For SGR routines add extra detail to output-folder / name
routine_detail = ""
if routine == "moment":
    routine_detail = f"moment{empire_config.n_tree_compare}"
elif routine == "filter":
    routine_detail = f"filter{empire_config.n_cluster}"
elif routine == "copula":
    routine_detail = f"copula{empire_config.n_cluster}"
else:
    routine_detail = "basic"

# Modifications to config
empire_config.use_scenario_generation = True
empire_config.use_fixed_sample = False
empire_config.number_of_scenarios = num_scenarios

# If routine = 'filter' or 'copula', make sure filters are created once beforehand
# This can be done by a basic run on the dataset with the desired number of clusters and the parameters below set to 'True'
empire_config.filter_make = False
empire_config.copula_clusters_make = False

if routine == "filter":
    empire_config.moment_matching = False
    empire_config.filter_use = True
    empire_config.copula_clusters_use = False
elif routine == "moment":
    empire_config.moment_matching = True
    empire_config.filter_use = False
    empire_config.copula_clusters_use = False
elif routine == "copula":
    empire_config.moment_matching = False
    empire_config.filter_use = False
    empire_config.copula_clusters_use = True
else: 
    empire_config.moment_matching = False
    empire_config.filter_use = False
    empire_config.copula_clusters_use = False


# Run script
for i in range(start_instance, start_instance + num_instances):

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
