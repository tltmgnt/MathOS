import copy
import itertools
import json
import random
import unittest
from mathos.research.pnp_complexity_barriers import (transcript,verify_transcript,
    evaluate_extension,algebraic_control,verify_algebraic,essential,essential_count,
    natural_control,verify_natural,dossier,verify_dossier)
from mathos.research.pnp_barrier_frontier import run,audit


class TestComplexityBarriers(unittest.TestCase):
    def test_transcript_completions(self):
        rng=random.Random(25025)
        for n in range(1,9):
            N=1<<n
            for k in (0,1,N//2,N-1,N):
                q=rng.sample(range(N),k)
                r=transcript(n,q)
                self.assertTrue(verify_transcript(n,q,r))
                if k<N:
                    self.assertNotIn(r["unqueried"],q)
                    self.assertEqual(r["alternative_completion"]["ones"],[r["unqueried"]])
                else:
                    self.assertIsNone(r["alternative_completion"])
        with self.assertRaises(ValueError):
            transcript(3,[1,1])

    def test_extension(self):
        for n in range(1,7):
            self.assertTrue(verify_algebraic(algebraic_control(n)))
            for i in range(1<<n):
                for j in range(1<<n):
                    point=[j>>k&1 for k in range(n)]
                    self.assertEqual(evaluate_extension(n,[i],point),int(i==j))
        self.assertEqual(evaluate_extension(3,[0,1,2],[2]*3),0)

    def test_natural_property_count(self):
        for n in (1,2,3):
            count=sum(all(p is not None for p in essential(n,t))
                      for t in itertools.product((0,1),repeat=1<<n))
            self.assertEqual(count,essential_count(n))
            self.assertTrue(verify_natural(natural_control(n)))
        self.assertTrue(all(x is not None for x in essential(3,[i.bit_count()%2 for i in range(8)])))

    def test_tampering(self):
        r=transcript(2,[0,1,2])
        with self.assertRaises(ValueError):
            verify_transcript(2,[0,1,2],{**r,"unqueried":1})
        r=algebraic_control(3)
        r["singleton_values"][0]=0
        with self.assertRaises(ValueError):
            verify_algebraic(r)
        r=natural_control(3)
        r["accepted_tables"]+=1
        with self.assertRaises(ValueError):
            verify_natural(r)
        r=dossier()
        r["barriers"]["relativization"]["status"]="overcome"
        with self.assertRaises(ValueError):
            verify_dossier(r)

    def test_pipeline(self):
        r=run()
        self.assertTrue(audit(json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["sizes"],8)
        self.assertEqual(r["summary"]["largest_query_bound"],4096)
        self.assertEqual(r["summary"]["barriers_overcome"],0)
        x=copy.deepcopy(r)
        x["p_not_equals_np_established"]=True
        with self.assertRaises(ValueError):
            audit(x)
        with self.assertRaises(ValueError):
            audit({**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
