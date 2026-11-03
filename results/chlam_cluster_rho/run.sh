#!/bin/bash
#SBATCH --job-name=chlam_cluster_rho
#SBATCH --partition=shared
#SBATCH --account=blangme2
#SBATCH --time=36:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
root=/scratch4/blangme2/sjhwang/ok_k_mer_experiments
out="$root/results/chlam_cluster_rho"
python=/home/shwang45/miniconda3/envs/python310/bin/python
for n in 2 3; do
    if [[ ! -f "$out/$([[ $n == 2 ]] && echo two || echo three).json" ]]; then
        if [[ $n == 2 ]]; then stem=two; else stem=three; fi
        "$python" "$root/bin/stability/grid_search_${n}k.py" \
            --tree-path "$root/data/chlamydiales/o__Chlamydiales.nwk" \
            --merged-csv "$root/data/chlamydiales/grid_search/chlamydia_merged_df.csv" \
            --dataset Chlamydia --masking-fraction 0 --seed 682185521938335537 \
            --k-low 6 --k-high 40 --w-step 0.05 --s 3 --threads 8 \
            --json-out "$out/$stem.json" --save-npy "$out/$stem.npy"
    fi
done
"$python" "$out/analyze.py"
