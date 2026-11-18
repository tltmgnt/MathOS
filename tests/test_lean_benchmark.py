import json
from pathlib import Path
import unittest
from unittest.mock import patch

from mathos.research import lean_benchmark


class LeanBenchmarkTests(unittest.TestCase):
    def test_parses_lean_axiom_reports(self):
        audit = lean_benchmark.audit
        self.assertEqual(audit("Candidate.lean:5:0: info: "
                               "'MathOSBenchmarkCandidate' does not depend on any axioms"), [])
        self.assertEqual(audit("'MathOSBenchmarkCandidate' depends on axioms: [sorryAx]"), ["sorryAx"])
        self.assertIsNone(audit("No audit was printed"))

    def test_replay_checks_integrity_and_proof_decisions(self):
        spec = json.loads(Path("benchmarks/lean/smoke.json").read_text(encoding="utf-8"))
        payload = {"schema": 1, "benchmark": spec, "toolchain": "Lean 4.14.0", "results": {}}
        bundle = dict(payload, sha256=lean_benchmark.digest(payload))
        with patch.object(lean_benchmark, "run", return_value=bundle):
            self.assertTrue(lean_benchmark.replay(bundle)["reproduced"])
        with patch.object(lean_benchmark, "run", return_value=dict(bundle, toolchain="other")):
            self.assertFalse(lean_benchmark.replay(bundle)["reproduced"])
        with self.assertRaisesRegex(ValueError, "checksum"):
            lean_benchmark.replay(dict(bundle, toolchain="edited"))
