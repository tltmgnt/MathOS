import tempfile
import unittest
from pathlib import Path
from mathos.research import tga_proctor_dimacs_fixtures as d


class DimacsFixtureTests(unittest.TestCase):
    def test_encoding(self):
        self.assertEqual(d.encode_dimacs(2,((1,-2,1),())),
                         b"p cnf 2 2\n1 -2 1 0\n0\n")

    def test_fixture_counts(self):
        fs=d.cases()
        self.assertEqual(len(fs),73)
        self.assertEqual(sum(ref is not None for _,_,ref,_ in fs),56)
        self.assertEqual(sum(ok for _,_,_,ok in fs),22)
        self.assertEqual(fs,d.cases())

    def test_emit(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(d.emit(td),73)
            self.assertEqual(len(list(Path(td).iterdir())),365)
            self.assertEqual((Path(td)/"72.cnf").stat().st_size,1000001)


if __name__=="__main__":
    unittest.main()
