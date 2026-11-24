import unittest
from mathos.research import tga_proctor_checker_cost as c


class CheckerCostTests(unittest.TestCase):
    def test_parent_counts(self):
        f=((1,2),(-1,2))
        env=(2,f,((((0,1,1,(2,)),),),False,"EMPTY",None))
        r=c.ledger(2,f,env)["counts"]
        self.assertEqual(r["parent_lookup_cells"],3)
        self.assertEqual(r["parent_shape_comparisons"],8)
        self.assertEqual(r["empty_scan_cells"],1)

    def test_capacity_counts(self):
        f=((1,),(2,),(-1,-2))
        p=(((0,f[0]),(1,f[1])),(((1,2),1),),((2,f[2]),))
        r=c.ledger(2,f,(2,f,((),False,"CAPACITY",p)))["counts"]
        self.assertEqual(r["reference_lookup_cells"],6)
        self.assertEqual(r["capacity_tuple_leaves"],4)
        self.assertEqual(r["capacity_word_nodes"],7)
        self.assertEqual(r["conflict_literal_comparisons"],16)

    def test_xor_counts(self):
        f=((1,),(-1,))
        p=(((1,),0,((1,f[1]),)),((1,),1,((0,f[0]),)))
        r=c.ledger(1,f,(1,f,((),False,"XOR",p)))["counts"]
        self.assertEqual(r["xor_pattern_leaves"],4)
        self.assertEqual(r["xor_pattern_literal_comparisons"],4)
        self.assertEqual(r["sparse_toggle_comparisons"],4)

    def test_families_and_fixture_envelope(self):
        r=c.controls()
        self.assertEqual(r["fixture_count"],53)
        self.assertEqual(r["accepted_expectation"],19)
        self.assertEqual(len(r["families"]),9)
        for row in r["fixtures"]+r["families"]:
            self.assertLessEqual(row["abstract_sum"],256*(row["natural_tokens"]+1)**4)
        self.assertFalse(r["total_machine_refinement"])


if __name__=="__main__":
    unittest.main()
