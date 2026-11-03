#!/usr/bin/env python3
"""Count unordered, strictly three-length ensembles in the original search grid."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--delta', type=float, default=0.005)
    args = parser.parse_args()
    if args.delta < 0:
        parser.error('delta must be nonnegative')
    three = json.loads((HERE/'three.json').read_text())
    two = json.loads((HERE/'two.json').read_text())
    tensor = np.load(HERE/'three.npy', mmap_mode='r')
    ks = list(range(three['k_low'], three['k_high']+1))
    main_ks = list(range(max(ks[0],three['k_main']-three['s']),min(ks[-1],three['k_main']+three['s'])+1))
    ws = np.round(np.arange(0,1+three['w_step'],three['w_step']),3)
    assert tensor.shape == (len(main_ks),len(ks),len(ks),len(ws),len(ws))
    valid = (ws[:,None]>0)&(ws[None,:]>0)&((1-ws[:,None]-ws[None,:])>1e-10)
    best = {}
    for i,a in enumerate(main_ks):
        for j,b in enumerate(ks):
            for l,c in enumerate(ks):
                if len({a,b,c}) != 3:
                    continue
                values = np.where(valid, tensor[i,j,l], np.inf)
                flat = np.argmin(values)
                u,v = np.unravel_index(flat,values.shape)
                rho = -float(values[u,v])
                if not np.isfinite(rho):
                    continue
                key = tuple(sorted((a,b,c)))
                weights = dict(zip((a,b,c),(ws[u],ws[v],1-ws[u]-ws[v])))
                if key not in best or rho > best[key]['rho']:
                    best[key] = dict(zip(('k1','k2','k3'),key),rho=rho,
                                     **{f'w{n+1}':float(weights[k]) for n,k in enumerate(key)})
    rows = pd.DataFrame(best.values()).sort_values(['rho','k1','k2','k3'],ascending=[False,True,True,True])
    optimum = -three['correlation']
    threshold = -two['correlation']
    rows['gap_to_optimum'] = optimum-rows.rho
    rows['better_than_best_two'] = rows.rho > threshold
    rows['within_delta'] = rows.gap_to_optimum <= args.delta + 1e-12
    rows.to_csv(HERE/'all_unique_triples.csv',index=False)
    rows[rows.better_than_best_two].to_csv(HERE/'better_than_two.csv',index=False)
    rows[rows.within_delta].to_csv(HERE/'within_delta.csv',index=False)
    summary = {'best_two_rho':threshold,'best_three_rho':optimum,'delta':args.delta,
               'unique_three_length_combinations':len(rows),
               'better_than_best_two':int(rows.better_than_best_two.sum()),
               'within_delta_of_best_three':int(rows.within_delta.sum()),
               'k_range':ks,'first_k_search_window':main_ks,'weight_step':three['w_step']}
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (HERE/'REPORT.md').write_text(f'''# Chlamydiales near-optimal ensembles

Best two-length rho: {threshold:.12f}
Best three-length rho: {optimum:.12f}

- Unique triples strictly better than the best two-length ensemble: {summary['better_than_best_two']}
- Unique triples within {args.delta} rho of the best three-length ensemble: {summary['within_delta_of_best_three']}
- Unique triples evaluated: {len(rows)}

Each unordered triple contains three distinct lengths, all with positive weights.
Weights are optimized over the original 0.05 grid; permutations and alternative
weights do not create additional combinations. Reported rho reverses the
original optimizer's sign, matching the manuscript. The second count includes
the optimum itself and uses an inclusive threshold (numerical tolerance 1e-12).

Scope: k=6–40, at least one k in the data-driven first-k window {main_ks}.
These counts describe the Ok-k-mer search space, not an unrestricted search
of all triples. Raw result JSONs record input/code hashes and search settings.
''')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
