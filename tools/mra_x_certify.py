"""Phase VI: checkable ordering and solution certificates, generated topology audit."""
import argparse
import copy
import hashlib
import itertools
import json
import math
import random
import time
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_synthesis as synth


def require(ok):
    if not ok:
        raise ValueError('certificate rejected')


def graph(d, factors):
    g = {v: set() for v in d}
    for s, _ in factors:
        for a, b in itertools.combinations(s, 2):
            g[a].add(b); g[b].add(a)
    return g


def filled(g, eliminated):
    # Independent direct clique-fill implementation, not the reachability DP in Phase V.
    g = {v: set(ns) for v, ns in g.items()}
    for v in eliminated:
        ns = g.pop(v)
        for u in ns:
            g[u].remove(v); g[u].update(ns - {u})
    return g


def transitions(d, g, vs, mask):
    remaining = filled(g, [v for i, v in enumerate(vs) if mask & (1 << i)])
    for i, v in enumerate(vs):
        if v in remaining:
            yield v, mask | (1 << i), d[v] * math.prod(d[u] for u in remaining[v])


def identity(d, f):
    return gap.digest(gap.instance_record(d, f))


def certify_order(d, f):
    ref.validate(d, f); require(len(d) <= 10)
    vs = sorted(d); g = graph(d, f); full = (1 << len(vs)) - 1
    lower = [0] * (full + 1)
    for mask in range(full - 1, -1, -1):
        lower[mask] = min(c + lower[nxt] for _, nxt, c in transitions(d, g, vs, mask))
    order, cost, _, _ = synth.exact_order(d, f)
    return {'instance_sha256': identity(d, f), 'order': order, 'cost': cost, 'potential': lower}


def verify_order(d, f, cert):
    ref.validate(d, f); require(len(d) <= 10)
    require(cert['instance_sha256'] == identity(d, f))
    vs = sorted(d); g = graph(d, f); full = (1 << len(vs)) - 1
    p = cert['potential']; order = cert['order']; cost = cert['cost']
    require(type(p) is list and len(p) == full + 1 and all(type(x) is int and x >= 0 for x in p))
    require(type(cost) is int and p[full] == 0 and p[0] == cost)
    require(type(order) is list and len(order) == len(vs) and set(order) == set(vs))
    edges = 0
    for mask in range(full):
        for _, nxt, c in transitions(d, g, vs, mask):
            require(p[mask] <= c + p[nxt]); edges += 1
    # Upper bound checked by replaying the proposed actual elimination path.
    actual = 0
    for v in order:
        actual += d[v] * math.prod(d[u] for u in g[v]); g = filled(g, [v])
    require(actual == cost)
    return edges


def verify_solution(d, f, result):
    # Recompute the local minimum from every bucket row, with independent witness checking.
    ref.validate(d, f); active = [(tuple(s), dict(t)) for s, t in f]
    order = result['order']; trace = result['trace']
    require(len(order) == len(d) and set(order) == set(d) and len(trace) == len(d))
    visits = width = 0; choices = []
    for v, record in zip(order, trace):
        bucket = [(s,t) for s,t in active if v in s]
        active = [(s,t) for s,t in active if v not in s]
        boundary = sorted({u for s,_ in bucket for u in s} - {v})
        require(record[0] == v and record[1] == boundary)
        claimed = {}
        for row, x in record[2]:
            require(tuple(row) not in claimed and type(x) is int and 0 <= x < d[v])
            claimed[tuple(row)] = x
        projected = {}; chosen = {}; width = max(width, len(boundary))
        for row in itertools.product(*(range(d[u]) for u in boundary)):
            a = dict(zip(boundary, row)); candidates = []
            for x in range(d[v]):
                a[v] = x; visits += 1
                vals = [t.get(tuple(a[u] for u in s)) for s,t in bucket]
                if None not in vals: candidates.append((sum(vals), x))
            if candidates:
                val, x = min(candidates); projected[row] = val; chosen[row] = x
        require(chosen == claimed); choices.append((v, boundary, chosen)); active.append((tuple(boundary), projected))
    vals = [t.get(()) for _,t in active]; opt = None if None in vals else sum(vals)
    require(result['optimum'] == opt and result['assignments_evaluated'] == visits and result['induced_width'] == width)
    witness = None
    if opt is not None:
        witness = {}
        for v, boundary, chosen in reversed(choices): witness[v] = chosen[tuple(witness[u] for u in boundary)]
        require(sum(t[tuple(witness[u] for u in s)] for s,t in f) == opt)
    require(result['witness'] == witness)
    return visits


