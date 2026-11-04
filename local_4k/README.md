# Local ±3 searches with up to four lengths

Runs the updated public `okkmer` executable on all eight manuscript datasets,
for both full-set and sketched inputs: sixteen searches. Existing prepared
indices from `../timing/indices/` are reused. No Dashing2 or installation is run.

Settings: `--local 3 --max-kmers 4 --k-low 6 --k-high 40 --w-step 0.05`,
eight threads, default improvement tolerance 1e-12. **Standard early stopping
is enabled**: adding a length must improve the current recommendation by more
than that tolerance. Conditions that stop before four are explicitly reported.
The prior full-set Caldisericia, Dethiobacteria, and Neisseriaceae results are
expected to stop early. A skipped fourth stage does not exclude the existence
of better four-length ensembles outside that progressive path.

At each evaluated four-length stage, lengths are distinct, weights are positive,
and weights sum to one on the 0.05 grid (969 weight assignments per combination).
Local candidates vary every length from the preceding stage within ±3, while
the additional length spans the complete 6–40 range.

The package source is frozen in `code_snapshot/`. The actual installed executable
uses that source via PYTHONPATH. Input/index/tree hashes and the baseline
one-to-three-length recommendation are recorded in `manifest.json`. Every
repeated stage is checked against its previous result before a run is marked
successful. Confirmed genome maps/exclusions are inherited from the timing run.

The Slurm array permits all sixteen tasks concurrently, with 8 CPUs, 32 GB,
and 36 hours per task. A dependent summary runs after all tasks end. GNU time
records elapsed seconds and peak RSS GiB for the search command only.

Outputs:

- `summary.tsv` and `REPORT.md`: whether four lengths were selected, their
  weights/rho, gain over the previous best ≤3, and early-stopping status.
- `stage_recommendations.tsv`: every evaluated stage, including its candidate count.
- `runs/`: native search outputs, logs, command/provenance, and GNU time measurements.
- `submissions/jobs.json`: scheduler job IDs and raw responses.

From this directory:

```bash
../../ok_k_mer/.venv/bin/python experiment.py collect
```

The scripts reject existing task directories or submission receipts rather than
overwrite completed results. No manuscript files are modified.
