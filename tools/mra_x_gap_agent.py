"""MRA-X / RE-X gap campaign: bounded agents, optional model planner, evidence gates."""
import argparse
import hashlib
import itertools
import json
import math
import random
from pathlib import Path

import mra_x_topology as ref

FAMILIES = {
    'isolated': (4, [(0,), (1,)]),
    'chain': (6, [(i,i+1) for i in range(5)]),
    'single_separator': (6, [(0,i) for i in range(1,6)]),
    'joint_branching': (6, [(0,1,i) for i in range(2,6)]),
    'wide_separator': (8, [(0,1,2,3,4,i) for i in range(5,8)]),
    'nested': (8, [(0,1,2),(1,2,3),(1,4),(3,5),(4,6),(5,7)]),
    'cycle': (7, [(i,(i+1)%7) for i in range(7)]),
    'grid': (9, [(i,i+1) for i in range(9) if i%3!=2]+[(i,i+3) for i in range(6)]),
    'dense': (7, list(itertools.combinations(range(7),2))),
    'hypergraph': (7, [(0,1,2,3),(2,3,4,5),(0,4,6)]),
    'dynamic': (7, [(0,1,2),(1,3),(3,4),(4,5),(5,6)]),
}
STRATEGIES = ('min_fill', 'natural', 'reverse', 'small_domain')
OPEN_GATES = {'physical_tape': 'Locate RE-X machine and compile elimination with persistent tape witnesses.',
              'formal': 'Mechanize optimality, termination and physical/logical equivalence.',
              'incremental': 'Prove sound invalidation and reuse after factor edits.',
              'competitive': 'Run matched external solver benchmarks, with time and memory metrics.'}


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def model_plan(model):
    # Opt-in only. Send public synthetic taxonomy, never repository contents or credentials.
    from openai import OpenAI
    prompt = {'families': list(FAMILIES), 'open_gates': OPEN_GATES,
              'task': 'Return JSON object with priority: a permutation of families. Prioritize wider and dynamic gaps. No code or claims.'}
    answer = OpenAI(timeout=30, max_retries=0).responses.create(
        model=model, input=canonical(prompt), max_output_tokens=1000, store=False)
    return json.loads(answer.output_text)['priority']


def priority_plan(proposal):
    if (isinstance(proposal, list) and all(isinstance(x,str) for x in proposal)
            and len(proposal)==len(FAMILIES) and set(proposal)==set(FAMILIES)):
        return proposal, 'accepted_advisory_priority'
    return list(reversed(FAMILIES)), 'deterministic_fallback'


def build(family, seed, trial):
    n, scopes = FAMILIES[family]
    rng = random.Random(seed)
    domains = {str(i): rng.randint(2,3) for i in range(n)}
    target = {v:rng.randrange(d) for v,d in domains.items()}
    factors = []
    for scope in scopes:
        s = tuple(map(str,scope))
        table = {a:rng.randint(-5,9) for a in ref.assignments(domains,s) if rng.random()<.7}
        table.setdefault(tuple(target[v] for v in s),0)
        factors.append((s,table))
    if trial%4==0:
        factors += [(('0',),{(0,):0}), (('0',),{(1,):0})]
    variants = [('base', factors)]
    if family=='dynamic':
        s=('0','3','6')
        variants += [('add',factors+[(s,{a:0 for a in ref.assignments(domains,s) if sum(a)%2==0})]),
                     ('remove',factors[1:])]
    return domains, variants


def order_for(name, domains, factors):
    if name=='min_fill': return ref.min_fill(domains,factors)
    if name=='natural': return list(domains)
    if name=='reverse': return list(reversed(domains))
    return sorted(domains,key=lambda v:(domains[v],v))


def instance_record(domains, factors):
    return {'domains':domains,'factors':[[list(s),[[list(a),c] for a,c in sorted(t.items())]] for s,t in factors]}


def oracle(domains, factors):
    best = None
    for row in itertools.product(*(range(d) for d in domains.values())):
        a = dict(zip(domains,row))
        try:
            c = sum(t[tuple(a[v] for v in s)] for s,t in factors)
        except KeyError:
            continue
        if best is None or c<best: best=c
    return best


def check_result(domains, factors, expected, result):
    if result['optimum']!=expected: return False
    if expected is None: return result['witness'] is None
    w = result['witness']
    return (isinstance(w,dict) and set(w)==set(domains)
            and all(type(w[v]) is int and 0<=w[v]<domains[v] for v in domains)
            and ref.recover(json.loads(json.dumps(result['trace'])))==w
            and ref.score(factors,w)==expected)


