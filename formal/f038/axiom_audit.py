#!/usr/bin/env python3
"""FV-08: generate full named-theorem axiom audit, and enforce a strict log policy.
The parser verifies compiler output, not source text as proof evidence.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = ["F038Formal", *("F038Formal." + m for m in (
    "Certificate", "Reduction", "Bridge", "Resources", "Physical", "Composition",
    "CertificateTests", "ReductionTests", "ResourcesTests", "PhysicalTests", "CompositionTests",
    "LocalMaterialization", "LocalMaterializationTests"))]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
DECL = re.compile(r"^(?:@\[[^\n]*\]\s+)?theorem\s+([A-Za-z_][\w']*)\b", re.M)
NS = re.compile(r"^namespace\s+([\w.]+)\s*$", re.M)
RESULT = re.compile(r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$", re.M)

def inventory():
    names = []
    for module in MODULES:
        source = (ROOT / (module.replace(".", "/") + ".lean")).read_text()
        namespaces = NS.findall(source)
        if len(namespaces) != 1:
            raise ValueError(f"unsupported namespace layout: {module}")
        names.extend(namespaces[0] + "." + name for name in DECL.findall(source))
    if not names or len(names) != len(set(names)):
        raise ValueError("empty or duplicate theorem inventory")
    return names

def validate(log, expected):
    if re.search(r"\bsorryAx\b|declaration uses .sorry.", log):
        raise ValueError("admitted proof")
    found = {}
    for name, deps in RESULT.findall(log):
        if name not in expected or name in found:
            raise ValueError(f"unexpected or duplicate axiom report: {name}")
        axioms = {x.strip() for x in deps.split(",") if x.strip()}
        if not axioms <= ALLOWED:
            raise ValueError(f"non-allowlisted axiom in {name}: {sorted(axioms-ALLOWED)}")
        found[name] = sorted(axioms)
    if set(found) != set(expected):
        raise ValueError(f"missing axiom reports: {sorted(set(expected)-set(found))}")
    return {"theorems": len(found), "allowedAxioms": sorted(ALLOWED), "dependencies": found}

def self_test():
    expect = ["A", "B"]
    good = "'A' depends on axioms: [propext, Classical.choice, Quot.sound]\n'B' does not depend on any axioms\n"
    assert validate(good, expect)["theorems"] == 2
    for bad in [good.replace("propext", "sorryAx"), good.replace("propext", "customAxiom"),
                good.splitlines()[0], good + good, good.replace("'B'", "'C'")]:
        try:
            validate(bad, expect)
        except ValueError:
            continue
        raise AssertionError("bad log accepted")
    print("FV08_AXIOM_PARSER_SELF_TEST_OK")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "self-test":
        self_test()
    elif cmd == "generate":
        names = inventory()
        Path(sys.argv[2]).write_text("\n".join(["import " + m for m in MODULES]
            + ["", *("#print axioms " + n for n in names), ""]))
        print(f"Generated {len(names)} named theorem checks")
    elif cmd == "verify":
        print(json.dumps(validate(Path(sys.argv[2]).read_text(), inventory()), indent=2))
    else:
        raise ValueError("unknown command")
