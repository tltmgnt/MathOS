"""Phase VII: component-wise certified planning, bounded exact solving and tape audit."""
import argparse
import hashlib
import json
import random
from pathlib import Path

import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_upgrade as up
import mra_x_certify as cert
import mra_x_tape as tape
from mra_x_frontier import highs


def require(ok):
    if not ok:
        raise ValueError('unified evidence check failed')


def partition(d, f):
    ref.validate(d, f)
    g = cert.graph(d, f)
    unseen = set(d); parts = []
    while unseen:
        todo = [min(unseen)]; seen = set()
        while todo:
            v = todo.pop()
            if v not in unseen: continue
            unseen.remove(v); seen.add(v); todo.extend(sorted(g[v] & unseen))
        parts.append(tuple(sorted(seen)))
    owner = {v:i for i,p in enumerate(parts) for v in p}
    buckets = [[] for _ in parts]; constants = []
    for s,t in f:
        if not s: constants.append((s,t)); continue
        i = owner[s[0]]
        require(all(owner[v]==i for v in s)); buckets[i].append((s,t))
    return [( {v:d[v] for v in p}, b) for p,b in zip(parts,buckets)], constants


def solve(d, f, budget=1000000, tape_audit=False):
    if type(budget) is not int or not 1<=budget<=10000000: raise ValueError('invalid enumeration budget')
    if len(d)>256 or any(not isinstance(v,str) or not 1<=k<=4 for v,k in d.items()) or len(f)>2048:
        raise ValueError('outside unified envelope')
    parts, constants = partition(d,f); planned=[]; predicted=0
    for sd,sf in parts:
        # Avoid exponential exact planning on components beyond the existing limit.
        c=cert.certify_order(sd,sf) if len(sd)<=10 else None
        o=c['order'] if c else up.choose(sd,sf)[1]
        work,width=up.predict(sd,sf,o); predicted+=work
        if predicted>budget:
            return {'status':'BUDGET_EXHAUSTED','predicted_lower_limit':predicted,'budget':budget}
        planned.append((sd,sf,o,c,work))
    optimum=ref.score(constants,{}); witness={}; trace=[]; order=[]; width=visits=0; reports=[]
    for sd,sf,o,c,work in planned:
        r=ref.solve(sd,sf,o); require(r['assignments_evaluated']==work)
        inequalities=cert.verify_order(sd,sf,c) if c else 0
        cert.verify_solution(sd,sf,r)
        tr=None
        if tape_audit and len(sd)<=8 and len(sf)<=32 and all(abs(x)<=10 for _,t in sf for x in t.values()):
            m=tape.Machine(sd,[s for s,_ in sf],o); tr=m.run(m.input(sf))
            require(m.decode(tr)=={k:r[k] for k in ('optimum','witness','trace')})
            tr=tr['transitions']
        if optimum is None or r['optimum'] is None: optimum=None
        else: optimum+=r['optimum']
        if r['witness'] is not None: witness.update(r['witness'])
        trace.extend(r['trace']); order.extend(o); width=max(width,r['induced_width']); visits+=work
        reports.append({'variables':sorted(sd),'order_certificate':c,'inequalities':inequalities,'visits':work,'tape_transitions':tr})
    result={'optimum':optimum,'witness':witness if optimum is not None else None,'trace':trace,'order':order,'induced_width':width,'assignments_evaluated':visits}
    require(cert.verify_solution(d,f,result)==visits)
    return {'status':'SOLVED','result':result,'components':reports,'globally_optimal_enumeration_order':all(x['order_certificate'] is not None for x in reports),'instance_sha256':cert.identity(d,f)}


def verify(d,f,report):
    require(report['status']=='SOLVED' and report['instance_sha256']==cert.identity(d,f))
    parts,_=partition(d,f); records=report['components']; require(len(parts)==len(records))
    order=[]; visits=0
    for (sd,sf),r in zip(parts,records):
        require(r['variables']==sorted(sd))
        c=r['order_certificate']
        o=[v for v in report['result']['order'] if v in sd]
        if c is not None:
            require(c['order']==o and cert.verify_order(sd,sf,c)==r['inequalities'])
        else: require(r['inequalities']==0)
        require(up.predict(sd,sf,o)[0]==r['visits']); visits+=r['visits']; order.extend(o)
        if r['tape_transitions'] is not None:
            m=tape.Machine(sd,[s for s,_ in sf],o); tr=m.run(m.input(sf))
            require(tr['transitions']==r['tape_transitions'])
            local=ref.solve(sd,sf,o); require(m.decode(tr)=={k:local[k] for k in ('optimum','witness','trace')})
    require(order==report['result']['order'] and visits==report['result']['assignments_evaluated'])
    require(report['globally_optimal_enumeration_order'] is all(r['order_certificate'] is not None for r in records))
    cert.verify_solution(d,f,report['result']); return True


