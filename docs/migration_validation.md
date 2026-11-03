# Repository split validation

Source repository commit: `fee3cf9fd8ea8c12ef9113c20b0b58f2588623f2`.
The new repository starts independent history from its extracted working tree;
the original repository retains the complete earlier Git history.

- 877 files/symlinks were inventoried before moving. Original hashes and paths
  are recorded in `migration.json`; code paths were then updated for relocation.
- The external `/vast/blangme2/sjhwang/ok_k_mer_data` directory was not moved or
  modified. The local data and stability-result symlinks retain their targets.
- 287 historical JSON, CSV, NPY, NPZ, PDF, and PNG result files were checked
  against pre-move SHA-256 hashes; all matched.
- A temporary-manifest collection read all 2 two-length and 212 three-length
  added-dataset results successfully. Its CSVs were written under `/tmp`,
  leaving the historical results intact.
- Both near-optimal-ensemble regression tests passed after moving.
- All four preexisting stability tests passed after moving. Added relocation
  checks verify component-boundary matching and read-only manifest handling.
- The Dethiobacteria dataset wrapper prepared a complete index and passed the
  public CLI's dry-run validation from this separate repository.
- All 12 public-package tests passed in the original package checkout after
  removing its experiment code, local data symlink, and result tree.

Selected final PDF plots, compact analysis tables, reports, configurations,
and scripts are versioned. Large result arrays, raw data, and logs remain
local. Historical recorded paths and source hashes intentionally retain their
original values. Old absolute paths embedded in notebook code were updated;
notebook outputs were preserved.
