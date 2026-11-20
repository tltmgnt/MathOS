"""MathOS BSD 08 — fail-closed parsing of external PARI/GP rank evidence.

PARI/GP ellrank does unconditional 2-descent (plus Cassels pairings);
it returns [rank_lower, rank_upper, sha_correction, points].
The documented 2-Selmer dimension is:
  dim Sel_2(E/Q) = rank_upper + dim E(Q)[2] + sha_correction.

This module DOES NOT perform 2-descent, replace independent expert review,
prove an all-parameters rank bound, or determine complex analytic rank.
Only evidence from actual PARI/GP execution may set the observed flags.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
from typing import Any


MARKER = re.compile(
    r"^MATHOS08\|(-?\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)\|(\d+)$"
)
SELECTED = (0, 1, 2, 3, 24, -24)
EXACT_RANK_THREE_CANDIDATES = (2, 3)
ALLOWED_FINAL_STATES = ("GENERATED", "UNVERIFIED", "SUPPORTED")


def curve_parameters(u: int) -> dict[str, int]:
    if type(u) is not int:
        raise TypeError("exact integer parameter required")
    s = u * (u + 1)
    return {
        "u": u,
        "a1": 0, "a2": s // 2, "a3": 1,
        "a4": -(s+2)//2, "a6": 0,
        "discriminant": s**4+10*s**3+34*s*s+60*s+37,
    }


def parse_gp_output(text: str, requested_u: int) -> dict[str, int]:
    markers = [m for line in text.splitlines()
               if (m := MARKER.fullmatch(line.strip())) is not None]
    if len(markers) != 1:
        raise ValueError("expected exactly one complete GP certificate marker")
    u, lo, hi, sha_corr, t2, sel2, points = map(int, markers[0].groups())
    if u != requested_u:
        raise ValueError("GP result parameter does not match requested curve")
    if not (0 <= lo <= hi <= sel2 <= 100):
        raise ValueError("rank intervals or Selmer dimension malformed")
    if t2 not in (0, 1, 2):
        raise ValueError("E(Q)[2] dimension out of range")
    if sha_corr < 0 or sha_corr % 2:
        raise ValueError("Cassels pairing correction must be nonnegative/even")
    if sel2 != hi + t2 + sha_corr:
        raise ValueError("PARI 2-Selmer identity mismatch")
    if points < 0:
        raise ValueError("negative number of points")
    return {
        "u":u, "rank_lower":lo, "rank_upper":hi, "sha_pairing_correction":sha_corr,
        "rational_two_torsion_dim":t2, "two_selmer_dim":sel2,
        "points_returned":points,
    }


def verify_run(root: Path, u: int) -> dict[str, Any]:
    assert u in SELECTED
    raw = root / f"u{u}.gp.log"
    exitpath = root / f"u{u}.exit"
    if not raw.is_file() or not exitpath.is_file():
        return {"u":u, "result":"NOT_RUN", "two_selmer_certified":False}
    data = raw.read_bytes()
    if len(data) > 2_000_000:
        raise ValueError("unexpectedly large CAS output")
    try:
        exit_code = int(exitpath.read_text(encoding="utf-8").strip())
    except ValueError as exc:
        raise ValueError("malformed exit code") from exc
    item = {
        "u":u,"pari_exit_code":exit_code,"stdout_sha256":hashlib.sha256(data).hexdigest(),
        "result":"INCONCLUSIVE" if exit_code else "OBSERVED",
        "two_selmer_certified":False,
    }
    if exit_code != 0:
        item["reason"] = "PARI failed or exceeded resource limit; no rank assertion"
        return item
    result = parse_gp_output(data.decode("utf-8"), u)
    item.update(result)
    item["two_selmer_certified"] = True  # Independent executable two-descent output, NOT peer review.
    item["rank_3_exact_from_run"] = (
        u in EXACT_RANK_THREE_CANDIDATES
        and item["rank_lower"] == item["rank_upper"] == 3
    )
    item["rank_3_upper_bound_from_run"] = (
        u in EXACT_RANK_THREE_CANDIDATES and item["rank_upper"] <= 3
    )
    return item


def report(root: Path, *, source_sha: str = "not-supplied") -> dict:
    runs = [verify_run(root,u) for u in SELECTED]
    success = [r for r in runs if r["result"] == "OBSERVED"]
    return {
        "schema_version":"mathos-bsd08-pari-v1",
        "family":"E_u: y^2+y=x^3+[u(u+1)/2]x^2-[(u(u+1)+2)/2]x",
        "mathematical_claim":"selected rational fibers' rank upper bounds",
        "backend":"PARI/GP ellrank with unconditional two-descent and Cassels pairing",
        "source_commit":source_sha,
        "selected_parameters":list(SELECTED),
        "number_of_successful_computations":len(success),
        "certified_by_executable_2descent_under_CAS_correctness":bool(success),
        "not_independent_human_peer_review":True,
        "infinite_uniform_upper_bound_of_three_proved":False,
        "infinite_exact_rank_three_family_proved":False,
        "analytic_rank_equality_proved":False,
        "mathematical_novelty_established":False,
        "BSD_proved":False,
        "observations":runs,
    }


def create_tect_scenario(result: dict) -> dict:
    """Actual canonical TECT input: local observed evidence, no assurance promotion.

    Controller actors are declared, not authenticated identities.
    Their presence does not constitute independent reproduction.
    """
    now = datetime.now(timezone.utc)
    start = now.isoformat().replace("+00:00", "Z")
    end = (now + timedelta(days=30)).isoformat().replace("+00:00", "Z")
    method="pari-ellrank-2descent-observation"
    policy={
        "actors":{"author":["author"],"validator":["validator"],
                  "adversary":["adversary"],"reproducer":["reproducer"],
                  "reviewer":["reviewer"]},
        "minimum_density":0.2,"minimum_groups":1,"epsilon":0.1,
        "required_attacks":["source_poisoning","contradiction_injection","assumption_violation"],
        "required_validations":[method],
    }
    claim_id="mathos-bsd08-observed-cas-computation"
    ops=[{
        "op":"register","actor":"author",
        "data":{"id":claim_id,
                "statement":"These PARI/GP rank and 2-Selmer upper-bound outputs were observed in one GitHub Actions computational run.",
                "provenance":["local:PARI/GP", "github:tltmgnt/MathOS"],
                "confidence":0.5,
                "assurance_scope":"Observed local computational output only; excludes independent review, infinite rank theorem and BSD"}
    },{
        "op":"transition","actor":"validator",
        "data":{"claim":claim_id,"target":"UNVERIFIED"}
    }]
    if result["number_of_successful_computations"] > 0:
        content=json.dumps(result,sort_keys=True,separators=(",",":")).encode("utf8")
        if len(content)>65536:
            raise ValueError("TECT receipt content exceeds 64KiB")
        receipt={
            "id":"pari-rank-output-01", "claim":claim_id,"claim_version":1,
            "kind":"validation","result":"PASS","source":"local:PARI/GP executed by GitHub CI",
            "method":method,"run_id":"github-actions-one-run","group":"same-cas-run",
            "weight":1.0,"quality":1.0,"reliability":1.0,"independence":0.4,
            "observed_at":start,"expires_at":end,
            "content_base64":base64.b64encode(content).decode("ascii"),
            "sha256":hashlib.sha256(content).hexdigest()
        }
        ops.append({"op":"evidence","actor":"validator","data":receipt})
        ops.append({"op":"transition","actor":"validator",
                    "data":{"claim":claim_id,"target":"SUPPORTED"}})
    return {"schema_version":1,"as_of":start,"policy":policy,"operations":ops}


def main() -> None:
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="mode",required=True)
    a=sub.add_parser("report")
    a.add_argument("--root",required=True)
    a.add_argument("--source-sha",default="not-supplied")
    a.add_argument("--output",required=True)
    a=sub.add_parser("tect-scenario")
    a.add_argument("--report",required=True)
    a.add_argument("--output",required=True)
    args=p.parse_args()
    if args.mode=="report":
        value=report(Path(args.root),source_sha=args.source_sha)
    else:
        value=create_tect_scenario(json.loads(Path(args.report).read_text()))
    Path(args.output).write_text(json.dumps(value,sort_keys=True,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
