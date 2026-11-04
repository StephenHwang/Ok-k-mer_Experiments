#!/usr/bin/env python3
"""Time local ±3 and global searches with normal stopping and at most three lengths."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

HERE=Path(__file__).resolve().parent
TIMING=HERE.parent
REPO=HERE.parent.parent.parent/'ok_k_mer'


def stamp():return datetime.now(timezone.utc).isoformat()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.partial')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temporary.replace(path)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def tsv(path,rows):
    keys=list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,delimiter='\t');w.writeheader();w.writerows(rows)
def env():
    result=dict(os.environ)
    result.update(PYTHONPATH=str(HERE/'code_snapshot/src'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
                  MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',LC_ALL='C')
    return result


def setup(args):
    if (HERE/'manifest.json').exists():raise ValueError('Already prepared')
    source=read(TIMING/'experiment.json')
    for name in ('runs','logs','submissions','inputs'):(HERE/name).mkdir()
    snapshot=HERE/'code_snapshot';snapshot.mkdir()
    shutil.copytree(REPO/'src/okkmer',snapshot/'src/okkmer',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(REPO/'pyproject.toml',snapshot/'pyproject.toml')
    (snapshot/'working_tree.patch').write_text(subprocess.check_output(['git','diff','HEAD'],cwd=REPO,text=True))
    tasks=[]
    for previous in source['tasks']:
        item=source['inputs'][previous['input_id']]
        old=read(Path(previous['output'])/'search/run.json')
        dataset_dir=HERE/'inputs'/item['dataset'];dataset_dir.mkdir(exist_ok=True)
        tree=dataset_dir/'reference.nwk';exclusions=dataset_dir/'excluded_genomes.txt'
        if not tree.exists():
            shutil.copy2(item['tree'],tree);shutil.copy2(item['exclude_genomes'],exclusions)
        task={'task_id':len(tasks),'dataset':item['dataset'],'distance_type':item['distance_type'],
              'mode':previous['mode'],'delta_k':3 if previous['mode']=='local' else None,
              'n_genomes':item['n_genomes'],'tree':str(tree),'tree_sha256':sha(tree),
              'exclude_genomes':str(exclusions),'exclude_sha256':sha(exclusions),'index':item['index'],
              'index_manifest_sha256':sha(Path(item['index'])/'manifest.json'),
              'baseline_run':str(Path(previous['output'])/'search/run.json'),
              'baseline_run_sha256':sha(Path(previous['output'])/'search/run.json'),
              'baseline_recommendation':old['recommendation'],'baseline_stages':old['stages']}
        task['output']=str(HERE/'runs'/f"{task['task_id']:02d}_{task['dataset']}_{task['distance_type']}_{task['mode']}")
        tasks.append(task)
    if len(tasks)!=32:raise ValueError('Expected 32 dataset/mode/input conditions')
    manifest={'schema_version':1,'created_utc':stamp(),'executable':str(REPO/'.venv/bin/okkmer'),
              'executable_sha256':sha(REPO/'.venv/bin/okkmer'),
              'snapshot_sha256':{str(p.relative_to(HERE)):sha(p) for p in snapshot.rglob('*') if p.is_file()},
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
              'versions':json.loads(subprocess.check_output([sys.executable,'-c',
                  'import json,platform,numpy,scipy,ete3,matplotlib;print(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,ete3=ete3.__version__,matplotlib=matplotlib.__version__)))'],text=True)),
              'modes':['local','global'],'local_delta_k':3,'max_kmers':3,'k_low':6,'k_high':40,
              'w_step':.05,'improvement_tol':1e-12,'early_stopping':True,'threads':8,'tasks':tasks}
    write(HERE/'manifest.json',manifest)
    tsv(HERE/'tasks.tsv',[{k:t[k] for k in ['task_id','dataset','mode','distance_type','n_genomes','index','output']} for t in tasks])
    collect(None)
    print('Prepared 32 local ±3/global searches with maximum three lengths; standard early stopping.')


def verify(manifest,task):
    for rel,expected in manifest['snapshot_sha256'].items():
        if sha(HERE/rel)!=expected:raise ValueError(f'Code snapshot changed: {rel}')
    for path,expected in [(manifest['executable'],manifest['executable_sha256']),
                          (task['tree'],task['tree_sha256']),
                          (task['exclude_genomes'],task['exclude_sha256']),
                          (Path(task['index'])/'manifest.json',task['index_manifest_sha256'])]:
        if sha(path)!=expected:raise ValueError(f'Input or executable changed: {path}')


def run(args):
    manifest=read(HERE/'manifest.json');task=manifest['tasks'][args.task_id];verify(manifest,task)
    out=Path(task['output']);out.mkdir(exist_ok=False)
    cmd=[manifest['executable'],'search','--tree',task['tree'],'--index',task['index'],
         '--exclude-genomes',task['exclude_genomes'],'--max-kmers','3',
         '--k-low','6','--k-high','40','--w-step','0.05','--improvement-tol','1e-12',
         '--threads','8','--output',str(out/'search')]
    cmd += ['--local','3'] if task['mode']=='local' else ['--global']
    record={'task':task,'command':cmd,'started_utc':stamp(),'hostname':socket.gethostname(),
            'slurm_job_id':os.environ.get('SLURM_JOB_ID'),'slurm_array_job_id':os.environ.get('SLURM_ARRAY_JOB_ID'),
            'slurm_array_task_id':os.environ.get('SLURM_ARRAY_TASK_ID'),
            'cpu_affinity':sorted(os.sched_getaffinity(0)),'versions':manifest['versions']}
    write(out/'invocation.json',record)
    (out/'cpuinfo.txt').write_text(Path('/proc/cpuinfo').read_text())
    timing=out/'gnu_time.tsv'
    timing.write_text('elapsed_seconds\tuser_seconds\tsystem_seconds\tpeak_rss_kib\texit_status\n')
    timed=['/usr/bin/time','--quiet','--append','--output',str(timing),'--format','%e\t%U\t%S\t%M\t%x',*cmd]
    with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
        result=subprocess.run(timed,stdout=stdout,stderr=stderr,env=env())
    with timing.open() as f:values=list(csv.DictReader(f,delimiter='\t'))
    if len(values)!=1:raise ValueError('Missing GNU time result')
    record.update(finished_utc=stamp(),returncode=result.returncode,
                  elapsed_seconds=float(values[0]['elapsed_seconds']),peak_rss_kib=int(values[0]['peak_rss_kib']),
                  peak_rss_gib=int(values[0]['peak_rss_kib'])/1048576,
                  user_seconds=float(values[0]['user_seconds']),system_seconds=float(values[0]['system_seconds']))
    if result.returncode==0:
        data=read(out/'search/run.json')
        if data['n_genomes']!=task['n_genomes'] or data['max_kmers']!=3 or not data['early_stopping']:
            raise ValueError('Unexpected search parameters')
        baseline={s['ensemble_size']:s['best'] for s in task['baseline_stages']}
        for stage in data['stages']:
            if stage['ensemble_size']>3:continue
            expected=baseline[stage['ensemble_size']]
            if expected['ks']!=stage['best']['ks'] or expected['weights']!=stage['best']['weights'] or abs(expected['rho']-stage['best']['rho'])>1e-12:
                raise ValueError('A one-to-three-length stage changed relative to the previous search')
        record.update(recommendation=data['recommendation'],stages=data['stages'],stop_reason=data['stop_reason'])
    write(out/'measurement.json',record)
    if result.returncode:raise RuntimeError(f'Search failed: {out}/stderr.log')
    print(task['dataset'],task['distance_type'],'selected',record['recommendation']['ks'],record['recommendation']['rho'])


def collect(args):
    manifest=read(HERE/'manifest.json');rows=[];stage_rows=[]
    for task in manifest['tasks']:
        row={key:task[key] for key in ['task_id','dataset','mode','distance_type','n_genomes']}
        row.update(status='not_completed',output=task['output'])
        path=Path(task['output'])/'measurement.json'
        if path.exists():
            data=read(path)
            row.update(status='complete' if data['returncode']==0 else 'failed',
                       elapsed_seconds=data['elapsed_seconds'],peak_rss_kib=data['peak_rss_kib'],
                       peak_rss_gib=data['peak_rss_gib'],user_seconds=data['user_seconds'],
                       system_seconds=data['system_seconds'],slurm_job_id=data['slurm_job_id'],hostname=data['hostname'])
            if data['returncode']==0:
                best=data['recommendation']
                row.update(selected_size=best['ensemble_size'],ks=json.dumps(best['ks']),weights=json.dumps(best['weights']),
                           rho=best['rho'],evaluated_sizes=','.join(str(s['ensemble_size']) for s in data['stages']),
                           stop_reason=data['stop_reason'],early_stopping=True,max_kmers=3,delta_k=task['delta_k'],threads=8)
                for stage in data['stages']:
                    b=stage['best'];stage_rows.append(dict(task_id=task['task_id'],dataset=task['dataset'],mode=task['mode'],distance_type=task['distance_type'],
                        ensemble_size=stage['ensemble_size'],n_combinations=stage['n_combinations'],ks=json.dumps(b['ks']),weights=json.dumps(b['weights']),rho=b['rho']))
        elif (Path(task['output'])/'invocation.json').exists():row['status']='started_or_interrupted'
        rows.append(row)
    tsv(HERE/'search_timings.tsv',rows)
    if stage_rows:tsv(HERE/'stage_recommendations.tsv',stage_rows)
    complete=[r for r in rows if r['status']=='complete']
    def elapsed(value):
        seconds=round(value);return f'{seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d}'
    lines=['# Local ±3 and global timing with normal early stopping (maximum three lengths)','',
           f'Completed {len(complete)}/32 conditions.','',
           '| Dataset | Mode | Input | Runtime (hh:mm:ss) | Peak RSS (GiB) | Selected lengths | Rho | Evaluated sizes |',
           '|---|---|---|---:|---:|---|---:|---|']
    for r in complete:lines.append(f"| {r['dataset']} | {r['mode']} | {r['distance_type']} | {elapsed(r['elapsed_seconds'])} | {r['peak_rss_gib']:.4f} | {r['ks']} | {r['rho']:.9f} | {r['evaluated_sizes']} |")
    lines+=['','Each search uses k=6–40, weight step 0.05 and eight threads.',
            'Standard early stopping is enabled: the search stops after a stage that fails to improve rho by more than 1e-12.',
            'GNU time measures the search invocation only, including input loading and result writing; installation, Dashing2 and index preparation are excluded.',
            'Peak RSS is converted from KiB to GiB by dividing by 1,048,576. Each condition is measured once.']
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
    if len(complete)==32:
        by={(r['dataset'],r['mode'],r['distance_type']):r for r in complete}
        order=['Anaerolineales','Aquificota','Bacillales_A','Caldisericia','Chlamydiales','Cyanobacteriales','Dethiobacteria','Neisseriaceae']
        wide=[];formatted=[]
        for dataset in order:
            row={'dataset':dataset,'n_genomes':by[(dataset,'local','full')]['n_genomes']}
            human=[f"{dataset} ({row['n_genomes']})"]
            for mode,kind in [('local','full'),('local','sketch'),('global','full'),('global','sketch')]:
                value=by[(dataset,mode,kind)];stem=mode+'_'+kind
                row.update({stem+'_elapsed_seconds':value['elapsed_seconds'],stem+'_peak_rss_gib':value['peak_rss_gib'],
                            stem+'_runtime_hhmmss':elapsed(value['elapsed_seconds']),stem+'_evaluated_sizes':value['evaluated_sizes']})
                human += [elapsed(value['elapsed_seconds']),f"{value['peak_rss_gib']:.3f}"]
            wide.append(row);formatted.append(human)
        tsv(HERE/'timing_memory.tsv',wide)
        lines=['# Search timing and memory: normal early stopping','',
               '| Dataset (genomes) | Local full time | Local full GiB | Local sketch time | Local sketch GiB | Global full time | Global full GiB | Global sketch time | Global sketch GiB |',
               '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        lines+=['| '+' | '.join(row)+' |' for row in formatted]
        (HERE/'timing_memory.md').write_text('\n'.join(lines)+'\n')
    print(f'Collected {len(complete)}/32 successful search timings.')


def submit(args):
    receipt=HERE/'submissions/jobs.json'
    if receipt.exists():raise ValueError('Submission receipt already exists; inspect before retrying')
    record={'created_utc':stamp(),'commands':[],'jobs':{}};write(receipt,record)
    for name,flags in [('search',['--array=0-31%32']),('collect',[])]:
        if name=='collect':flags=[f"--dependency=afterany:{record['jobs']['search']}"]
        cmd=['sbatch','--parsable',f'--output={HERE}/logs/{name}_%A_%a.out',f'--error={HERE}/logs/{name}_%A_%a.err',*flags,str(HERE/f'{name}.sh')]
        record['commands'].append(cmd);write(receipt,record)
        result=subprocess.run(cmd,text=True,capture_output=True)
        record.setdefault('responses',[]).append(dict(stdout=result.stdout,stderr=result.stderr,returncode=result.returncode));write(receipt,record)
        if result.returncode:raise RuntimeError(result.stderr)
        match=re.fullmatch(r'(\d+)(?:;[^\s]+)?',result.stdout.strip())
        if not match:raise RuntimeError('Unexpected scheduler response; inspect receipt before retrying')
        record['jobs'][name]=match.group(1);write(receipt,record)
    print(json.dumps(record['jobs'],indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('setup','submit','collect'):sub.add_parser(name)
    p_run=sub.add_parser('run');p_run.add_argument('--task-id',type=int,required=True)
    args=p.parse_args();globals()[args.command](args)

if __name__=='__main__':main()
