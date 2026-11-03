# Cyano near-optimal ensembles

Best two-length rho: 0.815903026139
Best three-length rho: 0.816261814480

- Unique triples strictly better than the best two-length ensemble: 2
- Unique triples within 0.005 rho of the best three-length ensemble: 77
- Unique triples evaluated: 3269

Each unordered triple contains three distinct lengths, all with positive weights.
Weights are optimized over the original 0.05 grid; permutations and alternative
weights do not create additional combinations. Reported rho reverses the
original optimizer's sign, matching the manuscript. The second count includes
the optimum itself and uses an inclusive threshold (numerical tolerance 1e-12).

Scope: k=6–40, at least one k in the data-driven first-k window [17, 18, 19, 20, 21, 22, 23].
These counts describe the Ok-k-mer search space, not an unrestricted search
of all triples. Raw result JSONs record input/code hashes and search settings.
