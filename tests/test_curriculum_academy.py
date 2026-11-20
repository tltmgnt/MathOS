"""Adversarial checks for the academy's structure-only validator."""
import copy
import json
from pathlib import Path
import unittest

from curriculum.academy.validate import CATALOG, ROOT, validate


class AcademyCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_real_catalog_passes_structure(self):
        self.assertEqual(validate(self.catalog, ROOT), [])

    def test_cannot_claim_certification(self):
        data = copy.deepcopy(self.catalog)
        data["automatic_certification"] = True
        self.assertTrue(any("automatic_certification" in x for x in validate(data)))

    def test_cannot_claim_external_validation(self):
        data = copy.deepcopy(self.catalog)
        data["external_validation_established"] = True
        self.assertTrue(any("external validation" in x for x in validate(data)))

    def test_cycle_rejected(self):
        data = copy.deepcopy(self.catalog)
        next(c for c in data["courses"] if c["id"] == "bridge")["prerequisites"] = ["agentic-clay"]
        self.assertTrue(any("cycle" in x for x in validate(data)))

    def test_unknown_prerequisite_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["courses"][0]["prerequisites"] = ["nonexistent"]
        self.assertTrue(any("prerequisite" in x for x in validate(data)))

    def test_missing_syllabus_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["courses"][0]["syllabus"] = "curriculum/not-a-syllabus.md"
        self.assertTrue(any("syllabus" in x for x in validate(data)))

    def test_parent_path_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["courses"][0]["syllabus"] = "../README.md"
        self.assertTrue(any("unsafe" in x for x in validate(data)))

    def test_missing_dimension_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["quality_dimensions"].pop()
        self.assertTrue(any("dimension" in x for x in validate(data)))

    def test_duplicate_course_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["courses"].append(copy.deepcopy(data["courses"][0]))
        self.assertTrue(any("course IDs" in x for x in validate(data)))

    def test_wrong_evidence_type_rejected(self):
        data = copy.deepcopy(self.catalog)
        data["courses"][0]["evidence_type"] = "self_certified"
        self.assertTrue(any("evidence_type" in x for x in validate(data)))


if __name__ == "__main__":
    unittest.main()
