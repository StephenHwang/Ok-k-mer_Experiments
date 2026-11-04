# Ok-k-mer search timings

Completed: 32/32 searches.

GNU time elapsed seconds and maximum RSS (KiB / 1,048,576 = GiB).
Only the CLI search is timed, including its input loading and result writing.
Installation, index preparation, Dashing2 and scheduler queue time are excluded.

| Dataset | Mode | Distances | Elapsed seconds | Peak RSS GiB |
|---|---|---|---:|---:|
| Aquificota | local | full | 83.40 | 0.1439 |
| Aquificota | global | full | 496.53 | 0.1523 |
| Aquificota | local | sketch | 80.89 | 0.1426 |
| Aquificota | global | sketch | 385.07 | 0.1518 |
| Bacillales_A | local | full | 95.59 | 0.1772 |
| Bacillales_A | global | full | 605.38 | 0.1866 |
| Bacillales_A | local | sketch | 108.43 | 0.1723 |
| Bacillales_A | global | sketch | 575.67 | 0.1822 |
| Caldisericia | local | full | 40.17 | 0.1327 |
| Caldisericia | global | full | 305.50 | 0.1378 |
| Caldisericia | local | sketch | 65.97 | 0.1301 |
| Caldisericia | global | sketch | 281.50 | 0.1409 |
| Chlamydiales | local | full | 139.72 | 0.1948 |
| Chlamydiales | global | full | 666.04 | 0.2068 |
| Chlamydiales | local | sketch | 86.28 | 0.1852 |
| Chlamydiales | global | sketch | 372.59 | 0.1949 |
| Cyanobacteriales | local | full | 280.96 | 0.3803 |
| Cyanobacteriales | global | full | 1400.15 | 0.3920 |
| Cyanobacteriales | local | sketch | 312.80 | 0.3474 |
| Cyanobacteriales | global | sketch | 1345.33 | 0.3577 |
| Neisseriaceae | local | full | 87.50 | 0.1453 |
| Neisseriaceae | global | full | 416.06 | 0.1538 |
| Neisseriaceae | local | sketch | 87.33 | 0.1452 |
| Neisseriaceae | global | sketch | 436.81 | 0.1529 |
| Anaerolineales | local | full | 369.52 | 0.3285 |
| Anaerolineales | global | full | 1608.08 | 0.3404 |
| Anaerolineales | local | sketch | 243.96 | 0.3055 |
| Anaerolineales | global | sketch | 1336.38 | 0.3130 |
| Dethiobacteria | local | full | 54.82 | 0.1351 |
| Dethiobacteria | global | full | 359.49 | 0.1434 |
| Dethiobacteria | local | sketch | 51.85 | 0.1342 |
| Dethiobacteria | global | sketch | 338.73 | 0.1462 |

One measurement per condition; no runtime variability estimate.
Early stopping enabled: False. All tasks request a maximum of three lengths.
