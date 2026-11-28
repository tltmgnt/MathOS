import copy
import json
import unittest
from mathos.research.pnp_expander_size import family,edges,certify,verify,spectral_pivots
from mathos.research.pnp_expander_frontier import run,audit,budget
from mathos.research.pnp_structural_kernel import brute


class TestExpanderSize(unittest.TestCase):
    def test_small_reference(self):
        for odd in (True,False):
            n,f,_=family(2,odd=odd)
            self.assertEqual(brute(n,f,budget()),not odd)
            p=certify(2,odd=odd,b=budget())
            self.assertTrue(verify(2,n,f,json.loads(json.dumps(p)),budget()))

    def test_exact_cut_check(self):
        s=3
        e=edges(s)
        V=s*s
        for mask in range(1,1<<V):
            k=mask.bit_count()
            cut=sum(bool(mask>>u&1)!=bool(mask>>v&1) for u,v in e)
            self.assertGreaterEqual(10*V*cut,9*k*(V-k))
        with self.assertRaises(ValueError):
            spectral_pivots(2,(),budget())

    def test_tampering(self):
        n,f,_=family(3)
        p=certify(3,odd=True,b=budget())
        for key in ("spectral_pivots","edges","rows"):
            q=copy.deepcopy(p)
            q[key]=q[key][:-1]
            with self.assertRaises(ValueError):
                verify(3,n,f,q,budget())
        q=copy.deepcopy(p)
        q["parameters"]["width_lower"]+=1
        with self.assertRaises(ValueError):
            verify(3,n,f,q,budget())
        with self.assertRaises(ValueError):
            verify(3,n,f[:-1],p,budget())
        n,f,_=family(3,odd=False)
        p=certify(3,odd=False,b=budget())
        p["decision_proof"]["assignment"]=[False]*n
        with self.assertRaises(ValueError):
            verify(3,n,f,p,budget())

    def test_report(self):
        r=run()
        self.assertEqual(r["completion"],"completed",r.get("reason"))
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["parity_decisions"],12)
        self.assertEqual(r["summary"]["exact_spectral_checks"],12)
        self.assertGreater(r["summary"]["positive_exponent_ratios"],0)
        with self.assertRaises(ValueError):
            audit({**r,"p_not_equals_np_established":True})
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
