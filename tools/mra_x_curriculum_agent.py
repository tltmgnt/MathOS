"""Bounded curriculum research agent. Executes labs, not academic certification."""
import argparse
import hashlib
import itertools
import json
import math
import sqlite3
from pathlib import Path
from contextlib import closing

import mra_x_gap_agent as gap
import mra_x_topology as ref

# id, topic, lab, prerequisites, open acceptance obligation (if any)
MODULES = [
 ('MATH-101','Discrete mathematics','domains',(),None),
 ('MATH-102','Mathematical logic','logic',('MATH-101',),None),
 ('MATH-103','Optimization theory','optimum',('MATH-101',),None),
 ('TGA-201','Graph theory','graphs',('MATH-101',),None),
 ('TGA-202','Structural topology','width',('TGA-201',),None),
 ('TGA-203','Gap analysis engineering','inventory',('TGA-202',),None),
 ('MRA-301','Constraint reasoning','families',('MATH-102','MATH-103'),None),
 ('MRA-302','Variable elimination','orders',('MRA-301','TGA-202'),None),
 ('MRA-303','Compositional reasoning','witness',('MRA-302',),None),
 ('REX-401','Computational theory','tape_control',('MATH-102',),None),
 ('REX-402','Restricted-memory computation',None,('REX-401',),'Implement an explicit RE-X single-tape encoding, transition table and persistent witnesses.'),
 ('REX-403','Physical-logical equivalence',None,('REX-402','MRA-303'),'Replay generalized elimination on the actual machine and establish time/space and equivalence bounds.'),
 ('AI-501','Agent architecture','planner',('TGA-203',),None),
 ('AI-502','Multi-agent orchestration','campaign',('AI-501','MRA-303'),None),
 ('AI-503','Neuro-symbolic intelligence','advisory',('AI-502',),None),
 ('VER-601','Mathematical proof engineering','projection',('MRA-302',),None),
 ('VER-602','Computational verification','failure',('AI-502',),None),
 ('VER-603','Mechanized proof systems',None,('VER-601',),'Provide a pinned Lean kernel replay of the general elimination theorem, with axiom and proposition audit.'),
 ('OPT-701','Computational complexity','complexity',('TGA-202','MRA-302'),None),
 ('OPT-702','Adaptive strategy selection','heldout',('AI-502','OPT-701'),None),
 ('OPT-703','Incremental reasoning',None,('MRA-303',),'Implement incremental repair and prove/test invalidation against full recomputation.'),
 ('RES-801','Automated scientific discovery','replay',('VER-602','OPT-702'),None),
 ('RES-802','Competitive intelligence',None,('OPT-702',),'Run frozen matched benchmarks with Toulbar2, CP-SAT and Z3; retain time, memory and failures.'),
 ('RES-803','Governed autonomous evolution',None,('REX-403','VER-603','OPT-703','RES-802'),'Integrate persistent research learning and sandboxed candidate code proposals with independent review; no auto-merge.'),
]


def require(ok):
    if not ok:
        raise ValueError('lab acceptance check failed')


def sample(family, seed, trial=1):
    d, variants = gap.build(family, seed, trial)
    return d, variants[0][1]


