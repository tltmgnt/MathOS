import unittest
from mathos.research.tga_proctor_pnp_tape_integration import fixtures,solve,verify_wire


class TapeIntegrationTests(unittest.TestCase):
    def test_exhaustive_controls(self):
        _, counts = fixtures()
        self.assertEqual(counts["systems"],4181)
        self.assertEqual(counts["sat"]+counts["unsat"],4181)

    def test_empty_and_contradictory(self):
        self.assertEqual(solve([],[])["wire"],[True])
        self.assertEqual(solve([[]],[])["wire"],[False,True])
        self.assertFalse(verify_wire([[]],[],[False,False]))
        self.assertFalse(verify_wire([],[],[False]))

    def test_reject_ragged(self):
        with self.assertRaises(ValueError):
            solve([[(0,0)]],[([],False)])
        with self.assertRaises(ValueError):
            solve([[(0,2)]],[])
