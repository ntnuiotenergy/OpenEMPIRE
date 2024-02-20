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
        echo "Activating existing conda environment: empire_env"
        source ~/miniconda3/bin/activate empire_env
    else
        echo "Creating new conda environment: empire_env"
        conda env create -f ./environment.yml
        source ~/miniconda3/bin/activate empire_env
        conda install -c gurobi gurobi -y
    fi
fi

echo "Active conda env: "
echo $CONDA_DEFAULT_ENV

if [ "$p" == "true" ]; then
    echo "Protective case"
    python scripts/run_analysis.py \
        --nuclear-capital-cost $ncc \
        --nuclear-availability $na \
        --max-onshore-wind-norway $w \
        --max-offshore-wind-grounded-norway $w \
        -p
else
    echo "Not protective case"
    python scripts/run_analysis.py \
        --nuclear-capital-cost $ncc \
        --nuclear-availability $na \
        --max-onshore-wind-norway $w \
        --max-offshore-wind-grounded-norway $w
fi

echo "Done with starting bash script!"