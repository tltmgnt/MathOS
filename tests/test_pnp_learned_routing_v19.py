import copy
import json
import unittest

from mathos.research.pnp_evidence_benchmark import digest
from mathos.research.pnp_unified_discovery_v18 import features
from mathos.research.pnp_learned_routing_v19 import fit, solve, verify, bucket, select, validate_gate
from mathos.research.pnp_learned_routing_frontier_v19 import summarize, ARMS

PLAN = ["min_product", 8]
LIB = [{"n":1,"axioms":[[-1],[1]],"steps":[[]],"edges":[]}]


def calibration(wins=False, losses=False):
    # Synthetic routing labels for unit testing the fit rule only;
    # real calibration requires the v18 report audit.
    rows = []
    for i in range(3):
        f = [[v] for v in range(1,21+i)] + [[-1]]
        n = 20+i
        base = "unknown" if wins and i==0 else "unsat"
        integrated = "unknown" if losses and i==1 else "unsat"
        rows.append({"case":{"n":n,"clauses":f},"features":features(n,f),
                     "reference_sat":False,
                     "arms":{"v16":{"result":{"decision":base}},
                             "v18":{"result":{"decision":integrated}}}})
    return {"schema":"mathos-pnp-v18-development/1","completion":"completed",
            "library_sha256":digest(LIB),"universal_obligation":"unresolved","rows":rows}


class TestLearnedRouting(unittest.TestCase):
    def test_tie_defaults_to_full_adaptive(self):
        g = fit(calibration(),LIB)
        f = [[i] for i in range(1,21)]
        r = solve(20,f,{},PLAN,LIB,g)
        self.assertEqual(r["route"],"adaptive")
        self.assertEqual(r["decision"],"sat")
        self.assertEqual(r["payload"]["total_steps"],r["total_steps"])
        self.assertTrue(verify(20,f,{},PLAN,LIB,g,json.loads(json.dumps(r))))

    def test_positive_calibration_activates_checked_retrieval(self):
        g = fit(calibration(wins=True),LIB)
        f = [[i] for i in range(1,21)] + [[-1]]
        r = solve(20,f,{},PLAN,LIB,g)
        self.assertEqual(r["route"],"integrated")
        self.assertEqual(r["decision"],"unsat")
        self.assertEqual(r["payload"]["attempts"][0]["route"],"library")
        self.assertTrue(verify(20,f,{},PLAN,LIB,g,r))
        bad = copy.deepcopy(r)
        bad["payload"]["attempts"][0]["payload"]["proof"] = [[1]]
        with self.assertRaises(ValueError):
            verify(20,f,{},PLAN,LIB,g,bad)

    def test_loss_and_sparse_bucket_default(self):
        g = fit(calibration(wins=True,losses=True),LIB)
        self.assertEqual(select(features(20,[[v] for v in range(1,21)]),g,LIB),"adaptive")
        c = calibration(wins=True)
        c["rows"] = c["rows"][:1]
        g = fit(c,LIB)
        self.assertEqual(select(c["rows"][0]["features"],g,LIB),"adaptive")

    def test_forged_metadata_and_calibration(self):
        g = fit(calibration(),LIB)
        f = [[1],[-1]]
        r = solve(1,f,{},PLAN,LIB,g)
        for key,value in (("decision","sat"),("route","integrated"),("gate_sha256","0"*64)):
            with self.assertRaises(ValueError):
                verify(1,f,{},PLAN,LIB,g,{**r,key:value})
        bad = copy.deepcopy(g)
        bad["buckets"]["large_simple"]["wins"] = 99
        with self.assertRaises(ValueError):
            validate_gate(bad,LIB)
        c = calibration()
        c["rows"][0]["arms"]["v18"]["result"]["decision"]="sat"
        with self.assertRaises(ValueError):
            fit(c,LIB)
        c = calibration()
        c["rows"].append(c["rows"][0])
        with self.assertRaises(ValueError):
            fit(c,LIB)

    def test_paired_accounting(self):
        rows=[]
        for a,b in (("unknown","unsat"),("sat","unknown"),("sat","sat")):
            arms={k:{"result":{"decision":a if k=="v16" else b},
                     "wall_seconds":1.0} for k in ARMS}
            arms["v19-gate"]["result"]["route"]="adaptive"
            rows.append({"case":{"family":"chain"},"arms":arms})
        s=summarize(rows)["all"]
        self.assertEqual(s["versus_v16"]["v19-gate"],{"wins":1,"losses":1})
        self.assertEqual(s["gate_routes"]["adaptive"],3)


if __name__ == "__main__":
    unittest.main()
