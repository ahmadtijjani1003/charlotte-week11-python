
import unittest
from pathlib import Path

class ProjectFilesTest(unittest.TestCase):
    def test_inputs_exist(self):
        data = Path(__file__).parent / 'data'
        self.assertTrue((data / 'scada_synthetic.csv').exists())
        self.assertTrue((data / 'well_b_synthetic.las').exists())

if __name__ == '__main__': unittest.main()
