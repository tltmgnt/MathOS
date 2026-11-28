import copy
import json
import unittest

from mathos.research.pnp_knowledge_library import build,verify_library,query,verify_query,strengthen,verify_strengthening,budget
from mathos.research.pnp_resolution_refutation import propose
from mathos.research.pnp_proof_abstraction import compress
from mathos.research.pnp_knowledge_frontier import templates,strengthening_control,run,audit
from mathos.research.pnp_evidence_benchmark import benchmark
from mathos.research.pnp_evidence_scheduler import evaluate
from mathos.research.pnp_failure_synthesis import run as failures
from mathos.research.pnp_abstraction_frontier import run as abstraction


class TestLibrary(unittest.TestCase):
    def test_dedup_and_index(self):
        ts=templates({"records":[]})
        lib=build(ts)
        self.assertTrue(verify_library(ts,json.loads(json.dumps(lib))))
        self.assertLess(len(lib["entries"]),len(ts))
        self.assertTrue(any(x["status"]=="covered" for x in lib["dispositions"]))
        n,f=2,[(1,),(-1,2),(-2,)]
        for index in (False,True):
            r=query(n,f,lib,indexed=index)
            self.assertEqual(r["decision"],"unsat")
            self.assertTrue(verify_query(n,f,lib,json.loads(json.dumps(r))))
        a=query(3,[(1,2,3)],lib)
        self.assertEqual(a["decision"],"unknown")
        self.assertEqual(len(a["attempts"]),0)
        self.assertTrue(verify_query(3,[(1,2,3)],lib,a))

    def test_strengthened_premises(self):
        c=strengthening_control()
        self.assertTrue(verify_strengthening(c["n"],c["clauses"],c["template"],c["embedding"],c["witnesses"],budget()))
        self.assertIsNone(strengthen(2,[(1,)],c["template"],(1,2),budget()))
        bad=list(c["witnesses"])
        bad[0]=(999,)
        with self.assertRaises(ValueError):
            verify_strengthening(c["n"],c["clauses"],c["template"],c["embedding"],bad,budget())

    def test_tampering(self):
        ts=templates({"records":[]})
        lib=build(ts)
        forged=copy.deepcopy(lib)
        d=next(x for x in forged["dispositions"] if x["status"]=="covered")
        d["embedding"]=[999]*len(d["embedding"])
        with self.assertRaises(ValueError):
            verify_library(ts,forged)
        f=[(1,),(-1,2),(-2,)]
        r=query(2,f,lib)
        with self.assertRaises(ValueError):
            verify_query(2,f,lib,{**r,"decision":"unknown"})
        with self.assertRaises(ValueError):
            verify_query(2,f,lib,{**r,"skipped":["invented"]})
        forged=copy.deepcopy(lib)
        forged["entries"][0]["signature"]["variables"]=999
        with self.assertRaises(ValueError):
            query(2,f,forged)

    def test_pipeline(self):
        s=benchmark(random_count=4)
        a=evaluate(s)
        f=failures(s,a,count=4)
        t=abstraction(s,a,f,count=4)
        r=run(s,a,f,t,count=4)
        self.assertEqual(r["completion"],"completed")
        self.assertTrue(audit(s,a,f,t,json.loads(json.dumps(r))))
        self.assertEqual(r["summary"]["fresh_cases"],4)
        self.assertFalse(r["p_equals_np_established"])
        with self.assertRaises(ValueError):
            audit(s,a,f,t,{**r,"rows":r["rows"][:-1]})


if __name__=="__main__":
    unittest.main()
