# Local ±3 and global timing with normal early stopping (maximum three lengths)

Completed 32/32 conditions.

| Dataset | Mode | Input | Runtime (hh:mm:ss) | Peak RSS (GiB) | Selected lengths | Rho | Evaluated sizes |
|---|---|---|---:|---:|---|---:|---|
| Aquificota | local | full | 00:01:45 | 0.1416 | [19, 20, 34] | 0.693164828 | 1,2,3 |
| Aquificota | global | full | 00:05:14 | 0.1501 | [19, 20, 34] | 0.693164828 | 1,2,3 |
| Aquificota | local | sketch | 00:01:07 | 0.1400 | [21, 22, 28] | 0.718198113 | 1,2,3 |
| Aquificota | global | sketch | 00:08:56 | 0.1508 | [21, 22, 28] | 0.718198113 | 1,2,3 |
| Bacillales_A | local | full | 00:02:09 | 0.1754 | [7, 23, 24] | 0.699399847 | 1,2,3 |
| Bacillales_A | global | full | 00:12:56 | 0.1856 | [7, 23, 24] | 0.699399847 | 1,2,3 |
| Bacillales_A | local | sketch | 00:02:37 | 0.1710 | [19, 23, 39] | 0.666704278 | 1,2,3 |
| Bacillales_A | global | sketch | 00:10:24 | 0.1838 | [19, 23, 39] | 0.666704278 | 1,2,3 |
| Caldisericia | local | full | 00:00:12 | 0.1285 | [20] | 0.773294249 | 1,2 |
| Caldisericia | global | full | 00:00:14 | 0.1291 | [20] | 0.773294249 | 1,2 |
| Caldisericia | local | sketch | 00:01:08 | 0.1276 | [17, 22, 30] | 0.728077791 | 1,2,3 |
| Caldisericia | global | sketch | 00:05:15 | 0.1373 | [17, 22, 30] | 0.728077791 | 1,2,3 |
| Chlamydiales | local | full | 00:02:30 | 0.1932 | [9, 17, 22] | 0.525435890 | 1,2,3 |
| Chlamydiales | global | full | 00:11:21 | 0.2023 | [9, 17, 22] | 0.525435890 | 1,2,3 |
| Chlamydiales | local | sketch | 00:02:26 | 0.1878 | [10, 19, 31] | 0.455310700 | 1,2,3 |
| Chlamydiales | global | sketch | 00:09:49 | 0.1976 | [10, 19, 31] | 0.455310700 | 1,2,3 |
| Cyanobacteriales | local | full | 00:06:32 | 0.3778 | [9, 10, 20] | 0.816261813 | 1,2,3 |
| Cyanobacteriales | global | full | 00:34:38 | 0.3848 | [9, 10, 20] | 0.816261813 | 1,2,3 |
| Cyanobacteriales | local | sketch | 00:07:09 | 0.3470 | [11, 20, 32] | 0.766117542 | 1,2,3 |
| Cyanobacteriales | global | sketch | 00:30:52 | 0.3602 | [11, 20, 32] | 0.766117542 | 1,2,3 |
| Neisseriaceae | local | full | 00:01:56 | 0.1464 | [10, 19] | 0.910282111 | 1,2,3 |
| Neisseriaceae | global | full | 00:07:13 | 0.1544 | [10, 19] | 0.910282111 | 1,2,3 |
| Neisseriaceae | local | sketch | 00:01:37 | 0.1459 | [10, 18, 20] | 0.908526448 | 1,2,3 |
| Neisseriaceae | global | sketch | 00:07:19 | 0.1541 | [10, 18, 20] | 0.908526448 | 1,2,3 |
| Anaerolineales | local | full | 00:06:17 | 0.3201 | [10, 20, 39] | 0.632583774 | 1,2,3 |
| Anaerolineales | global | full | 00:27:22 | 0.3365 | [10, 20, 39] | 0.632583774 | 1,2,3 |
| Anaerolineales | local | sketch | 00:04:17 | 0.3049 | [16, 18, 23] | 0.510294452 | 1,2,3 |
| Anaerolineales | global | sketch | 00:22:29 | 0.3123 | [16, 18, 23] | 0.510294452 | 1,2,3 |
| Dethiobacteria | local | full | 00:01:04 | 0.1367 | [20, 22] | 0.700878210 | 1,2,3 |
| Dethiobacteria | global | full | 00:06:50 | 0.1450 | [20, 22] | 0.700878210 | 1,2,3 |
| Dethiobacteria | local | sketch | 00:01:02 | 0.1354 | [18, 19, 21] | 0.578747605 | 1,2,3 |
| Dethiobacteria | global | sketch | 00:06:35 | 0.1467 | [18, 19, 21] | 0.578747605 | 1,2,3 |

Each search uses k=6–40, weight step 0.05 and eight threads.
Standard early stopping is enabled: the search stops after a stage that fails to improve rho by more than 1e-12.
GNU time measures the search invocation only, including input loading and result writing; installation, Dashing2 and index preparation are excluded.
Peak RSS is converted from KiB to GiB by dividing by 1,048,576. Each condition is measured once.
