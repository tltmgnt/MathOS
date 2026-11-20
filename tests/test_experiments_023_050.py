"""Regression and scope tests for the registered MathOS EXP-023..050 program."""
import json
import tempfile
import unittest
from pathlib import Path

from experiments.internal_reasoning.experiments_023_050 import (
    DEFAULT_CASES,
    EXPERIMENTS,
    PAIRED,
    PROTOCOL,
    _make_case,
    build_cases,
    evaluate,
    extract_integer,
    main,
    run_experiments,
)


class TestFollowupExperimentRegistry(unittest.TestCase):
    def test_exactly_twenty_eight_distinct_ids_and_questions(self):
        self.assertEqual(sorted(EXPERIMENTS), list(range(23, 51)))
        self.assertEqual(len({row[0] for row in EXPERIMENTS.values()}), 28)
        self.assertTrue(all(len(row[1]) > 20 for row in EXPERIMENTS.values()))
        self.assertEqual(PAIRED, {38, 39, 40, 41, 42, 43})

    def test_deterministic_bounded_cases_all_ids(self):
        for exp_id in EXPERIMENTS:
            with self.subTest(exp_id=exp_id):
                cases = build_cases(exp_id)
                self.assertEqual(cases, build_cases(exp_id))
                self.assertEqual(len(cases), DEFAULT_CASES)
                self.assertEqual(len({tuple(c["operands"]) for c in cases}), DEFAULT_CASES)
                self.assertTrue(all(c["prompt"] for c in cases))
                self.assertTrue(all(type(c["correct_answer"]) is int for c in cases))
                self.assertEqual(
                    all(c["paired_prompt"] is not None for c in cases),
                    exp_id in PAIRED,
                )

    def test_independent_arithmetic_oracle_on_all_conditions(self):
        subtraction = {31, 32, 33, 41, 45, 48}
        multiplication = {34, 35, 36, 37, 39, 46}
        for exp_id in EXPERIMENTS:
            for case in build_cases(exp_id):
                a, b = case["operands"][:2]
                c = case["operands"][2] if len(case["operands"]) == 3 else 0
                if exp_id in (40,):
                    truth = a + b + c
                elif exp_id == 42:
                    truth = a
                elif exp_id == 43:
                    truth = a * (b + c)
                elif exp_id in subtraction:
                    truth = a - b
                elif exp_id in multiplication:
                    truth = a * b
                else:
                    truth = a + b
                self.assertEqual(case["correct_answer"], truth)
                if exp_id in PAIRED:
                    paired_truth = -truth if exp_id == 41 else truth
                    self.assertEqual(case["paired_correct_answer"], paired_truth)
                    self.assertEqual(
                        case["paired_relation"],
                        "negated" if exp_id == 41 else "same",
                    )
                else:
                    self.assertIsNone(case["paired_correct_answer"])

    def test_special_population_controls(self):
        for case in build_cases(27):
            a, b = case["operands"]
            self.assertGreaterEqual(a % 10 + b % 10, 10)
        for case in build_cases(28):
            a, b = case["operands"]
            self.assertLess(a % 10 + b % 10, 10)
        for case in build_cases(32):
            a, b = case["operands"]
            self.assertLess(a, b)
        for case in build_cases(35):
            self.assertIn(0, case["operands"])
            self.assertEqual(case["correct_answer"], 0)
        for case in build_cases(50):
            self.assertTrue(all(1000 <= x <= 9999 for x in case["operands"]))
        self.assertNotEqual(build_cases(23, seed=406), build_cases(23, seed=407))

    def test_zero_and_invalid_count_rejected(self):
        for bad in (22, 51):
            with self.assertRaises(ValueError):
                build_cases(bad)
        for bad in (0, 101):
            with self.assertRaises(ValueError):
                build_cases(23, count=bad)

    def test_strict_start_of_answer_parser(self):
        self.assertEqual(extract_integer(" -23\n"), -23)
        self.assertEqual(extract_integer("0"), 0)
        self.assertEqual(extract_integer("17!"), 17)
        for bad in ("0.0%", "0.5%", "1,234", "12.3", "Answer: 5", "", "5/2", "  8."):
            self.assertIsNone(extract_integer(bad), msg=bad)
        self.assertIsNone(extract_integer(None))

    def test_metrics_parse_and_paired_truth_are_separate(self):
        c1 = _make_case(41, 1, 7, 2, 0)
        c2 = _make_case(41, 2, 9, 1, 0)
        records = [
            {**c1, "prediction": 5, "paired_prediction": -5},
            {**c2, "prediction": 8, "paired_prediction": None},
        ]
        result = evaluate(records)
        self.assertEqual(result["primary"]["correct_count"], 2)
        self.assertEqual(result["paired"]["both_parsed_count"], 1)
        self.assertEqual(result["paired"]["consistent_count"], 1)
        self.assertEqual(result["paired"]["both_correct_count"], 1)
        self.assertEqual(result["fixed_baselines"]["constant_zero"]["correct_count"], 0)

    def test_baseline_only_is_not_reported_as_model_experiment(self):
        with tempfile.TemporaryDirectory() as directory:
            reports = run_experiments(23, 50, output_dir=Path(directory))
            self.assertEqual(len(reports), 28)
            self.assertTrue(all(r["status"] == "BASELINES_ONLY_NO_MODEL" for r in reports))
            self.assertTrue(all(r["model_revision"] is None for r in reports))
            self.assertTrue(all(rec["prediction"] is None for r in reports for rec in r["records"]))
            self.assertTrue(all(r["metrics"]["primary"] is None for r in reports))
            manifest = json.loads((Path(directory) / "batch_manifest.json").read_text())
            self.assertEqual(manifest["completed_model_evaluations"], 0)
            self.assertEqual(manifest["baseline_only_experiment_records"], 28)
            self.assertEqual(manifest["protocol"], PROTOCOL)
            self.assertEqual(len(list(Path(directory).glob("experiment_*.json"))), 28)

    def test_model_requires_sha_and_does_not_load_on_bad_input(self):
        with self.assertRaisesRegex(ValueError, "pinned"):
            run_experiments(23, 23, backend="model", model_key="distilgpt2", revision="main")
        with self.assertRaisesRegex(ValueError, "model_key"):
            run_experiments(23, 23, backend="model", model_key="none", revision="0" * 40)
        with self.assertRaisesRegex(ValueError, "baseline-only"):
            run_experiments(23, 23, model_key="distilgpt2")
        with self.assertRaises(ValueError):
            run_experiments(23, 51)

    def test_cli_writes_baseline_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["--start", "49", "--end", "50", "--output-dir", directory]), 0)
            self.assertEqual(len(list(Path(directory).glob("experiment_*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
