import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "proctor_preflight", Path(__file__).resolve().parents[1] / "scripts/proctor_preflight.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PreflightTests(unittest.TestCase):
    def test_replay_failure_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proctor-example.yml"
            path.write_text("jobs:\n  replay:\n    steps:\n      - run: 'false | true'\n")
            with self.assertRaises(module.subprocess.CalledProcessError):
                module.replay(path)

    def test_replay_preserves_path_between_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proctor-example.yml"
            path.write_text(
                "jobs:\n  replay:\n    steps:\n"
                "      - run: echo /test-preflight >> \"$GITHUB_PATH\"\n"
                "      - run: 'test \"${PATH%%:*}\" = /test-preflight'\n"
            )
            module.replay(path)

    def test_selects_changed_workflow_and_excludes_self(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            text = "on:\n  pull_request:\n    paths:\n      - 'formal/ProctorTest.lean'\n"
            for name in ["proctor-f034-test.yml", module.PREFLIGHT]:
                (workflows / name).write_text(text)
            with patch.object(module, "ROOT", root), patch.object(module, "WORKFLOWS", workflows):
                self.assertEqual([p.name for p in module.select_workflows(["formal/ProctorTest.lean"])],
                                 ["proctor-f034-test.yml"])


if __name__ == "__main__":
    unittest.main()