def run_lab(lab, seed, cache, model):
    if lab == 'domains':
        d = {'a':2,'b':3,'c':4}
        rows = list(ref.assignments(d, tuple(d)))
        require(len(set(rows)) == math.prod(d.values()) == 24)
        return {'assignments':len(rows)}
    if lab == 'logic':
        neq = {(0,1):0,(1,0):0}
        d = dict.fromkeys('abc',2)
        f = [(('a','b'),neq),(('b','c'),neq),(('c','a'),neq)]
        require(ref.solve(d,f)['optimum'] is None and ref.solve(d,f[:2])['optimum']==0)
        return {'odd_cycle':'infeasible','path':'feasible'}
    if lab == 'optimum':
        d={'x':3}; f=[(('x',),{(0,):7,(1,):-4,(2,):3})]
        r=ref.solve(d,f); require(r['optimum']==-4 and r['witness']=={'x':1})
        return {'optimum':-4,'witness':r['witness']}
    if lab in ('graphs','width'):
        widths={}
        for family in gap.FAMILIES:
            d,f=sample(family,seed)
            order=ref.min_fill(d,f); r=ref.solve(d,f,order)
            require(len(order)==len(d) and set(order)==set(d))
            widths[family]=r['induced_width']
        require(widths['isolated']==0 and widths['chain']==1 and widths['dense']==6)
        return {'induced_widths':widths,'scope':'min-fill orders, not optimal treewidth'}
    if lab == 'inventory':
        require(len(gap.FAMILIES)==11 and len(gap.OPEN_GATES)==4)
        return {'families':list(gap.FAMILIES),'open_gates':gap.OPEN_GATES}
    if lab in ('families','orders','witness'):
        checks=0
        for i,family in enumerate(gap.FAMILIES):
            for trial in (0,1):
                d,variants=gap.build(family,seed+i,trial)
                for _,f in variants:
                    expected=gap.oracle(d,f)
                    for strategy in (gap.STRATEGIES if lab=='orders' else ('min_fill',)):
                        r=ref.solve(d,f,gap.order_for(strategy,d,f))
                        require(gap.check_result(d,f,expected,r)); checks+=1
        return {'oracle_and_witness_checks':checks}
    if lab == 'tape_control':
        # Finite toy one-tape machine: increment unary input. Not RE-X.
        tape=list('111_'); head=0; state='scan'; steps=0
        delta={('scan','1'):('scan','1',1),('scan','_'):('halt','1',0)}
        while state!='halt' and steps<10:
            state,symbol,move=delta[state,tape[head]]; tape[head]=symbol; head+=move; steps+=1
        require(state=='halt' and ''.join(tape)=='1111')
        return {'toy_transitions':steps,'scope':'unary increment only; no RE-X equivalence'}
    if lab == 'planner':
        require(gap.priority_plan(['bad'])[1]=='deterministic_fallback')
        require(gap.priority_plan(list(gap.FAMILIES))[1]=='accepted_advisory_priority')
        return {'valid_plan_accepted':True,'invalid_plan_rejected':True}
    if lab == 'campaign':
        r=gap.campaign(1,seed=seed); require(r['status']=='completed' and not r['counterexamples'])
        cache['campaign']=r
        return {'instances':r['instances'],'candidate_checks':r['candidate_checks'],'evidence_sha256':r['evidence_sha256']}
    if lab == 'advisory':
        if model:
            plan=gap.model_plan(model); p,status=gap.priority_plan(plan)
            require(status=='accepted_advisory_priority')
            return {'mode':'live_advisory','priority':p,'model':model}
        p,status=gap.priority_plan(None); require(status=='deterministic_fallback')
        return {'mode':'offline_fallback_only','live_model_tested':False,'priority':p}
    if lab == 'projection':
        # Bounded check of conditional minimum identity for every binary cost table on two bits.
        count=0
        for entries in itertools.product((-1,0,1),repeat=4):
            t=dict(zip(itertools.product(range(2),repeat=2),entries))
            m={y:min(t[x,y] for x in range(2)) for y in range(2)}
            for g in itertools.product((-1,0,1),repeat=2):
                require(min(t[x,y]+g[y] for x,y in t)==min(m[y]+g[y] for y in m)); count+=1
        return {'finite_projection_identities':count,'formal_proof':False}
    if lab == 'failure':
        require(gap.campaign(1,seed=seed,budget=1)['status']=='budget_exhausted')
        d,f=sample('chain',seed); r=ref.solve(d,f); expected=gap.oracle(d,f)
        require(gap.check_result(d,f,expected,r)); r['optimum']=expected+1 if expected is not None else 0
        require(not gap.check_result(d,f,expected,r))
        return {'budget_gate':True,'wrong_optimum_rejected':True}
    if lab == 'complexity':
        d,f=sample('dense',seed); r=ref.solve(d,f)
        visits=sum(d[v]*math.prod(d[u] for u in boundary) for v,boundary,_ in r['trace'])
        require(visits==r['assignments_evaluated'])
        return {'enumerations':visits,'width':r['induced_width'],'scope':'logical enumeration, not runtime'}
    if lab == 'heldout':
        # Select strategy using training observations only; then freeze and evaluate on disjoint seeds.
        training=cache['campaign']['evidence']; selected={}
        for family in gap.FAMILIES:
            selected[family]=min(gap.STRATEGIES,key=lambda s:sum(c['visits'] for e in training if e['family']==family for c in e['candidates'] if c['strategy']==s))
        chosen=baseline=0; checks=0
        for i,family in enumerate(gap.FAMILIES):
            d,f=sample(family,seed+100000+i)
            expected=gap.oracle(d,f)
            for strategy in (selected[family],'min_fill'):
                r=ref.solve(d,f,gap.order_for(strategy,d,f)); require(gap.check_result(d,f,expected,r))
                if checks%2==0: chosen+=r['assignments_evaluated']
                else: baseline+=r['assignments_evaluated']
                checks+=1
        return {'heldout_checks':checks,'selected_visits':chosen,'baseline_visits':baseline,'frozen_strategy':selected,'scope':'synthetic held-out seeds, not external benchmarking'}
    if lab == 'replay':
        r=gap.campaign(1,seed=seed); require(r==cache['campaign'])
        return {'exact_campaign_replay':True,'evidence_sha256':r['evidence_sha256']}
    raise ValueError('unknown lab')


