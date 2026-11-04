#!/bin/bash
#SBATCH --job-name=okkmer_3k_stop
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=36:00:00
set -euo pipefail
root="${OKKMER_STOP3_ROOT:-/scratch4/blangme2/sjhwang/ok_k_mer_experiments/timing/normal_stopping_3k}"
python="${OKKMER_PYTHON:-/scratch4/blangme2/sjhwang/ok_k_mer/.venv/bin/python}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec "$python" "$root/experiment.py" run --task-id "${SLURM_ARRAY_TASK_ID:?}"
