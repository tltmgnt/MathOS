import json
import random
import unittest
from mathos.research.pnp_growing_width import family,certificate,verify,balanced_cut,torus
from mathos.research.pnp_growing_width_frontier import run,audit,budget,balanced_strip


class TestGrowingWidth(unittest.TestCase):
    def test_exhaustive_small_cuts(self):
        s=3
        seen=0
        for mask in range(1<<(s*s)):
            vertices=[i for i in range(s*s) if mask>>i&1]
            if s*s<3*len(vertices)<=2*s*s:
                a=balanced_cut(s,vertices,budget())
                self.assertGreaterEqual(a["size"],2*s)
                seen+=1
        self.assertGreater(seen,0)

    def test_balanced_strip_boundary(self):
        # floor(3/2) rows have size V/3, excluded by the support interval.
        with self.assertRaisesRegex(ValueError, "cut not in support interval"):
            balanced_cut(3,range(3),budget())
        for s in range(3,17):
            with self.subTest(side=s):
                strip=balanced_strip(s)
                self.assertLess(s*s,3*len(strip))
                self.assertLessEqual(3*len(strip),2*s*s)
                self.assertEqual(balanced_cut(s,strip,budget())["size"],2*s)

    def test_random_cuts(self):
        rng=random.Random(22022)
        for s in (4,6,8,12,16):
            for _ in range(40):
                v=s*s
                subset=rng.sample(range(v),rng.randint(v//3+1,2*v//3))
                self.assertGreaterEqual(balanced_cut(s,subset,budget())["size"],2*s)
            self.assertEqual(balanced_cut(s,balanced_strip(s),budget())["size"],2*s)

    def test_certificate_and_tampering(self):
        n,f,rows=family(3)
        a=certificate(3,n,f,budget())
        self.assertTrue(verify(3,n,f,json.loads(json.dumps(a)),budget()))
        self.assertEqual(a["resolution_width_lower"],6)
        for key,value in (("resolution_width_lower",7),("balanced_cut_lower",7),("total_rhs",0),("rows",rows[:-1])):
            with self.assertRaises(ValueError):
                verify(3,n,f,{**a,key:value},budget())
        with self.assertRaises(ValueError):
            verify(3,n,f[:-1],a,budget())
        n,f,_=family(3,odd=False)
        a=certificate(3,n,f,budget(),odd=False)
        self.assertIsNone(a["resolution_width_lower"])

    def test_pipeline(self):
        r=run()
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["affine_decisions"],12)
        self.assertEqual(r["summary"]["odd_width_bounds"][-1]["lower_bound"],32)
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})
        with self.assertRaises(ValueError):
            audit({**r,"p_not_equals_np_established":True})


if __name__=="__main__":
    unittest.main()
