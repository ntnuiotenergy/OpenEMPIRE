#!/bin/bash
# This script will now serve as a job launcher

# Values for the arguments
NUCLEAR_CAPITAL_COSTS=("3000" "4000" "5000" "6000" "7000" "8000")
NUCLEAR_AVAILABILITIES=("0.75" "0.95")
MAX_WINDS=("0" "200000")
PROTECTIVE=("false" "true")

mkdir -p ./hpc_output/

# Submit a job for each set of parameter values
for ncc in "${NUCLEAR_CAPITAL_COSTS[@]}"; do
    for na in "${NUCLEAR_AVAILABILITIES[@]}"; do
        for w in "${MAX_WINDS[@]}"; do
            for p in "${PROTECTIVE[@]}"; do
                qsub \
                    -V \
                    -cwd \
                    -N empire_model_${ncc}_${na}_${w}_${p} \
                    -o ./hpc_output/ \
                    -e ./hpc_output/\
                    -l h_rt=12:00:00 \
                    -l mem_free=150G \
                    -l hostname="compute-4-51|compute-4-52|compute-4-53|compute-4-55|compute-4-56" \
                    -pe smp 8 \
                    ./scripts/run_analysis_sge_worker.sh $ncc $na $w $p
            done
        done
    done
done
