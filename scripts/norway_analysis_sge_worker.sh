#!/bin/bash
ncc=$1
na=$2
w=$3
p=$4

# Load modules and activate conda environment
module load gurobi/10.0

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

if [ "$p" == "true" ]; then
    python scripts/norway_analysis.py \
        --nuclear-capital-cost $ncc \
        --nuclear-availability $na \
        --max-onshore-wind-norway $w \
        --max-offshore-wind-grounded-norway $w \
        -p
else:
    python scripts/norway_analysis.py \
        --nuclear-capital-cost $ncc \
        --nuclear-availability $na \
        --max-onshore-wind-norway $w \
        --max-offshore-wind-grounded-norway $w
fi