def campaign(seed=38019, model=None):
    records={}; cache={}; events=[]
    for code,topic,lab,deps,obligation in MODULES:
        blocked=[d for d in deps if records[d]['status']!='LAB_PASS']
        events.append({'stage':'observe_plan','module':code,'prerequisite_gaps':blocked})
        evidence={}; error=None
        if obligation:
            status='OPEN_RESEARCH'
        elif blocked:
            status='BLOCKED'
        else:
            try:
                evidence=run_lab(lab,seed,cache,model); status='LAB_PASS'
            except Exception as exc:
                status='LAB_FAIL'; error=type(exc).__name__
        records[code]={'topic':topic,'status':status,'prerequisites':list(deps),'blocked_by':blocked,'evidence':evidence,'error':error,'acceptance_obligation':obligation}
        events.append({'stage':'execute_verify_arbitrate_learn','module':code,'status':status})
    sources={Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,gap.__file__,ref.__file__)}
    summary={s:sum(r['status']==s for r in records.values()) for s in ('LAB_PASS','LAB_FAIL','OPEN_RESEARCH','BLOCKED')}
    result={'seed':seed,'requested_model':model,'modules':records,'summary':summary,'events':events,'source_sha256':sources,
            'next_actions':[{'module':c,'task':r['acceptance_obligation']} for c,r in records.items() if r['status']=='OPEN_RESEARCH' and not r['blocked_by']],
            'scope':'bounded research labs only; no curriculum mastery, proof, physical equivalence or deployment promotion'}
    result['evidence_sha256']=gap.digest(result)
    return result


def persist(path, report):
    with closing(sqlite3.connect(str(path))) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS curriculum_runs (hash TEXT PRIMARY KEY, evidence TEXT NOT NULL)')
        db.execute('INSERT OR IGNORE INTO curriculum_runs VALUES (?,?)',(report['evidence_sha256'],gap.canonical(report)))


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--seed',type=int,default=38019)
    p.add_argument('--model'); p.add_argument('--output',type=Path,required=True); p.add_argument('--ledger',type=Path)
    a=p.parse_args(); r=campaign(a.seed,a.model)
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    if a.ledger: persist(a.ledger,r)
    print(json.dumps({'summary':r['summary'],'next_actions':r['next_actions'],'evidence_sha256':r['evidence_sha256']},indent=2))
    return int(bool(r['summary']['LAB_FAIL'] or r['summary']['BLOCKED']))


if __name__=='__main__': raise SystemExit(main())
