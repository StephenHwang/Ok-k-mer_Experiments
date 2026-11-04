#!/usr/bin/env python3
"""Create timing/memory and exact-size ensemble comparison tables."""
import argparse
import csv
import json
from pathlib import Path

ORDER = ['Anaerolineales','Aquificota','Bacillales_A','Caldisericia','Chlamydiales','Cyanobacteriales','Dethiobacteria','Neisseriaceae']
LABELS = ['o__Anaerolineales','p__Aquificota','o__Bacillales_A','c__Caldisericia','o__Chlamydiales','o__Cyanobacteriales','c__Dethiobacteria','f__Neisseriaceae']
CONDITIONS = [('local','full','Local full'),('local','sketch','Local sketch'),('global','full','Global full'),('global','sketch','Global sketch')]


def read(path):
    with path.open() as f:return list(csv.DictReader(f,delimiter='\t'))


def tsv(path,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t')
        writer.writeheader();writer.writerows(rows)


def markdown(path,headers,rows,description):
    lines=[description,'','| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']
    lines+=['| '+' | '.join(map(str,row))+' |' for row in rows]
    path.write_text('\n'.join(lines)+'\n')


def elapsed(seconds):
    value=round(float(seconds))
    return f'{value//60}:{value%60:02d}'


def weights(value):return ', '.join(f'{float(x):.2f}' for x in json.loads(value))
def lengths(value):return ', '.join(map(str,json.loads(value)))
def escape(value):return str(value).replace('_',r'\_').replace('%',r'\%')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    args=p.parse_args();root=args.root
    timings=read(root/'search_timings.tsv');stages=read(root/'stage_recommendations.tsv')
    if len(timings)!=32 or any(r['status']!='complete' for r in timings):raise ValueError('Require all 32 completed timings')
    timing={(r['dataset'],r['mode'],r['distance_type']):r for r in timings}
    stage={(r['dataset'],r['mode'],r['distance_type'],int(r['ensemble_size'])):r for r in stages}
    if len(timing)!=32 or len(stage)!=96 or len(stages)!=96:raise ValueError('Duplicate or missing condition/stage rows')
    for name in ORDER:
        for kind in ('full','sketch'):
            for size in (1,2,3):
                local=float(stage[(name,'local',kind,size)]['rho'])
                global_rho=float(stage[(name,'global',kind,size)]['rho'])
                if global_rho < local-1e-12:raise ValueError('Global score below local score')
                if size==1 and abs(global_rho-local)>1e-12:raise ValueError('Single-length scores differ by search mode')
    out=root/'tables';out.mkdir(exist_ok=True)
    timing_rows=[];timing_md=[];timing_tex=[];ensemble_rows=[];ensemble_md=[];ensemble_tex=[]
    for name,label in zip(ORDER,LABELS):
        n=int(timing[(name,'local','full')]['n_genomes'])
        display=f'{label} ({n})'
        human=[display];raw={'dataset':label,'n_genomes':n};tex=[escape(display)]
        for mode,kind,title in CONDITIONS:
            r=timing[(name,mode,kind)]
            if int(r['n_genomes'])!=n or r['evaluated_sizes']!='1,2,3':raise ValueError('Inconsistent coverage')
            if abs(float(r['peak_rss_gib'])-int(r['peak_rss_kib'])/1048576)>1e-12:raise ValueError('Memory unit mismatch')
            stem=f'{mode}_{kind}'
            raw.update({stem+'_time_mmss':elapsed(r['elapsed_seconds']),stem+'_elapsed_seconds':r['elapsed_seconds'],stem+'_peak_rss_gib':r['peak_rss_gib']})
            human += [elapsed(r['elapsed_seconds']),f"{float(r['peak_rss_gib']):.3f}"]
            tex += human[-2:]
            row={'dataset':label,'n_genomes':n,'condition':title,'mode':mode,'distance_type':kind}
            comparison=[display,title];texcomparison=[escape(display),title]
            for size in (1,2,3):
                s=stage[(name,mode,kind,size)]
                ks=json.loads(s['ks']);ws=json.loads(s['weights'])
                if len(ks)!=size or len(set(ks))!=size or len(ws)!=size or min(ws)<=0 or abs(sum(ws)-1)>1e-10:
                    raise ValueError('Invalid exact-size ensemble')
                row.update({f'{size}k_lengths':s['ks'],f'{size}k_weights':s['weights'],f'{size}k_rho':s['rho'],f'{size}k_n_combinations':s['n_combinations']})
                cell=lengths(s['ks'])+(f" ({weights(s['weights'])})" if size>1 else '')
                comparison += [cell,f"{float(s['rho']):.6f}"]
                texcell=lengths(s['ks']) if size==1 else r'\shortstack[l]{'+lengths(s['ks'])+r'\\('+weights(s['weights'])+')}'
                texcomparison += [texcell,f"{float(s['rho']):.6f}"]
            ensemble_rows.append(row);ensemble_md.append(comparison);ensemble_tex.append(texcomparison)
        timing_rows.append(raw);timing_md.append(human);timing_tex.append(tex)
    tsv(out/'timing_memory.tsv',timing_rows)
    headers=['Dataset (genomes)']
    for _,_,title in CONDITIONS:headers += [title+' time',title+' GiB']
    markdown(out/'timing_memory.md',headers,timing_md,
             '# Search timing and peak memory\n\nTime is minutes:seconds, rounded to the nearest second. Memory is peak RSS in GiB, rounded to three decimals. GNU time measures only the search CLI; installation, Dashing2, and index preparation are excluded. TSV retains unrounded measurements.')
    tsv(out/'ensemble_comparison.tsv',ensemble_rows)
    markdown(out/'ensemble_comparison.md',['Dataset (genomes)','Condition','One length','ρ₁','Two lengths (weights)','ρ₂','Three lengths (weights)','ρ₃'],ensemble_md,
             '# Best ensembles by exact ensemble size\n\nEach condition is shown separately. Weights follow the listed ascending lengths; single-length weight is 1.00. Each m-length ensemble has exactly m distinct lengths with positive weights. These are the best candidates within the specified global or local ±3 search space; the final overall recommendation may use fewer lengths. All stages 1–3 were evaluated, using k=6–40 and a 0.05 weight grid. Rhos are rounded to six decimals here; the TSV retains their precision.')
    lines=[r'% Requires booktabs. Time: min:sec. Peak memory: GiB.',r'\begin{tabular}{lrrrrrrrr}',r'\toprule',
           r'Dataset (genomes) & \multicolumn{2}{c}{Local full} & \multicolumn{2}{c}{Local sketch} & \multicolumn{2}{c}{Global full} & \multicolumn{2}{c}{Global sketch} \\',
           r'\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}',
           r' & Time & GiB & Time & GiB & Time & GiB & Time & GiB \\',r'\midrule']
    lines += [' & '.join(row)+r' \\' for row in timing_tex]
    lines += [r'\bottomrule',r'\end{tabular}']
    (out/'timing_memory.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'% Requires booktabs and longtable. Consider a landscape page for this table.',r'\begin{longtable}{lllr lrlr}',r'\toprule',
           r'Dataset (genomes) & Condition & One length & $\rho_1$ & Two lengths (weights) & $\rho_2$ & Three lengths (weights) & $\rho_3$ \\',r'\midrule',r'\endhead']
    lines += [' & '.join(row)+r' \\' for row in ensemble_tex]
    lines += [r'\bottomrule',r'\end{longtable}']
    (out/'ensemble_comparison.tex').write_text('\n'.join(lines)+'\n')
    print('Wrote 8 timing rows and 32 ensemble comparisons (96 stage results) to',out)

if __name__=='__main__':main()
