"""Migration checks independent of production data and scheduler access."""
import json
from pathlib import Path
import tempfile
import unittest

from experiment_paths import ORIGINAL_ROOT, ROOT, relocate
import stability


class RelocationTests(unittest.TestCase):
    def test_nested_paths_and_component_boundary(self):
        data = {'tasks': [{'merged_csv': ORIGINAL_ROOT + '/results/pairs.csv',
                           'tree_path': '/vast/external/tree.nwk'}],
                'source_sha256': {ORIGINAL_ROOT + '/bin/script.py': 'original-hash'}}
        converted = relocate(data)
        self.assertEqual(converted['tasks'][0]['merged_csv'], str(ROOT / 'results/pairs.csv'))
        self.assertEqual(converted['tasks'][0]['tree_path'], '/vast/external/tree.nwk')
        self.assertEqual(converted['source_sha256'], data['source_sha256'])
        self.assertEqual(data['tasks'][0]['merged_csv'], ORIGINAL_ROOT + '/results/pairs.csv')
        self.assertEqual(relocate(ORIGINAL_ROOT + '_experiments/bin'), ORIGINAL_ROOT + '_experiments/bin')

    def test_manifest_reader_leaves_original_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.json'
            path.write_text(json.dumps({'tasks': [{'json_out': ORIGINAL_ROOT + '/results/task.json'}]}))
            original = path.read_bytes()
            manifest = stability.read_manifest(path)
            self.assertEqual(manifest['tasks'][0]['json_out'], str(ROOT / 'results/task.json'))
            self.assertEqual(path.read_bytes(), original)
