"""Explicit ResearchOS / TECT-X attempt gate; evidence bookkeeping, never proof promotion."""
import hashlib
import json
from pathlib import Path
from mathos.proof_analysis.gap_analysis import Claim, analyze
from mathos.research.tga_pnp_resolution_gap import graph, report


def require(condition,message):
    if not condition:
        raise ValueError(message)


def validate(plan,g):
    fields=('attempt_id','base_commit','base_replay','hypothesis','route','topology',
            'scope','cost','gap_disposition','independent_reference','next')
    require(all(isinstance(plan.get(k),str) and plan[k] for k in fields),'missing plan field')
    require(plan.get('promotion')=='NONE','automatic promotion is forbidden')
    require(plan['gap_disposition'] in ('NARROWED_RESTRICTED_CASE_ONLY','NO_CHANGE',
            'BARRIER_IDENTIFIED','CANDIDATE_REQUIRES_REVIEW'),'unsupported disposition')
    require(bool(plan.get('targets')) and all(k in g and g[k].state=='open'
            for k in plan['targets']),'targets must be existing open claims')
    require(plan['route'] in g and g[plan['route']].state=='derived','unknown route')
    require(bool(plan.get('adversarial')) and bool(plan.get('expected')) and
            bool(plan.get('evidence_sources')),'missing tests or evidence sources')


def compact(r):
    return {k:{'status':r[k]['status'],
               'minimal_completion_sets':r[k]['minimal_completion_sets']}
            for k in ('certificate_route','selector_route','mathematical_resolution','evidence_gate')}


def run_attempt(plan_path,audit):
    p=Path(plan_path)
    data=p.read_bytes()
    plan=json.loads(data)
    g=graph()
    validate(plan,g)
    before=report()
    require(before['PNP_RESOLUTION_STATUS']=='OPEN','unexpected base status')
    require(before['mathematical_resolution']['status']=='BLOCKED','unexpected base closure')
    # Candidate-specific subgraph; no status promotion from executable checks.
    local=dict(g)
    local['attempt_soundness_review']=Claim('Independent review of candidate guarded-affine derivation','open')
    local['attempt_full_affine_integration']=Claim('Full affine separator-query integration and total resource accounting','open')
    local['attempt_route']=Claim('Candidate hybrid route review and universal completion','derived',(
        tuple(plan['targets'])+('attempt_soundness_review','attempt_full_affine_integration'),))
    local_before=analyze(local,'attempt_route')
    print('TECTX_PRE_GAP_OK targets='+','.join(plan['targets'])+' status=OPEN',flush=True)
    observed=audit()
    require(observed==plan['expected'],'attempt metrics differ from plan')
    after=report()
    require(before==after,'global gap status or dependency change requires separately reviewed evidence')
    local_after=analyze(local,'attempt_route')
    require(local_before==local_after,'candidate review cannot be auto-promoted')
    evidence={}
    for name in plan['evidence_sources']:
        f=Path(name)
        require(not f.is_absolute() and '..' not in f.parts,'invalid evidence path')
        evidence[name]=hashlib.sha256(f.read_bytes()).hexdigest()
    result={'attempt_id':plan['attempt_id'],'base_commit':plan['base_commit'],
            'plan_sha256':hashlib.sha256(data).hexdigest(),'targets':plan['targets'],
            'pre_gap':compact(before),'post_gap':compact(after),
            'local_open_completion_sets':local_after['minimal_completion_sets'],
            'evidence_sha256':evidence,'observed':observed,
            'gap_disposition':plan['gap_disposition'],'topology':plan['topology'],
            'scope':plan['scope'],'cost':plan['cost'],'adversarial':plan['adversarial'],
            'independent_reference':plan['independent_reference'],
            'mathematical_review':'NOT_SUPPLIED','lean_proof':'NOT_SUPPLIED',
            'exact_head_ci':'CHECK_EXTERNALLY','promotion':'NONE',
            'PNP_RESOLUTION_STATUS':'OPEN','next':plan['next']}
    print(json.dumps(result,sort_keys=True))
    print('TECTX_POST_GAP_OK status=OPEN promotion=NONE')
    return result
