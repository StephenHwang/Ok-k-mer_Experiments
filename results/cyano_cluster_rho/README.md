# Cyano near-optimal ensemble analysis

Submitted Slurm job: 32839230. All new scripts and outputs are confined here;
main scripts and source data are read only.

The saved historical three-k tensor used a 0.1 weight step, so this job reruns
two- and three-k searches on the cached Cyano dataframe with the current 0.05
weight step. Previous matching three-k baseline rho: 0.816261814480166.

`run.sh` saves raw tensors and provenance JSONs then runs `analyze.py`.
`REPORT.md` and `summary.json` contain final counts; `all_unique_triples.csv`,
`better_than_two.csv`, and `within_delta.csv` enumerate combinations and their
best weights/rhos. To change the tolerance after completion:

```
/home/shwang45/miniconda3/envs/python310/bin/python results/cyano_cluster_rho/analyze.py --delta 0.005
```

Only three distinct k values with positive weights count. Permutations and
alternative weights are collapsed. The search matches Ok-k-mer's restricted
first-k window (17–23), with the other two lengths in 6–40; it does not evaluate
triples entirely outside that window. The two comparison criteria are independent.
