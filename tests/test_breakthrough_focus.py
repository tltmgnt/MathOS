import copy
import unittest
from mathos.research import breakthrough_focus as m


class BreakthroughFocusTests(unittest.TestCase):
    def setUp(self):
        self.plan=m.load("docs/research/BREAKTHROUGH_FOCUS.v1.json")
        self.reg=m.load("docs/proof-analysis/OBLIGATIONS.v1.json")
        self.routes=m.load("docs/research/CLAY_PROOF_ROUTES.v1.json")

    def queue(self):
        return m.build_queue(self.plan,self.reg,self.routes)

    def packet(self):
        p={k:"Explicit candidate material; test fixture only" for k in m.REQUIRED}
        p.update(claim_id="NS.critical_bound",outcome="PROOF_CANDIDATE",promotion="NONE",
                 evidence_kind="MATHEMATICAL_ARGUMENT",formal_status="NOT_CHECKED",
                 novelty_status="NOT_CHECKED",review_status="NOT_REVIEWED")
        return p

    def test_queue(self):
        q=self.queue()
        self.assertEqual(q["open_obligations"],14)
        self.assertEqual(len(q["queued_claims"]),12)
        self.assertFalse(q["mathematical_proof_established"])

    def test_coverage(self):
        self.plan["tracks"].pop()
        with self.assertRaises(ValueError): self.queue()

    def test_wrong_route(self):
        self.plan["tracks"][0]["route"]="PNP.equality"
        with self.assertRaises(ValueError): self.queue()

    def test_canonical_drift(self):
        self.reg["tracks"][0]["work_packages"][0]["graph_state"]="closed"
        with self.assertRaises(ValueError): self.queue()

    def test_valid_packet_is_only_metadata(self):
        r=m.intake(self.packet(),self.queue())
        self.assertFalse(r["mathematical_proof_established"])
        self.assertEqual(r["promotion"],"NONE")

    def test_bounded_test_cannot_be_proof(self):
        p=self.packet();p["evidence_kind"]="BOUNDED_TEST"
        with self.assertRaises(ValueError): m.intake(p,self.queue())

    def test_unrelated_claim(self):
        p=self.packet();p["claim_id"]="BSD.leading_term"
        with self.assertRaises(ValueError): m.intake(p,self.queue())

    def test_missing_implication(self):
        p=self.packet();del p["implication_to_claim"]
        with self.assertRaises(ValueError): m.intake(p,self.queue())

    def test_forged_promotion(self):
        p=self.packet();p["promotion"]="SOLVED"
        with self.assertRaises(ValueError): m.intake(p,self.queue())

    def test_forged_review(self):
        p=self.packet();p["review_status"]="ACCEPTED"
        with self.assertRaises(ValueError): m.intake(p,self.queue())
