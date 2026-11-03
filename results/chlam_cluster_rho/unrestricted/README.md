# Unrestricted Chlamydiales ensemble analysis

All 6,545 unordered triples from k=6–40; three distinct lengths and positive
weights on the 0.05 grid. Uses the original optimizer with s=34 so every
first length is evaluated. Reuses the completed full two-length baseline.
Original restricted results are preserved in the parent directory.

Primary near-optimal count is relative to the new unrestricted optimum.
summary.json and all_unique_triples.csv also retain the count/indicator
relative to the previous restricted optimum for direct comparison.

Expected runtime: approximately 6–8 hours based on the prior 78-minute
three-k search and a fivefold increase in first-k candidates, plus queue time.

Submitted Slurm job: 32841775.
