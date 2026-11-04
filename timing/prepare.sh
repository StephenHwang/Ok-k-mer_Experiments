#!/bin/bash
#SBATCH --job-name=okkmer_prepare
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00
set -euo pipefail
root="${OKKMER_TIMING_ROOT:-/scratch4/blangme2/sjhwang/ok_k_mer_experiments/timing}"
python="${OKKMER_TIMING_PYTHON:-/scratch4/blangme2/sjhwang/ok_k_mer/.venv/bin/python}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec "$python" "$root/benchmark.py" prepare --task-id "${SLURM_ARRAY_TASK_ID:?}"
