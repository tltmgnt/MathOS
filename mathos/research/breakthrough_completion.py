"""End-to-end completion gate for the two explicitly scoped cycle-six cases."""
from fractions import Fraction
from pathlib import Path
import json
from mathos.research import breakthrough_cycle6 as cycle
from scripts.millennium_docx import verify

ROOT=Path(__file__).resolve().parents[2]
D=ROOT/"docs/research/breakthrough"


def audit():
    manifest=json.loads((D/"cycle6-completion.json").read_text())
    evidence=json.loads((D/"cycle6-evidence.json").read_text())
    policy=json.loads((D.parent/"BREAKTHROUGH_USE_CASE_POLICY.v1.json").read_text())
    report=cycle.run()
    if report!=evidence["report"]:
        raise ValueError("replay mismatch")
    if manifest["source_commit"]!=evidence["source_commit"] or manifest["workflow_run"]!=evidence["workflow_run"]:
        raise ValueError("source mismatch")
    if manifest["global_promotion"]!="NONE" or report["promotion"]!="NONE" or report["open_obligations"]!=14:
        raise ValueError("global status promotion forbidden")
    if policy["independent_review"]!="OPTIONAL_NONBLOCKING" or manifest["independent_review"]!="NOT_PERFORMED_NONBLOCKING":
        raise ValueError("review status inaccurate")
    if {x["id"] for x in policy["active_cases"]}!={x["id"] for x in manifest["cases"]}:
        raise ValueError("case coverage mismatch")
    expected={"PNP-AND-XOR":("PNP-B006","COMPLETED_SCOPED"),
              "BSD-E41-P5":("BSD-B006","COMPLETED_SCOPED_UNDER_CITED_THEOREMS")}
    for x in manifest["cases"]:
        if (x["paper"],x["status"])!=expected[x["id"]]:
            raise ValueError("scope mismatch")
    p=report["results"]["PNP-B006"]["controls"]
    b=report["results"]["BSD-B006"]["controls"]
    if not p["use_case_completed"] or p["exhaustive_cases"]!=3375 or p["tampered_certificates_rejected"]!=2 or p["general_sat_runtime_proved"]:
        raise ValueError("SAT exit failed")
    c=b["certificate"]
    v=Fraction(c["normalized_hecke_value"])
    N=int(c["scaled_integer"]);D0=int(c["scale_denominator"]);M=int(c["fixed_point_scale"])
    lo,hi=map(int,c["scaled_interval_integer_endpoints"])
    if Fraction(N,D0)!=v or not ((N-1)*M<lo<=N*M<=hi<(N+1)*M) or N%125!=50 or D0%5==0:
        raise ValueError("Hecke certificate inconsistent")
    if not b["sha_5_primary_trivial_under_CLS_theorem"] or b["all_prime_sha_finiteness_proved"]:
        raise ValueError("arithmetic scope mismatch")
    if any(x["intake"]["external_review_verified"] for x in report["results"].values()):
        raise ValueError("invented independent review")
    papers=sorted(D.glob("*-B[0-9][0-9][0-9].md"))
    if len(papers)!=12:
        raise ValueError("paper library mismatch")
    for src in papers: verify(src,src.with_suffix(".docx"))
    return {"completed_scoped_cases":2,"validated_docx":len(papers),"replay_matches":True,
            "independent_review":"NOT_PERFORMED_NONBLOCKING","canonical_open_obligations":14,
            "global_promotion":"NONE"}

if __name__=="__main__":print(json.dumps(audit(),indent=2))
