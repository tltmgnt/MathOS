"""Scoped regression tests for TGA performance baselines (not mathematics)."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mathos.proof_analysis.gap_analysis import analyze
from scripts.tga_gap_benchmark import benchmark, fixture


class ProofGapBenchmarkTests(unittest.TestCase):
    def test_fixture_expected_sets_independent_of_analyzer(self):
        for kind, sizes in (
            ("chain", (3, 10, 50)),
            ("shared", (3, 10, 50)),
            ("alternatives", (3, 10, 50)),
            ("binary_choices", (1, 3, 5)),
        ):
            for size in sizes:
                with self.subTest(kind=kind, size=size):
                    graph, expected = fixture(kind, size)
                    self.assertEqual(
                        analyze(graph, "target")["minimal_completion_sets"], expected
                    )
                    self.assertEqual(len(graph),
                        3 * size + 1 if kind == "binary_choices" else size)

    def test_benchmark_report_scope_and_independent_boolean_crosscheck(self):
        report = benchmark(sizes=(10,), layers=(2,), repeats=1)
        self.assertEqual(report["schema"], "mathos.tga.proof_gap_benchmark/1")
        self.assertEqual(len(report["cases"]), 4)
        self.assertFalse(report["mathematical_theorem_certified"])
        self.assertFalse(report["lean_kernel_checked"])
        for case in report["cases"]:
            self.assertTrue(case["fixture_expected_sets_match"])
            self.assertTrue(case["exhaustive_boolean_crosscheck"].startswith("pass_"))
            self.assertGreaterEqual(case["instrumented_wall_ms"]["min"], 0)
            self.assertGreater(case["tracemalloc_peak_bytes"]["max"], 0)

    def test_reject_bad_or_unbounded_parameters(self):
        with self.assertRaises(ValueError):
            fixture("alternatives", 501)
        with self.assertRaises(ValueError):
            fixture("binary_choices", 11)
        with self.assertRaises(ValueError):
            fixture("unknown", 4)
        with self.assertRaises(ValueError):
            benchmark(sizes=(10,), layers=(2,), repeats=0)

    def test_cli_creates_report_without_mutating_proof_state(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            subprocess.run([
                sys.executable, "scripts/tga_gap_benchmark.py",
                "--sizes", "5", "--layers", "2", "--repeats", "1",
                "--output", str(output),
            ], check=True, capture_output=True, text=True)
            content = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(content["mathematical_theorem_certified"])
            self.assertEqual(len(content["cases"]), 4)


if __name__ == "__main__":
    unittest.main()