def network(seed, blocks, size, connected=False):
    rng=random.Random(seed); d={}; f=[]
    for b in range(blocks):
        vs=[f'{b:02d}:{i:02d}' for i in range(size)]
        d.update({v:rng.randint(2,3) for v in vs})
        scopes=[(vs[i],vs[i+1]) for i in range(size-1)]
        if not connected and size>=4: scopes.extend([(vs[0],vs[2],vs[3]),(vs[0],vs[-1])])
        target={v:rng.randrange(d[v]) for v in vs}
        for s in scopes:
            t={a:rng.randint(-5,7) for a in ref.assignments(d,s) if rng.random()<.7}
            t.setdefault(tuple(target[v] for v in s),0); f.append((s,t))
    f.append(((),{():-3}))
    if seed%5==0:
        v=next(iter(d)); f.extend([((v,),{(0,):0}),((v,),{(1,):0})])
    return d,f


def audit():
    rows=[]; controls=0; packets=[]
    for seed in range(7100,7120):
        d,f=network(seed, 2+(seed%4)*2, 6); report=solve(d,f,tape_audit=True)
        require(verify(d,f,report)); r=report['result']
        base=ref.solve(d,f); h,w,kind=highs(d,f)
        require(r['optimum']==base['optimum']==h and r['assignments_evaluated']<=base['assignments_evaluated'])
        require(w is None if h is None else set(w)==set(d) and ref.score(f,w)==h)
        packets.append({'instance':gap.instance_record(d,f),'report':report,'external_witness':w})
        rows.append({'seed':seed,'family':'disconnected_hypergraphs','variables':len(d),'components':len(report['components']),'certified_order':report['globally_optimal_enumeration_order'],'optimum':h,'external_status':kind,'visits':r['assignments_evaluated'],'baseline_visits':base['assignments_evaluated'],'inequalities':sum(c['inequalities'] for c in report['components']),'tape_runs':sum(c['tape_transitions'] is not None for c in report['components']),'tape_transitions':sum(c['tape_transitions'] or 0 for c in report['components'])})
    for seed in range(7120,7124):
        d,f=network(seed,1,128,connected=True); report=solve(d,f); require(verify(d,f,report)); r=report['result']; base=ref.solve(d,f); h,w,kind=highs(d,f)
        require(r['optimum']==base['optimum']==h and not report['globally_optimal_enumeration_order'])
        require(w is None if h is None else set(w)==set(d) and ref.score(f,w)==h)
        packets.append({'instance':gap.instance_record(d,f),'report':report,'external_witness':w})
        rows.append({'seed':seed,'family':'long_chain','variables':len(d),'components':1,'certified_order':False,'optimum':h,'external_status':kind,'visits':r['assignments_evaluated'],'baseline_visits':base['assignments_evaluated'],'inequalities':0,'tape_runs':0,'tape_transitions':0})
    for d,f in [({},[]),({},[((),{})]),({},[((),{():-7})]),({'a':1,'b':2},[])]:
        r=solve(d,f); require(verify(d,f,r) and r['result']['optimum']==ref.brute(d,f)); controls+=1
    d,f=network(7199,2,6); require(solve(d,f,budget=1)['status']=='BUDGET_EXHAUSTED'); controls+=1
    r=solve(d,f); r['globally_optimal_enumeration_order']=False
    try: verify(d,f,r)
    except ValueError: controls+=1
    else: raise ValueError('accepted false certification flag')
    import scipy
    out={'rows':rows,'packets':packets,'controls':controls,'external_solver':'SciPy/HiGHS '+scipy.__version__,'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,up.__file__,cert.__file__,cert.synth.__file__,cert.synth.evo.__file__,up.curriculum.__file__,tape.__file__,__import__('mra_x_frontier').__file__)},'scope':'component-local exact planning; large connected components use heuristic planning; bounded synthetic comparisons, no runtime or memory superiority, no original RE-X or Lean certification'}
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({'cases':len(r['rows']),'certified_orders':sum(x['certified_order'] for x in r['rows']),'max_variables':max(x['variables'] for x in r['rows']),'controls':r['controls'],**{k:sum(x[k] for x in r['rows']) for k in ('components','visits','baseline_visits','inequalities','tape_runs','tape_transitions')}},indent=2))
