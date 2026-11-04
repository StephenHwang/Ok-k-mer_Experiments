#!/bin/bash
#SBATCH --job-name=okkmer_local4_summary
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
set -euo pipefail
root="${OKKMER_LOCAL4_ROOT:-/scratch4/blangme2/sjhwang/ok_k_mer_experiments/local_4k}"
exec /scratch4/blangme2/sjhwang/ok_k_mer/.venv/bin/python "$root/experiment.py" collect
