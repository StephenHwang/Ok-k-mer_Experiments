import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import benchmark

class TimingTests(unittest.TestCase):
    def test_gnu_time_and_gib_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'time.tsv'
            path.write_text('elapsed_seconds\tuser_seconds\tsystem_seconds\tpeak_rss_kib\texit_status\n')
            result=subprocess.run(['/usr/bin/time','--quiet','--append','--output',str(path),
                '--format','%e\t%U\t%S\t%M\t%x',sys.executable,'-c','x=bytearray(20*1024*1024)'])
            self.assertEqual(result.returncode,0)
            values=benchmark.parse_time(path)
            self.assertGreater(values['peak_rss_kib'],20*1024)
            self.assertEqual(values['peak_rss_gib'],values['peak_rss_kib']/1048576)
            self.assertEqual(values['time_exit_status'],0)

    def test_partial_collection_does_not_claim_unfinished_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            tasks=[]
            for i in range(2):
                tasks.append(dict(task_id=i,dataset='Toy',distance_type='full',mode=['local','global'][i],n_genomes=3,threads=8,output=str(root/f'run{i}')))
            (root/'experiment.json').write_text(json.dumps(dict(tasks=tasks,early_stopping=False)))
            out=root/'run0';out.mkdir()
            (out/'measurement.json').write_text(json.dumps(dict(returncode=0,elapsed_seconds=2,peak_rss_gib=.25,
                recommendation=dict(ks=[6],weights=[1],rho=.7),stop_reason='max_kmers_reached',
                stages=[dict(ensemble_size=1,n_combinations=1,best=dict(ks=[6],weights=[1],rho=.7))])))
            with patch.object(benchmark,'HERE',root),contextlib.redirect_stdout(io.StringIO()):
                benchmark.collect(None)
            rows=benchmark.table(root/'search_timings.tsv')
            self.assertEqual(rows[0]['status'],'complete')
            self.assertEqual(rows[1]['status'],'not_completed')
            self.assertEqual(rows[1]['elapsed_seconds'],'')

if __name__=='__main__':unittest.main()
