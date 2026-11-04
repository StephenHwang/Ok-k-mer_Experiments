# Ok-k-mer search timing: eight datasets × four conditions

This experiment times the updated public `okkmer search` executable from the
sibling `ok_k_mer` repository. There are **32 searches**, one measurement each:

- local ±3, full-set distances
- local ±3, sketch distances
- global, full-set distances
- global, sketch distances

All use inclusive k=6–40, weight step 0.05, and maximum ensemble size three.
The benchmark defaults to `--no-early-stop`, explicitly evaluating stages 1, 2,
and 3 even if a preceding stage does not improve rho. The final recommendation
can still contain fewer than three lengths. This option does not change the
weight grid, scoring, or candidate search space at any stage. Without the
option the public CLI retains its standard early-stopping behavior. The plan
command's `--early-stopping` switch selects that standard policy instead.
The chosen policy is frozen in `experiment.json` before scheduling.

## What is timed

GNU `/usr/bin/time` wraps only the `okkmer search` process. Its elapsed wall
seconds include Python startup, loading the prepared index, reference-distance
calculation, optimization, and writing search result files. They exclude
installation, Dashing2, index preparation, wrapper provenance collection,
report compilation, and scheduler queue time.

Peak memory is GNU time's maximum resident set size, **KiB / 1,048,576 = GiB**.
It is measured process RSS, not Slurm's memory allocation. User/system CPU
seconds and process exit status are also retained. Single measurements do not
provide runtime uncertainty estimates.

## Inputs and provenance

Exact/full inputs are selected per k from the validated
`dashing_timing/no_sketching/20261101/all_datasets_by_k.tsv` compilation under
`/vast/blangme2/sjhwang/ok_k_mer_data`. Cyanobacteriales spans multiple retries;
its successful source is selected separately for each k.

Sketch inputs come from `dashing_timing/with_sketching/`
`run_20261103T153050Z_tvb1_8j9`: full SetSketch with **4,096 registers**.
Both inputs use Jaccard distances, not similarities. Each native CLI index
records all 35 source checksums. Matrix symlinks and exact genome maps are under
`inputs/`; original matrices are never modified.

The confirmed Anaerolineales accession aliases are applied. Dethiobacteria
excludes its two unavailable tree leaves and retains 102 genomes. The new
Neisseriaceae matrices contain 147 genomes, including `GCA_030146515.1` and
`GCA_017991555.1`, which are absent from the reference tree; these two are
excluded from both conditions to retain the manuscript's 145 genomes.
All other datasets use the tree's complete genome set.

`code_snapshot/` freezes the updated package source and its uncommitted diff;
the timed command is the actual installed `.venv/bin/okkmer` entry point with
`PYTHONPATH` pointing to that identical source snapshot. This prevents later
edits to the development checkout from changing queued experiments. Source,
entry-point, index and tree hashes, package versions, node CPU information,
commands, Slurm IDs, affinity, and native thread limits are recorded.

## Execution

From this folder, use the package’s existing environment at
`../../ok_k_mer/.venv/bin/python`.

```bash
../../ok_k_mer/.venv/bin/python benchmark.py plan
../../ok_k_mer/.venv/bin/python benchmark.py submit
```

`submit` schedules three jobs and saves all commands/responses in
`submissions/jobs.json`:

1. **16 preparation tasks**: build one index per dataset/input type, outside
   the timer; 1 CPU, 8 GB, 2 hours, concurrency four.
2. **32 search tasks** after successful preparation: 8 CPUs, 32 GB, 36 hours
   per search, concurrency 32.
3. **Summary job** after the search array ends, including failures.

Only the package's search threads use eight CPUs. BLAS/OpenMP/NumExpr worker
counts are fixed at one to prevent nested native-thread oversubscription.
No subtree annotation or full weight-grid export is requested.
Existing indices, task directories, and submission receipts are protected
against accidental overwriting. Do not submit the same experiment twice.

## Outputs

- `experiment.json`, `tasks.tsv`, `inputs.tsv`: frozen plan and source mapping.
- `indices/`: 16 prepared distance indices, built before timing.
- `runs/`: one directory per search, with `gnu_time.tsv`, `measurement.json`,
  `invocation.json`, stdout/stderr, CPU details, and full native search outputs.
- `search_timings.tsv`: per-search elapsed seconds, peak RSS GiB, result, and
  status. Missing or interrupted measurements are never treated as successes.
- `stage_recommendations.tsv`: best rho/lengths/weights and combination counts
  at every evaluated ensemble size.
- `REPORT.md`: readable completed timing table.
- `logs/`, `preparation/`, `submissions/`: scheduler logs and execution receipts.

Refresh partial results at any time with:

```bash
../../ok_k_mer/.venv/bin/python benchmark.py collect
```

The search array throttle was raised from 8 to 32 while running. The change and
verification are recorded in `submissions/scheduler_updates.jsonl`. Original
submission receipts retain the initial throttle; per-search start times and
host placement remain recorded.

## Comparison tables

`make_tables.py` reads the completed timing and stage summaries and writes:

- `tables/timing_memory.{md,tsv,tex}`: eight datasets, with time and peak RSS
  GiB for each of the four search/input conditions.
- `tables/ensemble_comparison.{md,tsv,tex}`: 32 condition rows comparing the
  best single-, two-, and three-length ensembles, weights, and Spearman rho.

Markdown displays time as min:sec and memory to three decimals. TSV files
retain unrounded numeric values. The LaTeX timing table requires booktabs;
the ensemble table also requires longtable and may benefit from landscape
orientation. Exact-size stage winners can differ from the final recommendation.

Regenerate with `../../ok_k_mer/.venv/bin/python make_tables.py` from this folder.
