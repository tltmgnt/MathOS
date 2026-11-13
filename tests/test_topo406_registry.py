"""MathOS TOPO-406 verification registry tests."""

import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "verification" / "registry.json"


class TestTOPO406Registry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with REGISTRY.open(encoding="utf-8") as file:
            cls.registry = json.load(file)

        cls.claims = cls.registry["claims"]

    def test_registry_standard(self):
        self.assertEqual(
            self.registry["standard"],
            "TOPO-406"
        )

    def test_registry_not_empty(self):
        self.assertGreater(len(self.claims), 0)

    def test_unique_claim_ids(self):
        ids = [claim["claim_id"] for claim in self.claims]

        self.assertEqual(
            len(ids),
            len(set(ids)),
            "Duplicate claim IDs found."
        )

    def test_evidence_records_exist(self):
        for claim in self.claims:
            with self.subTest(claim=claim["claim_id"]):
                path = ROOT / claim["evidence_record"]

                self.assertTrue(
                    path.is_file(),
                    f"Missing evidence record: {path}"
                )

    def test_claim_identifiers_match(self):
        for claim in self.claims:
            with self.subTest(claim=claim["claim_id"]):
                path = ROOT / claim["evidence_record"]

                with path.open(encoding="utf-8") as file:
                    record = json.load(file)

                self.assertEqual(
                    claim["claim_id"],
                    record["claim_id"]
                )

    def test_verification_files_exist(self):
        for claim in self.claims:
            with self.subTest(claim=claim["claim_id"]):
                path = ROOT / claim["verification"]["test_file"]

                self.assertTrue(
                    path.is_file(),
                    f"Missing verification test: {path}"
                )

    def test_test_classes_and_methods_exist(self):
        for claim in self.claims:
            with self.subTest(claim=claim["claim_id"]):
                verification = claim["verification"]

                path = ROOT / verification["test_file"]

                tree = ast.parse(
                    path.read_text(encoding="utf-8")
                )

                classes = {
                    node.name: node
                    for node in tree.body
                    if isinstance(node, ast.ClassDef)
                }

                class_name = verification["test_class"]
                method_name = verification["test_method"]

                self.assertIn(class_name, classes)

                methods = {
                    node.name
                    for node in classes[class_name].body
                    if isinstance(
                        node,
                        (ast.FunctionDef, ast.AsyncFunctionDef)
                    )
                }

                self.assertIn(method_name, methods)

                if "boundary_test" in verification:
                    self.assertIn(
                        verification["boundary_test"],
                        methods
                    )

    def test_registry_status_matches_evidence(self):
        for claim in self.claims:
            with self.subTest(claim=claim["claim_id"]):
                path = ROOT / claim["evidence_record"]

                with path.open(encoding="utf-8") as file:
                    record = json.load(file)

                self.assertEqual(
                    claim["status"],
                    record["status"]
                )


if __name__ == "__main__":
    unittest.main()
