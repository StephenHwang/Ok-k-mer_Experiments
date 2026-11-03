# Chlamydiales near-optimal ensemble analysis

Submitted Slurm job: 32839369. All new scripts and outputs are confined here;
main scripts and source data are read only.

This job reruns two- and three-k searches on the cached Chlamydiales
dataframe with the current 0.05 weight step, matching the Cyano analysis. Previous matching three-k baseline rho: 0.5254358897547535.

`run.sh` saves raw tensors and provenance JSONs then runs `analyze.py`.
`REPORT.md` and `summary.json` contain final counts; `all_unique_triples.csv`,
`better_than_two.csv`, and `within_delta.csv` enumerate combinations and their
best weights/rhos. To change the tolerance after completion:

```
/home/shwang45/miniconda3/envs/python310/bin/python results/chlam_cluster_rho/analyze.py --delta 0.005
```

Only three distinct k values with positive weights count. Permutations and
alternative weights are collapsed. The search matches Ok-k-mer's restricted
first-k window (17–23), with the other two lengths in 6–40; it does not evaluate
triples entirely outside that window. The two comparison criteria are independent.