def generated(seed):
    rng = random.Random(seed); n = rng.randint(5, 9); vs = [str(i) for i in range(n)]
    d = {v:rng.randint(2,3) for v in vs}; density = rng.choice((.15,.35,.55,.8))
    scopes = [s for s in itertools.combinations(vs,2) if rng.random() < density]
    for _ in range(rng.randrange(4)):
        scopes.append(tuple(sorted(rng.sample(vs,rng.randint(3,min(4,n))))))
    target = {v:rng.randrange(d[v]) for v in vs}; f = []
    for s in scopes:
        t = {a:rng.randint(-7,9) for a in ref.assignments(d,s) if rng.random()<.65}
        t.setdefault(tuple(target[v] for v in s),0); f.append((s,t))
    if seed%5 == 0: f.append(((vs[0],),{}))
    return d,f


def signature(d,f):
    g = graph(d,f); unseen = set(g); components = 0
    while unseen:
        pending = {min(unseen)}; components += 1
        while pending:
            v = pending.pop()
            if v in unseen: unseen.remove(v); pending.update(g[v] & unseen)
    edges = sum(map(len,g.values()))//2
    return [len(d), edges, components, edges-len(d)+components, max((len(s) for s,_ in f),default=0), sorted(map(len,g.values()))]


def audit():
    rows=[]; controls=0; signatures=set(); certificates=[]
    for seed in range(6100,6160):
        d,f=generated(seed); sig=signature(d,f); signatures.add(json.dumps(sig))
        start=time.perf_counter_ns(); c=certify_order(d,f); result=ref.solve(d,f,c['order']); certified_ns=time.perf_counter_ns()-start
        start=time.perf_counter_ns(); edges=verify_order(d,f,c); visits=verify_solution(d,f,result); verification_ns=time.perf_counter_ns()-start
        start=time.perf_counter_ns(); b,_=synth.baseline(d,f); base=ref.solve(d,f,b); baseline_ns=time.perf_counter_ns()-start
        expected=gap.oracle(d,f)
        require(gap.check_result(d,f,expected,result) and gap.check_result(d,f,expected,base) and visits<=base['assignments_evaluated'])
        rows.append({'seed':seed,'signature':sig,'instance_sha256':c['instance_sha256'],'feasible':expected is not None,'exact':visits,'baseline':base['assignments_evaluated'],'inequalities':edges,'certified_ns':certified_ns,'verification_ns':verification_ns,'baseline_ns':baseline_ns})
        certificates.append({'seed':seed,'instance':gap.instance_record(d,f),'order_certificate':c,'solution_certificate':result})
        if seed==6101:
            for key,value in [('cost',c['cost']+1),('instance_sha256','0'*64),('order',c['order'][:-1]),('potential',[0]*len(c['potential']))]:
                bad=copy.deepcopy(c); bad[key]=value
                try: verify_order(d,f,bad)
                except ValueError: controls+=1
                else: raise ValueError('accepted invalid order certificate')
            for key,value in [('optimum',result['optimum']+1),('witness',{}),('trace',result['trace'][:-1]),('assignments_evaluated',visits+1)]:
                bad=copy.deepcopy(result); bad[key]=value
                try: verify_solution(d,f,bad)
                except ValueError: controls+=1
                else: raise ValueError('accepted invalid solution certificate')
    out={'rows':rows,'certificates':certificates,'distinct_feature_signatures':len(signatures),'rejected_controls':controls,'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,synth.__file__,synth.up.__file__,synth.evo.__file__)},'scope':'bounded synthetic generated instances; feature signatures are not isomorphism classes; checkable certificates, not kernel-verified proofs; timings are exploratory single-pass and include certificate generation only in candidate time'}
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({'cases':len(r['rows']),'feasible':sum(x['feasible'] for x in r['rows']),'signatures':r['distinct_feature_signatures'],'controls':r['rejected_controls'],**{k:sum(x[k] for x in r['rows']) for k in ('exact','baseline','inequalities','certified_ns','verification_ns','baseline_ns')}},indent=2))
