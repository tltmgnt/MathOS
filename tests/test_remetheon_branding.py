"""REMETHEON brand consistency checks (identity and scope, not trademark clearance).

The public brand must not silently promote planned memory/AI experiences
to delivered features or undermine the existing TECT-X proof status.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/brand/remetheon.brand.json"
GUIDE = ROOT / "docs/brand/REMETHEON.md"
README = ROOT / "README.md"


class RemetheonBrandConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.guide = GUIDE.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_public_name_descriptor_and_tagline(self):
        self.assertEqual(self.manifest["schema_version"], "1.0")
        self.assertEqual(self.manifest["brand_id"], "remetheon")
        self.assertEqual(self.manifest["display_name"], "REMETHEON")
        self.assertEqual(self.manifest["descriptor"], "Mathematical Memory Intelligence")
        self.assertEqual(self.manifest["tagline"],
                         "Every insight remembered. Every proof advanced.")

    def test_readme_adopts_brand_without_breaking_legacy_identity(self):
        self.assertTrue(self.readme.startswith("# REMETHEON\n"))
        for name in ("MathOS", "TECT-X", "docs/brand/REMETHEON.md",
                     "docs/brand/remetheon.brand.json"):
            with self.subTest(name=name):
                self.assertIn(name, self.readme)
        self.assertIn("## Millennium Ω research assurance", self.readme)
        self.assertIn("## TECT-X: source-scoped thematic research assurance", self.readme)

    def test_five_unique_public_product_families(self):
        families = self.manifest["product_family"]
        names = [entry["name"] for entry in families]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {
            "Remetheon TGA", "Remetheon Kernel", "Remetheon Chronicle",
            "Remetheon Research", "Remetheon Scholar",
        })

    def test_planned_memory_and_learning_are_not_claimed_as_implemented(self):
        families = {entry["name"]: entry for entry in self.manifest["product_family"]}
        self.assertEqual(families["Remetheon Chronicle"]["status"], "planned")
        self.assertEqual(families["Remetheon Scholar"]["status"], "planned")
        self.assertEqual(families["Remetheon Research"]["status"], "planned_product_experience")
        for product in ("Remetheon Chronicle", "Remetheon Research", "Remetheon Scholar"):
            self.assertIsNone(families[product]["source"])
        self.assertIn("not shipped", self.readme)
        self.assertIn("roadmap", self.guide.lower())

    def test_existing_scoped_research_tools_keep_scope_labels_and_sources(self):
        families = {entry["name"]: entry for entry in self.manifest["product_family"]}
        self.assertEqual(families["Remetheon TGA"]["status"], "implemented_research_prototype")
        self.assertEqual(families["Remetheon Kernel"]["status"],
                         "implemented_scoped_research_prototype")
        for name in ("Remetheon TGA", "Remetheon Kernel"):
            path = families[name]["source"]
            self.assertIsInstance(path, str)
            self.assertTrue((ROOT / path).is_file(), name)
            self.assertIn("research", path)

    def test_legacy_code_and_public_links_are_stable(self):
        m = self.manifest["migration_policy"]
        self.assertFalse(m["github_repo_rename"])
        self.assertFalse(m["rename_imports_or_files"])
        self.assertTrue(m["preserve_legacy_identifiers"])
        self.assertEqual(self.manifest["repository"], "tltmgnt/MathOS")
        self.assertEqual(self.manifest["former_project_name"], "MathOS")
        self.assertEqual(self.manifest["research_technology"], "TECT-X")
        self.assertTrue((ROOT / "mathos").is_dir())
        self.assertTrue((ROOT / "docs/research/TECT_X_THEMATIC_REGISTER.v1.json").is_file())

    def test_proof_scope_and_brand_legal_claims_remain_unverified(self):
        caveats = self.manifest["scope_notes"]
        self.assertIn("not introduce persistent memory", caveats["current"])
        self.assertIn("not", caveats["temporal_memory"])
        self.assertIn("not", caveats["certification"])
        self.assertIn("No trademark registration", caveats["trademark"])
        self.assertIn("no", self.guide.lower())
        self.assertIn("not a claim", self.guide.lower())

    def test_docs_reference_brand_without_rewriting_theorem_scope(self):
        docs = {
            "docs/research/TECT_X_INTELLIGENT_PROOF_VERIFIER.md": "Remetheon TGA",
            "docs/research/TECT_X_FORMAL_VERIFICATION.md": "Remetheon Kernel",
            "docs/research/TECT_X_TYPED_ARGUMENT_VERIFICATION.md": "Remetheon Kernel",
        }
        for path, new_name in docs.items():
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn(new_name, text)
                self.assertIn("../brand/REMETHEON.md", text)
                self.assertIn("TECT-X", text)

    def test_brand_guide_contains_math_memory_provenance_proposal(self):
        for field in ("record_id", "created_at", "revision_of", "claim_status",
                      "verification_artifacts", "privacy_scope"):
            with self.subTest(field=field):
                self.assertIn(field, self.guide)
        self.assertIn("future product requirement", self.guide)

    def test_no_automated_legal_clearance_claimed(self):
        self.assertIn("trademark", self.guide.lower())
        self.assertIn("have **not** been performed", self.guide)
        self.assertNotIn("registered trademark", self.manifest["purpose"].lower())


if __name__ == "__main__":
    unittest.main()
