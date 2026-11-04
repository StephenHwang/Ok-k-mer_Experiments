#!/usr/bin/env python3
"""Prepare fixed inputs and time the public Ok-k-mer search executable in Slurm."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
DATA = Path('/vast/blangme2/sjhwang/ok_k_mer_data')
FULL_TABLE = DATA/'dashing_timing/no_sketching/20261101/all_datasets_by_k.tsv'
SKETCH = DATA/'dashing_timing/with_sketching/run_20261103T153050Z_tvb1_8j9'


def stamp(): return datetime.now(timezone.utc).isoformat()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def write_json(path,value):
    path=Path(path);temporary=path.with_name(path.name+'.partial')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temporary.replace(path)

def read_json(path): return json.loads(Path(path).read_text())

def table(path):
    with Path(path).open() as f:return list(csv.DictReader(f,delimiter='\t'))

def write_table(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys,delimiter='\t');writer.writeheader();writer.writerows(rows)

def labels(path):
    with Path(path).open() as f:
        for line in f:
            if line.startswith('#Sources\t'):return line.rstrip('\r\n').split('\t')[1:]
    raise ValueError(f'Missing #Sources: {path}')

def accession(label):
    match=re.match(r'GC[AF]_\d+\.\d+',Path(label).name)
    if not match:raise ValueError(f'Unrecognized genome label: {label}')
    return match.group()


def environment(manifest):
    env=dict(os.environ)
    env.update(PYTHONPATH=str(HERE/'code_snapshot/src'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
               MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',LC_ALL='C')
    return env


def verify_snapshot(manifest):
    for relative,expected in manifest['snapshot_sha256'].items():
        if sha(HERE/relative)!=expected:raise ValueError(f'Code snapshot changed: {relative}')
    if sha(manifest['executable'])!=manifest['executable_sha256']:
        raise ValueError('Ok-k-mer executable entry point changed since planning')


def plan(args):
    from ete3 import Tree
    if (HERE/'experiment.json').exists():raise ValueError('Already planned; use existing experiment.json')
    repo=args.repo.resolve()
    executable=repo/'.venv/bin/okkmer'
    if not executable.is_file():raise ValueError(f'Missing installed CLI: {executable}')
    configs=read_json(HERE.parent/'configs/datasets.json')['datasets']
    rows=table(FULL_TABLE)
    full={(row['dataset'],int(row['k'])):row for row in rows}
    if len(full)!=280 or any(row['status']!='ok' for row in full.values()):
        raise ValueError('Full-set compilation is incomplete or contains failed tasks')
    sketch_table=SKETCH/'compiled_20261103T162637Z_yonifc7k/all_datasets_by_k.tsv'
    sketch_rows=table(sketch_table)
    if len(sketch_rows)!=280 or any(row['status']!='ok' for row in sketch_rows):
        raise ValueError('Sketch compilation is incomplete or contains failed tasks')
    snapshot=HERE/'code_snapshot';snapshot.mkdir()
    shutil.copytree(repo/'src/okkmer',snapshot/'src/okkmer',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(repo/'pyproject.toml',snapshot/'pyproject.toml')
    patch=subprocess.check_output(['git','diff','HEAD'],cwd=repo,text=True)
    (snapshot/'working_tree.patch').write_text(patch)
    for name in ('inputs','indices','runs','logs','preparation','submissions'):(HERE/name).mkdir(exist_ok=True)
    inputs=[];tasks=[]
    for config in configs:
        dataset=config['dataset'];folder=Path(config['tree']).parts[1]
        original_tree=DATA/folder/Path(config['tree']).name
        tree=Tree(str(original_tree),format=1)
        leaves=set(tree.get_leaf_names())
        retained=leaves-set(config['exclusions'])
        directory=HERE/'inputs'/dataset;directory.mkdir()
        tree_copy=directory/'reference.nwk';shutil.copy2(original_tree,tree_copy)
        exclusions=set(config['exclusions'])
        prepared=[]
        for kind in ('full','sketch'):
            case=directory/kind;case.mkdir();matrices=case/'matrices';matrices.mkdir()
            source_rows=[];first_labels=None;first_ids=None;mapping=None
            for k in range(6,41):
                source=(Path(full[(folder,k)]['source_run'])/f'jaccard_k{k}.tsv') if kind=='full' else SKETCH/folder/f'jaccard_k{k}.tsv'
                source=source.resolve(strict=True)
                current=labels(source)
                normalized=[config['aliases'].get(accession(v),accession(v)) for v in current]
                if len(normalized)!=len(set(normalized)) or not retained<=set(normalized):
                    raise ValueError(f'Invalid genome coverage: {dataset}/{kind}/k{k}; tree only {retained-set(normalized)}')
                if first_labels is not None and (set(current)!=set(first_labels) or set(normalized)!=first_ids):
                    raise ValueError(f'Labels change between k matrices: {dataset}/{kind}')
                if first_labels is None:
                    first_labels=current;first_ids=set(normalized)
                    mapping=dict(zip(current,normalized))
                (matrices/f'jaccard_k{k}.tsv').symlink_to(source)
                source_rows.append({'k':k,'path':str(source)})
            exclusions.update(first_ids-retained)
            mapping_path=case/'genome_map.tsv'
            with mapping_path.open('w',newline='') as f:
                writer=csv.writer(f,delimiter='\t');writer.writerow(['source_id','genome_id'])
                writer.writerows(sorted(mapping.items()))
            item={'input_id':len(inputs),'dataset':dataset,'folder':folder,'distance_type':kind,
                  'matrices':str(matrices),'genome_map':str(mapping_path),'tree':str(tree_copy),
                  'original_tree':str(original_tree),'tree_sha256':sha(tree_copy),'n_genomes':len(retained),
                  'n_matrix_genomes':len(first_ids),'index':str(HERE/'indices'/dataset/kind),'sources':source_rows}
            inputs.append(item);prepared.append(item)
        if prepared[0]['n_matrix_genomes']!=prepared[1]['n_matrix_genomes']:
            raise ValueError(f'Full/sketch genome counts differ: {dataset}')
        excluded=directory/'excluded_genomes.txt';excluded.write_text(''.join(x+'\n' for x in sorted(exclusions)))
        for item in prepared:
            item['exclude_genomes']=str(excluded)
            item['excluded_ids']=sorted(exclusions)
            for mode in ('local','global'):
                task={'task_id':len(tasks),'input_id':item['input_id'],'dataset':dataset,
                      'distance_type':item['distance_type'],'mode':mode,'delta_k':3 if mode=='local' else None,
                      'n_genomes':len(retained),'threads':8}
                task['output']=str(HERE/'runs'/f"{task['task_id']:02d}_{dataset}_{item['distance_type']}_{mode}")
                tasks.append(task)
        print(dataset,len(retained),'retained genomes; exclusions:',','.join(sorted(exclusions)) or 'none',flush=True)
    manifest={'schema_version':1,'created_utc':stamp(),'repository':str(repo),
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
              'source_status':subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True),
              'snapshot_sha256':{str(path.relative_to(HERE)):sha(path) for path in snapshot.rglob('*') if path.is_file()},
              'executable':str(executable),'executable_sha256':sha(executable),'python':sys.executable,
              'full_compilation':str(FULL_TABLE),'full_compilation_sha256':sha(FULL_TABLE),
              'sketch_experiment':read_json(SKETCH/'experiment.json'),'sketch_compilation':str(sketch_table),
              'sketch_compilation_sha256':sha(sketch_table),
              'early_stopping':args.early_stopping,'k_low':6,'k_high':40,'max_kmers':3,'w_step':.05,
              'threads':8,'repetitions':1,'inputs':inputs,'tasks':tasks}
    versions=subprocess.check_output([sys.executable,'-c',
        'import json,platform,numpy,scipy,ete3,matplotlib;print(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__,scipy=scipy.__version__,ete3=ete3.__version__,matplotlib=matplotlib.__version__)))'],text=True)
    manifest['versions']=json.loads(versions)
    write_json(HERE/'experiment.json',manifest)
    write_table(HERE/'tasks.tsv',tasks)
    write_table(HERE/'inputs.tsv',[{key:value for key,value in item.items() if key not in ('sources','excluded_ids')} for item in inputs])
    collect(None)
    print('Prepared experiment: 16 input indices, 32 searches',flush=True)


def prepare(args):
    manifest=read_json(HERE/'experiment.json');verify_snapshot(manifest)
    item=manifest['inputs'][args.task_id]
    out=Path(item['index']);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise ValueError(f'Index output exists: {out}')
    cmd=[manifest['executable'],'index','--distances',item['matrices'],'--input-kind','distance',
         '--genome-map',item['genome_map'],'--k-low','6','--k-high','40','--output',str(out)]
    record={'started_utc':stamp(),'command':cmd,'slurm_job_id':os.environ.get('SLURM_JOB_ID')}
    result=subprocess.run(cmd,env=environment(manifest))
    record.update(finished_utc=stamp(),returncode=result.returncode)
    write_json(HERE/'preparation'/f"{args.task_id:02d}.json",record)
    if result.returncode:raise RuntimeError('Index preparation failed')


def parse_time(path):
    rows=table(path)
    if len(rows)!=1:raise ValueError('Expected one GNU time measurement')
    row=rows[0]
    return {'elapsed_seconds':float(row['elapsed_seconds']),'user_seconds':float(row['user_seconds']),
            'system_seconds':float(row['system_seconds']),'peak_rss_kib':int(row['peak_rss_kib']),
            'peak_rss_gib':int(row['peak_rss_kib'])/1048576,'time_exit_status':int(row['exit_status'])}


def run(args):
    manifest=read_json(HERE/'experiment.json');verify_snapshot(manifest)
    task=manifest['tasks'][args.task_id];item=manifest['inputs'][task['input_id']]
    if sha(item['tree'])!=item['tree_sha256']:raise ValueError('Reference tree changed')
    index_manifest=Path(item['index'])/'manifest.json'
    if not index_manifest.exists():raise ValueError('Index preparation has not completed')
    out=Path(task['output']);out.mkdir(exist_ok=False)
    cmd=[manifest['executable'],'search','--tree',item['tree'],'--index',item['index'],
         '--k-low','6','--k-high','40','--max-kmers','3','--w-step','0.05','--threads','8',
         '--exclude-genomes',item['exclude_genomes'],'--output',str(out/'search')]
    cmd+=['--local','3'] if task['mode']=='local' else ['--global']
    if not manifest['early_stopping']:cmd+=['--no-early-stop']
    record={'task':task,'command':cmd,'started_utc':stamp(),'hostname':socket.gethostname(),
            'slurm_job_id':os.environ.get('SLURM_JOB_ID'),'slurm_array_job_id':os.environ.get('SLURM_ARRAY_JOB_ID'),
            'slurm_array_task_id':os.environ.get('SLURM_ARRAY_TASK_ID'),
            'allocated_cpus':os.environ.get('SLURM_CPUS_PER_TASK'),'cpu_affinity':sorted(os.sched_getaffinity(0)),
            'index_manifest_sha256':sha(index_manifest),'tree_sha256':sha(item['tree']),
            'source_snapshot':manifest['snapshot_sha256'],'versions':manifest['versions'],
            'environment':{name:environment(manifest)[name] for name in ('PYTHONPATH','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','LC_ALL')}}
    write_json(out/'invocation.json',record)
    cpuinfo=Path('/proc/cpuinfo')
    if cpuinfo.exists():(out/'cpuinfo.txt').write_text(cpuinfo.read_text())
    timed=out/'gnu_time.tsv'
    timed.write_text('elapsed_seconds\tuser_seconds\tsystem_seconds\tpeak_rss_kib\texit_status\n')
    timed_cmd=['/usr/bin/time','--quiet','--append','--output',str(timed),
               '--format','%e\t%U\t%S\t%M\t%x',*cmd]
    # Only the search subprocess is measured. No installation, index building,
    # Dashing2, wrapper provenance collection or report generation is timed.
    with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
        result=subprocess.run(timed_cmd,stdout=stdout,stderr=stderr,env=environment(manifest))
    record.update(finished_utc=stamp(),returncode=result.returncode,**parse_time(timed))
    search=out/'search/run.json'
    if result.returncode==0:
        data=read_json(search)
        if not manifest['early_stopping'] and [s['ensemble_size'] for s in data['stages']]!=[1,2,3]:
            raise ValueError('Search did not evaluate all three stages')
        if data['n_genomes']!=task['n_genomes']:raise ValueError('Unexpected retained genome count')
        record['recommendation']=data['recommendation']
        record['stages']=data['stages']
        record['stop_reason']=data['stop_reason']
    write_json(out/'measurement.json',record)
    if result.returncode:raise RuntimeError(f'Search failed ({result.returncode}); see {out}/stderr.log')
    print(f"{task['dataset']} {task['distance_type']} {task['mode']}: {record['elapsed_seconds']} seconds, {record['peak_rss_gib']:.4f} GiB",flush=True)


def collect(args):
    manifest=read_json(HERE/'experiment.json');rows=[];stage_rows=[]
    for task in manifest['tasks']:
        out=Path(task['output']);path=out/'measurement.json'
        row={key:task[key] for key in ('task_id','dataset','distance_type','mode','n_genomes','threads')}
        row.update(status='not_completed',output=str(out))
        if path.exists():
            measurement=read_json(path)
            row.update(status='complete' if measurement['returncode']==0 else 'failed',
                       **{key:measurement.get(key) for key in ('elapsed_seconds','user_seconds','system_seconds','peak_rss_kib','peak_rss_gib','returncode','hostname','slurm_job_id')})
            if 'recommendation' in measurement:
                best=measurement['recommendation']
                row.update(recommended_ks=json.dumps(best['ks']),recommended_weights=json.dumps(best['weights']),
                           rho=best['rho'],stop_reason=measurement['stop_reason'])
                row['evaluated_sizes']=','.join(str(s['ensemble_size']) for s in measurement['stages'])
                for stage in measurement['stages']:
                    stage_rows.append(dict(task_id=task['task_id'],dataset=task['dataset'],distance_type=task['distance_type'],mode=task['mode'],
                                           ensemble_size=stage['ensemble_size'],n_combinations=stage['n_combinations'],
                                           ks=json.dumps(stage['best']['ks']),weights=json.dumps(stage['best']['weights']),rho=stage['best']['rho']))
        elif (out/'invocation.json').exists():row['status']='started_or_interrupted'
        rows.append(row)
    write_table(HERE/'search_timings.tsv',rows);write_table(HERE/'stage_recommendations.tsv',stage_rows)
    complete=[row for row in rows if row['status']=='complete']
    lines=['# Ok-k-mer search timings','',f'Completed: {len(complete)}/32 searches.','',
           'GNU time elapsed seconds and maximum RSS (KiB / 1,048,576 = GiB).',
           'Only the CLI search is timed, including its input loading and result writing.',
           'Installation, index preparation, Dashing2 and scheduler queue time are excluded.','',
           '| Dataset | Mode | Distances | Elapsed seconds | Peak RSS GiB |','|---|---|---|---:|---:|']
    for row in complete:lines.append(f"| {row['dataset']} | {row['mode']} | {row['distance_type']} | {row['elapsed_seconds']:.2f} | {row['peak_rss_gib']:.4f} |")
    lines+=['','One measurement per condition; no runtime variability estimate.',
            f"Early stopping enabled: {manifest['early_stopping']}. All tasks request a maximum of three lengths."]
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(f'Collected {len(complete)}/32 successful searches')


def submit(args):
    manifest=read_json(HERE/'experiment.json');verify_snapshot(manifest)
    receipt=HERE/'submissions/jobs.json'
    if receipt.exists():raise ValueError('Submission receipt exists; inspect it before scheduling retries')
    record={'created_utc':stamp(),'jobs':{},'commands':[]}
    write_json(receipt,record)
    def sbatch(name,extra):
        cmd=['sbatch','--parsable',f'--output={HERE}/logs/{name}_%A_%a.out',f'--error={HERE}/logs/{name}_%A_%a.err',*extra,str(HERE/f'{name}.sh')]
        record['commands'].append(cmd);write_json(receipt,record)
        result=subprocess.run(cmd,capture_output=True,text=True)
        record.setdefault('responses',[]).append({'name':name,'stdout':result.stdout,'stderr':result.stderr,'returncode':result.returncode})
        write_json(receipt,record)
        if result.returncode:raise RuntimeError(result.stderr)
        match=re.fullmatch(r'(\d+)(?:;[^\s]+)?',result.stdout.strip())
        if not match:raise RuntimeError('Unrecognized scheduler response; inspect receipt before retrying')
        job=match.group(1);record['jobs'][name]=job;write_json(receipt,record);return job
    prep=sbatch('prepare',['--array=0-15%4'])
    search=sbatch('search',['--array=0-31%32',f'--dependency=afterok:{prep}'])
    summary=sbatch('collect',[f'--dependency=afterany:{search}'])
    print(json.dumps(record['jobs'],indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    item=sub.add_parser('plan');item.add_argument('--repo',type=Path,default=HERE.parent.parent/'ok_k_mer')
    item.add_argument('--early-stopping',action='store_true',help='Use the CLI default stopping rule instead of forcing all three stages')
    for name in ('prepare','run'):
        item=sub.add_parser(name);item.add_argument('--task-id',type=int,required=True)
    sub.add_parser('collect');sub.add_parser('submit')
    args=p.parse_args();globals()[args.command](args)

if __name__=='__main__':main()
