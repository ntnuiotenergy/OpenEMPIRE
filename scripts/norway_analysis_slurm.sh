#!/bin/bash
#SBATCH --partition=CPUQ
#SBATCH --job-name=empire_model
#SBATCH --output=empire_model_%j.out
#SBATCH --error=empire_model_%j.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=200G
#SBATCH --array=1-24%6

# Load any necessary modules
module load Anaconda/2022.10

# Check if empire_env is the active environment
if [[ "$CONDA_DEFAULT_ENV" != "empire_env" ]]; then
    # Check if empire_env exists among the installed environments
    conda info --envs | grep -q "empire_env"
    if [ $? -eq 0 ]; then
        source $(dirname $(which conda))/activate empire_env
    else
        conda env create -f ./environment.yml
        source $(dirname $(which conda))/activate empire_env
        conda install -c gurobi gurobi -y
    fi
fi

# Define different values for arguments
NUCLEAR_CAPITAL_COSTS=("3000" "4000" "5000" "6000" "7000" "8000")
NUCLEAR_AVAILABILITIES=("0.75" "0.95")
MAX_WINDS=("0" "200000")

# Loop and run the script with different values
for ncc in "${NUCLEAR_CAPITAL_COSTS[@]}"; do
    for na in "${NUCLEAR_AVAILABILITIES[@]}"; do
        for w in "${MAX_WINDS[@]}"; do
            python run_empire_model.py \
                --nuclear-capital-cost $ncc \
                --nuclear-availability $na \
                --max-onshore-wind-norway $w \
                --max-offshore-wind-grounded-norway $w \
                --test-run
        done
    done
done
