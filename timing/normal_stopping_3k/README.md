# Search timing with normal early stopping (maximum three lengths)

Thirty-two fresh measurements: eight datasets × local ±3/global search ×
full/sketched inputs. This repeats the parent timing experiment's four
conditions with **normal early stopping enabled in every search**.

Settings: `--max-kmers 3 --k-low 6 --k-high 40 --w-step 0.05`, eight workers,
and default improvement tolerance 1e-12. Local runs use `--local 3`; global
runs use `--global`. **The `--no-early-stop` flag is never passed.**

After completing a stage, the search stops if that stage's best rho does not
improve the current recommendation by more than 1e-12. A failed two-length
stage skips triples entirely; a failed three-length stage retains the previous
recommendation. Evaluated sizes and stopping reasons are recorded per run.

Existing native indices from `../indices/` are reused. Trees, explicit genome
exclusions and confirmed mappings are inherited from the completed original
benchmark. There is no Dashing2 run, installation, or index rebuilding. The
previous forced-through-three timings and manuscript files are preserved.

GNU `/usr/bin/time` wraps only the search invocation, including startup, index
loading, tree-distance calculation, optimization, and result writing. It excludes
wrapper bookkeeping, preprocessing and queue time. Peak RSS GiB is GNU time's
KiB divided by 1,048,576. Wall seconds, CPU seconds, RSS, node and Slurm IDs
are retained. There is one measurement per condition.

Source is frozen in `code_snapshot/`, with revision, diff, versions and hashes
recorded. Reached stages are checked against the previous benchmark's scores,
lengths and weights before a run is marked successful. Runtime can vary with
shared-cluster load as well as the stopping policy.

## Slurm resources and outputs

All 32 searches may run concurrently, with 8 CPUs, 32 GB and a 36-hour limit per
search. BLAS/OpenMP/NumExpr workers are fixed at one; Ok-k-mer uses eight search
workers. A dependent summary job runs after the array ends, including failures.

- `manifest.json`, `tasks.tsv`: frozen settings and reused input paths.
- `runs/`: native results, GNU-time TSV, stdout/stderr, CPU info, invocation
  and measurement JSONs.
- `search_timings.tsv`: statuses, elapsed seconds, peak memory GiB,
  recommendations, evaluated stages and stopping reasons.
- `stage_recommendations.tsv`: every evaluated stage's best ensemble.
- `REPORT.md`: readable progress and results.
- `timing_memory.{md,tsv}`: final eight-dataset, four-condition timing table.
- `submissions/jobs.json`, `logs/`: scheduler receipts and logs.

From this directory, refresh partial results with:

```bash
../../../ok_k_mer/.venv/bin/python experiment.py collect
```

Existing task outputs and submission receipts are protected from overwriting.