def campaign(rounds=2, seed=38018, proposal=None, budget=25000000):
    if not 1<=rounds<=8 or not 1<=budget<=100000000: raise ValueError('bounded rounds/budget required')
    priority, planner = priority_plan(proposal)
    evidence, failures, events = [], [], []
    spent = 0
    stats = {f:{s:0 for s in STRATEGIES} for f in FAMILIES}
    for rnd in range(rounds):
        events.append({'stage':'observe_plan','round':rnd,'priority':priority[:]})
        for family in priority:
            for trial in range(4):
                case_seed = seed + rnd*10000 + list(FAMILIES).index(family)*100 + trial
                domains, variants = build(family,case_seed,trial)
                for edit,factors in variants:
                    # Conservative bound on candidate enumerations and oracle assignments, not wall time.
                    charge = (1+len(STRATEGIES)*len(domains))*math.prod(domains.values())
                    if spent+charge>budget:
                        return finish(evidence,failures,events,spent,'budget_exhausted',planner,rounds,seed)
                    spent += charge
                    record = instance_record(domains,factors)
                    expected = oracle(domains,factors)
                    preferred = min(STRATEGIES,key=lambda s:stats[family][s])
                    candidates = []
                    for strategy in sorted(STRATEGIES,key=lambda s:s!=preferred):
                        try:
                            r = ref.solve(domains,factors,order_for(strategy,domains,factors))
                            ok = check_result(domains,factors,expected,r)
                            c = {'strategy':strategy,'ok':ok,'optimum':r['optimum'],'width':r['induced_width'],'visits':r['assignments_evaluated']}
                        except Exception as exc:
                            c = {'strategy':strategy,'ok':False,'error':type(exc).__name__}
                        candidates.append(c)
                        if not c['ok']:
                            failures.append({'family':family,'seed':case_seed,'edit':edit,'instance':record,'expected':expected,'candidate':c})
                        else: stats[family][strategy]+=c['visits']
                    good=[c for c in candidates if c['ok']]
                    best=min(good,key=lambda c:(c['visits'],c['width'],c['strategy'])) if good else None
                    evidence.append({'family':family,'seed':case_seed,'edit':edit,'instance_sha256':digest(record),
                                     'expected':expected,'preferred':preferred,'candidates':candidates,'selected':best})
                    if failures:
                        return finish(evidence,failures,events,spent,'counterexample',planner,rounds,seed)
        # Prioritize families where the default order has the greatest observed cost overhead.
        priority=sorted(priority,key=lambda f:stats[f]['min_fill']-min(stats[f].values()),reverse=True)
        events.append({'stage':'learn','round':rnd,'preferred_by_family':{f:min(STRATEGIES,key=lambda s:stats[f][s]) for f in FAMILIES}})
    return finish(evidence,failures,events,spent,'completed',planner,rounds,seed)


def finish(evidence,failures,events,spent,status,planner,rounds,seed):
    summary={f:{'instances':0,'verified_candidates':0,'max_width':0,'selected_visits':0,'min_fill_visits':0} for f in FAMILIES}
    for e in evidence:
        s=summary[e['family']]; s['instances']+=1
        s['verified_candidates']+=sum(c['ok'] for c in e['candidates'])
        if e['selected']:
            s['max_width']=max(s['max_width'],*(c.get('width',0) for c in e['candidates']))
            s['selected_visits']+=e['selected']['visits']
        s['min_fill_visits']+=next((c.get('visits',0) for c in e['candidates'] if c['strategy']=='min_fill'),0)
    events.append({'stage':'arbitrate','status':status,'promotion':False})
    out={'status':status,'planner':planner,'rounds_requested':rounds,'seed':seed,'budget_charge':spent,'source_sha256':hashlib.sha256(Path(ref.__file__).read_bytes()).hexdigest(),
         'instances':len(evidence),'candidate_checks':sum(len(e['candidates']) for e in evidence),
         'counterexamples':failures,'families':summary,'events':events,'evidence':evidence,'open_gates':OPEN_GATES,
         'scope':'bounded synthetic logical evidence; dynamic full recomputation; selected order is retrospective; no proof or deployment promotion'}
    out['evidence_sha256']=digest(out)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rounds',type=int,default=2); p.add_argument('--seed',type=int,default=38018)
    p.add_argument('--budget',type=int,default=25000000); p.add_argument('--model'); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); proposal=None; model_error=None
    if args.model:
        try: proposal=model_plan(args.model)
        except Exception as exc: model_error=type(exc).__name__
    result=campaign(args.rounds,args.seed,proposal,args.budget)
    if args.model:
        result.pop('evidence_sha256'); result['requested_model']=args.model; result['model_error']=model_error; result['evidence_sha256']=digest(result)
    with args.output.open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ('status','planner','instances','candidate_checks','families','evidence_sha256')},indent=2))
    raise SystemExit(0 if result['status']=='completed' else 1)


if __name__=='__main__': main()
