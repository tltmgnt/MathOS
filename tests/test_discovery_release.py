import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mathos.research import discovery_release as release


class DiscoveryReleaseTests(unittest.TestCase):
    def packet(self, root):
        for name in release.PAYLOADS:
            release.write_json(root / name, {"fixture": name})
        release.write_json(root / "manifest.json", {
            "schema_version": 1, "source_commit": "a" * 40,
            "sha256": {name: release.digest(root / name) for name in release.PAYLOADS},
        })

    def test_integrity_never_certifies(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.packet(root)
            result = release.verify_packet(root)
            self.assertEqual(result["integrity"], "PASS")
            self.assertFalse(result["external_validation_established"])

    def test_tamper_missing_extra_and_symlink(self):
        for mode in ("tamper", "missing", "extra", "symlink"):
            with self.subTest(mode=mode), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.packet(root)
                path = root / "kernel.json"
                if mode == "tamper":
                    path.write_text("{}")
                elif mode == "missing":
                    path.unlink()
                elif mode == "extra":
                    (root / "extra.json").touch()
                else:
                    path.unlink()
                    path.symlink_to(root / "benchmark.json")
                with self.assertRaises(ValueError):
                    release.verify_packet(root)

    def test_duplicate_manifest_keys_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.packet(root)
            (root / "manifest.json").write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ValueError):
                release.verify_packet(root)

    def test_controls_and_no_promotion(self):
        kernel = {"checked_count": 1, "claims": [
            {"claim_id": "fixture", "formal_result": {"status": "KERNEL_CHECKED_SCOPE_ONLY"}}]}
        benchmark = {"sha256": "fixture", "results": {
            name: {"checked": count, "total": 3} for name, count in release.EXPECTED.items()}}
        replay = {"reproduced": True, "original_sha256": "fixture"}
        portfolio = {"external_independent_reproduction_completed": True}
        review = {"reviews": [{}]}
        result = release.summarize(kernel, benchmark, replay, portfolio, review)
        self.assertFalse(result["level_5_certified"])
        self.assertFalse(result["level_6_certified"])
        self.assertFalse(result["millennium_prize_solution_certified"])
        for failed in ("kernel", "benchmark", "replay"):
            with self.subTest(failed=failed):
                k = dict(kernel, checked_count=0) if failed == "kernel" else kernel
                b = dict(benchmark, results={}) if failed == "benchmark" else benchmark
                r = dict(replay, reproduced=False) if failed == "replay" else replay
                with self.assertRaises(ValueError):
                    release.summarize(k, b, r, portfolio, review)
