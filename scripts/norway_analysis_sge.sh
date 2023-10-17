#!/bin/bash
# This script will now serve as a job launcher

# Values for the arguments
NUCLEAR_CAPITAL_COSTS=("3000" "4000" "5000" "6000" "7000" "8000")
NUCLEAR_AVAILABILITIES=("0.75" "0.95")
MAX_WINDS=("0" "200000")

N_TASKS=$(( ${#NUCLEAR_CAPITAL_COSTS[@]} * ${#NUCLEAR_AVAILABILITIES[@]} * ${#MAX_WINDS[@]} ))

# Submit a job for each set of parameter values
for ncc in "${NUCLEAR_CAPITAL_COSTS[@]}"; do
    for na in "${NUCLEAR_AVAILABILITIES[@]}"; do
        for w in "${MAX_WINDS[@]}"; do
            qsub \
                -V \
                -cwd \
                -N empire_model_${ncc}_${na}_${w} \
                -o empire_model_${ncc}_${na}_${w}.out \
                -e empire_model_${ncc}_${na}_${w}.err \
                -l h_rt=12:00:00 \
                -l mem_free=150G \
                -l hostname="compute-4-55|compute-4-51|compute-4-52|compute-4-53|compute-4-54" \
                # -pe smp $N_TASKS \ # Parallel Environment PE, smp-multithreaded tasks on same node
                ./norway_analysis_sge_worker.sh $ncc $na $w
        done
    done
done
