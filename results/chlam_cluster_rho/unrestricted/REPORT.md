# Chlamydiales unrestricted near-optimal ensembles

Best two-length rho: 0.513214363293
Best three-length rho: 0.525435889755

- Unique triples strictly better than the best two-length ensemble: 164
- Unique triples within 0.005 rho of the best three-length ensemble: 58
- Unique triples evaluated: 6545

Each unordered triple contains three distinct lengths, all with positive weights.
Weights are optimized over the original 0.05 grid; permutations and alternative
weights do not create additional combinations. Reported rho reverses the
original optimizer's sign, matching the manuscript. The second count includes
the optimum itself and uses an inclusive threshold (numerical tolerance 1e-12).

Scope: all unordered triples of distinct lengths from k=6–40, with no
first-k window restriction. Weights remain on the discrete 0.05 grid. Raw result JSONs record input/code hashes and search settings.
