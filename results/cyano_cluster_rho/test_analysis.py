import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import analyze

class CountTest(unittest.TestCase):
    def test_deduplicates_and_excludes_zero_weights_and_repeated_lengths(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out/'three.json').write_text(json.dumps(dict(k_low=6,k_high=8,k_main=7,s=1,w_step=.25,correlation=-.91)))
            (out/'two.json').write_text(json.dumps(dict(correlation=-.905)))
            tensor = np.full((3,3,3,5,5),np.inf)
            tensor[0,1,2,1,1] = -.9
            tensor[2,0,1,1,2] = -.91
            tensor[0,1,2,0,1] = -.99  # zero-weight term is not a triple
            tensor[0,0,1,1,1] = -.99  # repeated lengths are not a triple
            np.save(out/'three.npy',tensor)
            with patch.object(analyze,'HERE',out), patch('sys.argv',['analyze.py']):
                analyze.main()
            result = json.loads((out/'summary.json').read_text())
            self.assertEqual(result['unique_three_length_combinations'],1)
            self.assertEqual(result['better_than_best_two'],1)
            self.assertEqual(result['within_delta_of_best_three'],1)

if __name__ == '__main__':
    unittest.main()
