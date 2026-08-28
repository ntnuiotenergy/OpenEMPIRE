#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -V
#$ -o logs/empire_$JOB_ID.out
#$ -e logs/empire_$JOB_ID.err
#$ -l hostname="compute-4-51|compute-4-52|compute-4-53|compute-4-55|compute-4-56"

# Basic SGE script for running EMPIRE on Solstorm
# Can be executed directly (submits via qsub) or submitted manually with qsub
# Usage: sh run_empire_basic_sge.sh <dataset>
# Example: sh run_empire_basic_sge.sh test
# Or: qsub run_empire_basic_sge.sh test
# 
# Note: Jobs are restricted to high-memory nodes (500+ GB RAM) required for EMPIRE
# Available nodes: compute-4-51, compute-4-52, compute-4-53, compute-4-55, compute-4-56

# Get dataset parameter (default to 'test' if not provided)
DATASET=${1:-test}

# If not running as a job (no $JOB_ID), submit this script via qsub
if [ -z "$JOB_ID" ]; then
    echo "Submitting EMPIRE job for dataset: $DATASET"
    mkdir -p logs
    
    # High-memory nodes with 500+ GB RAM
    HIGH_MEM_NODES=("compute-4-51" "compute-4-52" "compute-4-53" "compute-4-55" "compute-4-56")
    
    echo "Checking availability of high-memory nodes..."
    
    # Find the least loaded node
    BEST_NODE=""
    MIN_LOAD=999999
    
    for node in "${HIGH_MEM_NODES[@]}"; do
        # Check if node is in queue output (busy with jobs)
        JOBS_ON_NODE=$(qstat -u "*" 2>/dev/null | grep "${node}" | wc -l)
        
        # Ensure it's a number
        if ! [[ "$JOBS_ON_NODE" =~ ^[0-9]+$ ]]; then
            JOBS_ON_NODE=0
        fi
        
        if [ "$JOBS_ON_NODE" -lt "$MIN_LOAD" ]; then
            MIN_LOAD=$JOBS_ON_NODE
            BEST_NODE=$node
        fi
        
        echo "  ${node}: ${JOBS_ON_NODE} jobs"
    done
    
    if [ -z "$BEST_NODE" ]; then
        echo "ERROR: No suitable node found!"
        exit 1
    fi
    
    echo "Selected node: ${BEST_NODE} (${MIN_LOAD} jobs)"
    echo "Submitting job..."
    
    # Submit to the selected node
    qsub -l hostname=${BEST_NODE} $0 $DATASET
    echo "Job submitted to ${BEST_NODE}. Use 'qstat' to monitor status."
    exit 0
fi

echo "================================================"
echo "EMPIRE Basic Run on Solstorm"
echo "================================================"
echo "Job ID: $JOB_ID"
echo "Hostname: $(hostname)"
echo "Dataset: $DATASET"
echo "Start time: $(date)"
echo "================================================"

# Create logs directory if it doesn't exist
mkdir -p logs

# Load required modules
echo "Loading modules..."
# Don't load Python module - use conda environment's Python instead
module load gurobi/12.0

# Initialize conda
eval "$(/home/$USER/miniconda3/bin/conda shell.bash hook)"

# Check if empire_env exists and activate or create it
echo "Checking for empire_env..."
if [[ "$CONDA_DEFAULT_ENV" != "empire_env" ]]; then
    # Check if empire_env exists among the installed environments
    conda info --envs | grep -q "empire_env"
    if [ $? -eq 0 ]; then
        echo "Activating existing conda environment: empire_env"
        conda activate empire_env
    else
        echo "Creating new conda environment: empire_env"
        echo "This is a one-time setup and may take several minutes..."
        conda env create -f ./environment.yml
        conda activate empire_env
        echo "Environment creation complete!"
    fi
else
    echo "empire_env should be active now."
fi

# Verify that we are actually in the correct environment
if [[ "$CONDA_DEFAULT_ENV" != "empire_env" ]]; then
    echo "ERROR: Failed to activate empire_env!"
    echo "Current environment: $CONDA_DEFAULT_ENV"
    echo "Please check conda installation and environment configuration."
    exit 1
fi
echo "✓ Successfully activated empire_env"

# Verify environment
echo "Python version: $(python --version)"
echo "Conda environment: $CONDA_DEFAULT_ENV"

# Run EMPIRE
echo "================================================"
echo "Starting EMPIRE run with dataset: $DATASET"
echo "================================================"

# Add force flag for test dataset to overwrite previous results
FORCE_FLAG=""
if [[ "$DATASET" == "test" ]]; then
    FORCE_FLAG="-f"
fi

python scripts/run.py -d $DATASET $FORCE_FLAG

EXIT_CODE=$?

echo "================================================"
echo "EMPIRE run completed"
echo "Exit code: $EXIT_CODE"
echo "End time: $(date)"
echo "================================================"

exit $EXIT_CODE
