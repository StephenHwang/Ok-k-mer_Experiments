# Local ±3 search up to four lengths

Completed 16/16 conditions; four lengths selected in 10 completed conditions.

| Dataset | Input | Selected lengths | Weights | Rho | Gain over prior best ≤3 | Four-length stage evaluated |
|---|---|---|---|---:|---:|---|
| Aquificota | full | [19, 20, 34] | [0.35, 0.4, 0.25] | 0.693164828 | 0.000000000 | True |
| Aquificota | sketch | [21, 22, 28, 29] | [0.2, 0.2, 0.4, 0.2] | 0.725575900 | 0.007377787 | True |
| Bacillales_A | full | [6, 7, 23, 24] | [0.15, 0.2, 0.4, 0.25] | 0.699403092 | 0.000003245 | True |
| Bacillales_A | sketch | [19, 23, 38, 39] | [0.3, 0.25, 0.25, 0.2] | 0.680501277 | 0.013796999 | True |
| Caldisericia | full | [20] | [1.0] | 0.773294249 | 0.000000000 | False |
| Caldisericia | sketch | [17, 22, 30, 33] | [0.15, 0.2, 0.35, 0.3] | 0.739832011 | 0.011754220 | True |
| Chlamydiales | full | [8, 10, 17, 22] | [0.3, 0.15, 0.3, 0.25] | 0.527610730 | 0.002174841 | True |
| Chlamydiales | sketch | [10, 19, 31, 34] | [0.35, 0.2, 0.2, 0.25] | 0.479866761 | 0.024556061 | True |
| Cyanobacteriales | full | [9, 10, 20] | [0.05, 0.2, 0.75] | 0.816261813 | 0.000000000 | True |
| Cyanobacteriales | sketch | [11, 18, 21, 32] | [0.35, 0.15, 0.2, 0.3] | 0.777061328 | 0.010943786 | True |
| Neisseriaceae | full | [10, 19] | [0.2, 0.8] | 0.910282111 | 0.000000000 | False |
| Neisseriaceae | sketch | [10, 18, 20, 21] | [0.15, 0.2, 0.5, 0.15] | 0.909279961 | 0.000753513 | True |
| Anaerolineales | full | [10, 20, 39] | [0.15, 0.8, 0.05] | 0.632583774 | 0.000000000 | True |
| Anaerolineales | sketch | [12, 18, 20, 23] | [0.25, 0.25, 0.2, 0.3] | 0.524861330 | 0.014566877 | True |
| Dethiobacteria | full | [20, 22] | [0.7, 0.3] | 0.700878210 | 0.000000000 | False |
| Dethiobacteria | sketch | [18, 19, 21, 30] | [0.2, 0.2, 0.3, 0.3] | 0.592036516 | 0.013288912 | True |

Standard early stopping is enabled. A stage must improve the current winner by more than 1e-12.
A skipped fourth stage means the algorithm stopped earlier; it does not establish that no four-length ensemble could improve rho.
Every evaluated four-length combination contains four distinct lengths with positive weights on the 0.05 grid.
Inputs are reused from the completed timing experiment; no Dashing2, installation, or index preparation is run.
