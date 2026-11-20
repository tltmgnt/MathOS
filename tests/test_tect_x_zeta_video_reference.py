"""Validate external-media provenance and enforce no-proof promotion for zeta TDA."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/research/TECT_X_ZETA_TDA_AUDIT.v1.json"
VIDEO_NOTE = ROOT / "docs/research/TECT_X_VIDEO_REFERENCE_AI_RH_BRUTE_FORCE.md"
GAP_NOTE = ROOT / "docs/research/TECT_X_ONE_MILLION_ZETA_TDA_GAP_ANALYSIS.md"
VIDEO_URL = "https://www.youtube.com/watch?v=M7eQUHH-oWI"


class TestExternalVideoReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.video_note = VIDEO_NOTE.read_text(encoding="utf-8")
        cls.gap_note = GAP_NOTE.read_text(encoding="utf-8")

    def test_video_citation_is_explicit_not_guessed_from_counts(self):
        source = self.audit["media_reference"]
        self.assertEqual(source["url"], VIDEO_URL)
        self.assertEqual(source["youtube_video_id"], "M7eQUHH-oWI")
        self.assertEqual(source["published_date"], "2026-03-21")
        self.assertEqual(source["creator"], "Superintelligence")
        self.assertIn("Riemann Hypothesis by Brute Force?", source["title"])
        self.assertIn("screenshot", source["provenance"].lower())
        self.assertIn(VIDEO_URL, self.video_note)
        self.assertIn(VIDEO_URL, self.gap_note)

    def test_no_transcript_or_rights_claim(self):
        source = self.audit["media_reference"]
        self.assertIs(source["transcript_reviewed"], False)
        self.assertIs(source["video_or_screenshot_redistributed"], False)
        self.assertIs(source["changes_scientific_certification"], False)
        self.assertIn("not experimental evidence or proof", source["role"])
        self.assertIn("not embedded or redistributed", self.video_note)

    def test_research_evidence_is_not_math_proof(self):
        self.assertEqual(self.audit["variant_count"], 1_000_000)
        self.assertEqual(self.audit["rips_h01_sample_size_per_family"], 128)
        self.assertEqual(self.audit["zero_sets_computed"], 0)
        flags = self.audit["scientific_claims"]
        for key in (
            "riemann_hypothesis_proved",
            "nontrivial_zeta_zero_certified",
            "topological_zero_correspondence_proved",
            "bsd_or_selmer_rank_proved",
            "new_mathematical_novelty_established",
            "independent_math_review_completed",
        ):
            self.assertIs(flags[key], False, key)
        self.assertIn("Li-prefix countermodel", self.video_note)
        self.assertIn("not a theorem", self.video_note)


if __name__ == "__main__":
    unittest.main()
