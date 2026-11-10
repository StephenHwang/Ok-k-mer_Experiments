# Ok-k-mer manuscript docs
Assorted docmentation on these files.

## Layout

- `configs/datasets.json`: the eight manuscript datasets, explicit input
  semantics, confirmed accession mappings, and missing-genome exclusions.
- `workflows/`: manuscript dataset searches and legacy-score validation using
  the separately installed CLI.
- `bin/`: preserved grid searches, masking simulations, and Slurm wrappers.
- `src/`: legacy figure helpers, notebooks, and saved node annotations.
- `results/`: existing experiment results, including near-optimal ensemble
  analyses and final figure/table exports; large generated artifacts are local.
- `data/`: local symlink to the unchanged external raw-data directory.
- `migration.json`: original repository commit, file hashes, symlink targets,
  and original paths recorded before the repository split.

## Environment

Use Python 3.10 or newer. With sibling checkouts:

```bash
python -m pip install -e '../ok_k_mer[plot]'
python -m pip install -r requirements.txt
```

In this workspace the package's existing environment can be used directly:

```bash
../ok_k_mer/.venv/bin/python workflows/run_dataset.py \
    --dataset Chlamydiales --threads 8 --output results/cli_chlamydiales
```

Alternatively, pass `--okkmer-source ../ok_k_mer` when using another Python
that has the required dependencies but not an installed package. This explicit
option applies only to `run_dataset.py`.

Inputs are documented in `configs/datasets.json`. Recreate the local `data`
symlink if working on another machine. Large inputs are not bundled in Git.
See [the experiment inventory](docs/inventory.md) for figures, tables, and
preserved workflow entry points, and [scientific compatibility](docs/compatibility.md)
for differences between legacy algorithms and the public CLI.

## Existing runs and relocation

Historical JSON, CSV, and tensor files preserve their recorded values and
absolute paths. `bin/stability/stability.py` resolves the pre-split root to
this checkout in memory when reading manifests and results. New runs record
new paths. The original data directory under `/vast` is unchanged.

Slurm wrappers default to this workspace's experiments checkout. Override
`STABILITY_BIN` (masking arrays) or `OKKMER_EXPERIMENTS_ROOT` (grid-search
wrappers) when using another checkout; near-optimal `run.sh` scripts can also
be edited for a different installation. Historical job receipts retain their
original command lines as provenance.

All existing local results were moved here. Git tracks code, configurations,
node-annotation TSVs, and selected compact analysis reports and tables. Raw
matrices, tensors, logs, and large generated figures remain local and ignored.
Exploratory files previously ignored under `src/old_exploration` remain local.

## Checks

```bash
../ok_k_mer/.venv/bin/python -m unittest discover -s bin/stability -p 'test_*.py' -v
../ok_k_mer/.venv/bin/python results/chlam_cluster_rho/test_analysis.py
../ok_k_mer/.venv/bin/python results/cyano_cluster_rho/test_analysis.py
```

No workflow modifies the manuscript directory. This repository has no GitHub
remote until one is explicitly configured.
