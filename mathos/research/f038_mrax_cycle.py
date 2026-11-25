"""Local MRA-X v1.0 stage gate adapter; no provider or acceptance authority."""
import hashlib
import json
from pathlib import Path
from mathos.research.f038_tectx_cycle import run_attempt,require
from mathos.research.tga_pnp_resolution_gap import graph

ROLES=('planner','construct','alternative','critic','cost','verify','impact')
SCHEMA={
 'planner':{'target_id':str,'question':str,'strategy':str,'alternative':str,'stop_rule':str,'literature_leads':list},
 'construct':{'claim':str,'scope':str,'derivation':str,'unresolved_steps':list,'candidate_tests':list},
 'alternative':{'claim':str,'scope':str,'derivation':str,'unresolved_steps':list,'candidate_tests':list},
 'critic':{'objections':list,'counterexample_candidates':list,'equivalence_audit':str,'barrier_audit':str,'recommended_disposition':str},
 'cost':{'computational_model':str,'cost_ledger':dict,'missing_bounds':list,'conclusion':str},
 'verify':{'supported_steps':list,'unsupported_steps':list,'proof_obligations':list,'formalization_plan':str,'verdict':str},
 'impact':{'disposition':str,'claimed_impact':str,'remaining_gaps':list,'next_question':str,'human_review_requests':list}}
LEDGER=('encoding','preprocessing','inference','repetitions','arithmetic_bits','memory','reconstruction','overall')


def gate(plan):
    g=graph()
    stages=plan.get('mrax')
    require(type(stages) is dict and set(stages)==set(ROLES),'invalid stage set')
    for role in ROLES:
        s=stages[role]
        require(type(s) is dict and set(s)==set(SCHEMA[role]),'invalid stage fields: '+role)
        for key,typ in SCHEMA[role].items():
            v=s[key]
            require(type(v) is typ,'invalid field type: '+role+'.'+key)
            if typ is str:
                require(bool(v.strip()),'empty text')
            if typ is list:
                require(all(type(x) is str and bool(x.strip()) for x in v),'invalid list entry')
    target=stages['planner']['target_id']
    require(target in g and g[target].state=='open' and target in plan['targets'],'invalid target')
    require(plan.get('promotion')=='NONE','automatic acceptance prohibited')
    require(stages['construct']['claim']!=stages['alternative']['claim'],'duplicate candidate statement')
    ledger=stages['cost']['cost_ledger']
    require(set(ledger)==set(LEDGER) and all(type(v) is str and v.strip() for v in ledger.values()),
            'invalid cost ledger')
    require(bool(stages['cost']['missing_bounds']) and bool(stages['impact']['remaining_gaps']),
            'universal gaps must remain explicit')
    if stages['critic']['recommended_disposition']!='restricted_result':
        return 'STOP_CRITIC'
    if stages['cost']['conclusion']!='restricted_bound_only':
        return 'STOP_COST'
    if stages['verify']['verdict']!='ready_for_finite_check':
        return 'STOP_VERIFY'
    if stages['impact']['disposition']!='restricted_result':
        return 'STOP_IMPACT'
    return 'PROCEED_RESTRICTED'


def run_mrax(path,audit):
    plan=json.loads(Path(path).read_text())
    disposition=gate(plan)
    print('MRAX_STAGE_GATE '+disposition,flush=True)
    require(disposition=='PROCEED_RESTRICTED','candidate stopped before experiment')
    # TECT-X performs the actual pre-gap, experiment, evidence hashing and post-gap check.
    result=run_attempt(path,audit)
    stages=plan['mrax']
    record={'attempt_id':plan['attempt_id'],'stage_order':list(ROLES),
            'stage_sha256':{k:hashlib.sha256(json.dumps(stages[k],sort_keys=True).encode()).hexdigest()
                            for k in ROLES},
            'stage_origin':'AUTHORED_LOCAL_RECORDS_NOT_LIVE_API_CALLS',
            'construct_and_alternative':'DISTINCT_MATHEMATICAL_TRACKS_NOT_INDEPENDENT_AGENTS',
            'gate':disposition,'evidence_status':'FINITE_AUDIT_MATCHED',
            'gap_disposition':result['gap_disposition'],'promotion':'NONE',
            'PNP_RESOLUTION_STATUS':'OPEN','independent_review':'NOT_SUPPLIED'}
    print(json.dumps(record,sort_keys=True))
    print('MRAX_POST_GATE_OK status=OPEN promotion=NONE')
    return record
