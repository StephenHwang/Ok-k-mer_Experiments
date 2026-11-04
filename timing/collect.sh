#!/bin/bash
#SBATCH --job-name=okkmer_timing_summary
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:30:00
set -euo pipefail
root="${OKKMER_TIMING_ROOT:-/scratch4/blangme2/sjhwang/ok_k_mer_experiments/timing}"
python="${OKKMER_TIMING_PYTHON:-/scratch4/blangme2/sjhwang/ok_k_mer/.venv/bin/python}"
exec "$python" "$root/benchmark.py" collect
