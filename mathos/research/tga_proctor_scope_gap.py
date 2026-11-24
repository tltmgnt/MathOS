"""Executable scope diagnostics for Proctor 601; no change to proof states."""
import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from mathos.research import tga_agent as a
from mathos.research import tga_proctor as p
from mathos.research import tga_proctor_unified as u
from mathos.proof_analysis.gap_analysis import Claim, analyze

GAPS={
 "G01":"Formal target registry",
 "G02":"Structured model-generated candidate",
 "G03":"Semantic alignment and translator",
 "G04":"Unbounded arithmetic/induction proof path",
 "G05":"Pinned library proof path",
 "G06":"Trusted isolated execution",
 "G07":"Statement-bound proof acceptance ledger",
 "G08":"Verified dependency edges and graph closure",
 "G09":"Source-aligned specialist formalization",
 "G10":"Evidence-guided search feedback",
 "G11":"Authorized live run and independent deployment replay",
 "G12":"Independent learner outcome evidence",
}
def model():
    g={k:Claim(v,"open") for k,v in GAPS.items()}
    g["baseline"]=Claim("Prior scoped Boolean kernel workflow (assumed from pinned run)","established_external")
    g["M1"]=Claim("Autonomous bounded theorem production","derived",
                  (("baseline","G01","G02","G03","G06","G07","G11"),))
    g["M2"]=Claim("Beyond finite Boolean enumeration","derived",(("M1","G04"),("M1","G05")))
    g["M3"]=Claim("Specialist proof-obligation integration","derived",(("M2","G08","G09","G10"),))
    g["M4"]=Claim("Course quality validation","derived",(("M3","G12"),))
    results={}
    for k in ("M1","M2","M3","M4"):
        r=analyze(g,k)
        results[k]={x:r[x] for x in ("status","minimal_completion_sets","common_to_all_modeled_routes")}
    return results

def prefix_countermodels():
    out=[]
    for n in (0,1,4,16,64,256):
        f=lambda x:int(x>n)
        assert all(f(x)==0 for x in range(n+1))
        assert f(n+1)==1
        out.append({"prefix_end":n,"exact_observations":n+1,"failure_index":n+1,"value":1})
    return out

def controls():
    c=copy.deepcopy(u.DEMO);c.update(variables=5,left=0,right=0)
    try:u.analyze_candidate(c)
    except ValueError:rejected=True
    else:raise AssertionError("expected current bound")
    with TemporaryDirectory() as td:
        root=Path(td)
        a.run(a.Offline(),root/"agent",attempts=2,max_calls=8)
        ck=root/"agent/state.json";state=json.loads(ck.read_text())
        first=u.run(ck,u.DEMO,root/"first")
        second=u.run(ck,dict(u.DEMO,attempt_id=2),root/"second")
        assert first["status"]==second["status"]=="FINITE_CHECK_ONLY"
        assert first["exact_evidence"]==second["exact_evidence"]
        assert first["attempt_sha256"]!=second["attempt_sha256"]
        copy_state=copy.deepcopy(state)
        copy_state["attempts"][0]["roles"]["deriver"]["derivation"]="Changed free-text training control; no proof."
        assert copy_state!=state
        audit=p.audit(copy_state)
        assert audit["status"]=="STRUCTURAL_REPLAY_CONSISTENT"
        assert audit["model_identity_authenticated"] is False
        assert json.loads(ck.read_text())==state
    return {"five_variable_identity_rejected":rejected,
            "same_identity_linked_to_distinct_attempts":[state["attempts"][0]["claim_id"],state["attempts"][1]["claim_id"]],
            "attempt_link_proves_research_relevance":False,
            "changed_free_text_structurally_accepted":True,"original_checkpoint_unchanged":True,
            "model_identity_authenticated":False,
            "prefix_countermodels":prefix_countermodels()}

def run():
    return {"status":"SCOPE_DIAGNOSTICS_ONLY","graph":model(),"controls":controls(),
            "formal_countermodel_replay":"SEPARATE_KERNEL_JOB","canonical_open_obligations":14,
            "global_promotion":"NONE","educational_validation_established":False}

if __name__=="__main__":print(json.dumps(run(),indent=2))
