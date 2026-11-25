#!/usr/bin/env python3
"""Replay the checked-in Proctor CI shell steps before opening a PR.

Run only on trusted, self-authored source branches. Requires Python 3.11,
PyYAML and Bash; the existing workflows install pinned Lean 4.14.0.
"""
import argparse
import fnmatch
import os
from pathlib import Path
import subprocess
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
PREFLIGHT = "proctor-f034-preflight.yml"


def load(path):
    return yaml.safe_load(path.read_text())


def select_workflows(changed):
    result = []
    for path in sorted(WORKFLOWS.glob("proctor-*.yml")):
        if path.name == PREFLIGHT:
            continue
        if "f034" not in path.name and path.name != "proctor-pnp-adaptive-propagation.yml":
            continue
        document = load(path)
        events = document.get("on", document.get(True, {}))
        trigger = events.get("pull_request", {}) or {}
        patterns = trigger.get("paths", [])
        if path.relative_to(ROOT).as_posix() in changed or any(
            fnmatch.fnmatchcase(file, pattern)
            for file in changed for pattern in patterns
        ):
            result.append(path)
    return result or [WORKFLOWS / "proctor-pnp-adaptive-propagation.yml"]


def replay(path):
    document = load(path)
    for name, job in document["jobs"].items():
        if job.get("strategy") or job.get("if") or job.get("container"):
            raise ValueError(f"{path.name}/{name}: unsupported job configuration")
        if job.get("env") or document.get("env") or job.get("defaults") or document.get("defaults"):
            raise ValueError(f"{path.name}/{name}: unsupported environment or defaults")
        with tempfile.TemporaryDirectory(prefix="proctor-preflight-") as tmp:
            env = os.environ.copy()
            pathfile = Path(tmp) / "path"
            pathfile.touch()
            env["GITHUB_PATH"] = str(pathfile)
            for index, step in enumerate(job["steps"], 1):
                action = step.get("uses", "")
                if action:
                    if not action.startswith(("actions/checkout@", "actions/setup-python@", "actions/upload-artifact@")):
                        raise ValueError(f"Unsupported action: {action}")
                    continue
                command = step["run"]
                if step.get("if") or step.get("env") or step.get("continue-on-error") or step.get("working-directory") or step.get("shell", "bash") != "bash" or "$" + "{{" in command:
                    raise ValueError(f"{path.name}/{name}/{index}: unsupported shell step")
                print(f"=== {path.name}/{name} step {index} ===", flush=True)
                subprocess.run(["bash", "-e", "-u", "-o", "pipefail", "-c", command],
                               cwd=ROOT, env=env, check=True)
                additions = pathfile.read_text().splitlines()
                if additions:
                    env["PATH"] = os.pathsep.join(list(reversed(additions)) + [env["PATH"]])
                    pathfile.write_text("")
    print(f"PREFLIGHT_OK {path.name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/research/pnp-f032-parity-lean")
    parser.add_argument("--workflow", action="append", help="Explicit proctor-*.yml workflow; repeatable")
    parser.add_argument("--list", action="store_true", help="Show selected workflows without executing")
    args = parser.parse_args()
    if args.workflow:
        paths = []
        for name in args.workflow:
            if Path(name).name != name or not name.startswith("proctor-") or not name.endswith(".yml") or name == PREFLIGHT:
                parser.error("expected a Proctor workflow filename, not a path")
            paths.append(WORKFLOWS / name)
    else:
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", args.base + "...HEAD"], cwd=ROOT, text=True
        ).splitlines()
        paths = select_workflows(changed)
    for path in paths:
        if not path.is_file():
            parser.error(f"workflow not found: {path.name}")
        print(path.name, flush=True)
        if not args.list:
            replay(path)


if __name__ == "__main__":
    main()
