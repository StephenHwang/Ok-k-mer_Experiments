#!/bin/bash
#SBATCH --job-name=okkmer_3k_summary
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
set -euo pipefail
root="${OKKMER_STOP3_ROOT:-/scratch4/blangme2/sjhwang/ok_k_mer_experiments/timing/normal_stopping_3k}"
exec /scratch4/blangme2/sjhwang/ok_k_mer/.venv/bin/python "$root/experiment.py" collect
