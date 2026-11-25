import unittest
from itertools import product
import random

from mathos.research import millennium_followup_round4 as r


class RoundFourTests(unittest.TestCase):
    def test_all_scoped_derivations(self):
        p=r.run()
        self.assertEqual(p["globally_proved"],0)
        self.assertEqual(len(p["rh"]["cases"]),8)
        self.assertEqual(len(p["yang_mills"]["cases"]),11)
        self.assertEqual(p["hodge"]["cases"][-1]["primitive_rank"],14)
        self.assertEqual(p["poincare"]["linear_product"],"divergent")

    def test_separator_random_against_brute(self):
        rng=random.Random(406)
        for _ in range(120):
            n=rng.randint(1,7)
            clauses=[tuple(rng.choice((-1,1))*rng.randint(1,n) for _ in range(rng.randint(1,4)))
                     for _ in range(rng.randint(0,12))]
            expected=sum(all(any(bits[abs(l)-1]==int(l>0) for l in c) for c in clauses)
                         for bits in product((0,1),repeat=n))
            self.assertEqual(r.separator_count(n,clauses)["count"],expected)

    def test_width_cap(self):
        with self.assertRaisesRegex(ValueError,"width cap"):
            r.separator_count(14,[tuple(range(1,15))])


if __name__=="__main__":
    unittest.main()
