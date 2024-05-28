import os
import shutil
from argparse import ArgumentParser
from pathlib import Path

from empire.utils import get_name_of_last_folder_in_path

parser = ArgumentParser(description="A CLI script to run the Empire model.")

parser.add_argument(
    "-d",
    "--dataset",
    help="Specify the required dataset",
    default="europe_agg_v50",
)

parser.add_argument(
    "-rdir",
    "--results-directory",
    help="Specify the results directory for in sample runs",
    default="run_in_sample",
)

args = parser.parse_args()
dataset = args.dataset
results_dir = args.results_directory

# Get all runs
empire_path = Path.cwd()
results_path = empire_path / f"Results/{results_dir}/dataset_{dataset}"
all_run_paths = sorted([d for d in results_path.iterdir() if d.is_dir()])

new_results_path = empire_path / f"NewResults/{results_dir}/dataset_{dataset}"

exclude_files = ["results_output_Operational_resolved.csv", "results_output_curtailed_operational.csv",
                 "results_output_Operational.csv", "results_output_transmision_operational.csv"]

include_files = ["results_objective.csv"]

if not os.path.exists(new_results_path):
    os.makedirs(new_results_path)

for run_path in all_run_paths:
    run_config = get_name_of_last_folder_in_path(run_path)

    print(run_config)

    sgr_method = run_config.split("_")[0]
    num_scenarios = run_config.split("_")[1][3:]
    instance_num = run_config.split("_")[2]

    if not os.path.exists(new_results_path / sgr_method):
        os.makedirs(new_results_path / sgr_method)
    
    if not os.path.exists(new_results_path / sgr_method / num_scenarios):
        os.makedirs(new_results_path / sgr_method / num_scenarios)

    final_dest_folder = new_results_path / sgr_method / num_scenarios / instance_num

    if not os.path.exists(final_dest_folder):
        os.makedirs(final_dest_folder)

    # Iterate over files in the source folder
    for filename in os.listdir(run_path / "Output"):
        # Skip files in the exclude list
        #if filename in exclude_files:
        if filename in exclude_files:
            continue

        # Construct the full path of the item
        item_path = os.path.join(run_path / "Output", filename)
        
        if os.path.isfile(item_path):
            # Copy the file to the destination folder
            dest_path = os.path.join(final_dest_folder, filename)
            shutil.copy(item_path, dest_path)

    if instance_num == 30:
        print(f"Done with {sgr_method}-sce{num_scenarios}")
