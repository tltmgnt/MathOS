import tempfile
import unittest
from pathlib import Path

from mathos.research import tga_proctor_data_fixtures as d


class DataFixtureTests(unittest.TestCase):
    def test_wire_format(self):
        self.assertEqual(d.encode_expected(0,((),)),b"3401\n0\n1\n0\n")
        self.assertEqual(d.encode_envelope((0,((),),((),False,"EMPTY",None))),
                         b"3402\n0\n1\n0\n0\n0\n0\n")
        self.assertEqual(d.encode_expected(2,((1,-2),)),b"3401\n2\n1\n2\n1\n1\n2\n0\n")

    def test_fixture_counts(self):
        fs=d.cases()
        self.assertEqual(len(fs),67)
        self.assertEqual(sum(ok for _,_,ok in fs),19)
        self.assertEqual(fs,d.cases())
        self.assertEqual(len(fs[-1][0]),1000001)

    def test_export(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(d.emit(td),67)
            self.assertEqual(len(list(Path(td).iterdir())),201)
            for i,(a,b,ok) in enumerate(d.cases()):
                self.assertEqual((Path(td)/f"{i}.cnfdata").read_bytes(),a)
                self.assertEqual((Path(td)/f"{i}.proofdata").read_bytes(),b)
                self.assertEqual((Path(td)/f"{i}.verdict").read_bytes(),b"1\n" if ok else b"0\n")


if __name__=="__main__":
    unittest.main()
