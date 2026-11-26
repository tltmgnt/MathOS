"""Phase V: exact structural order synthesis and review-only policy patches."""
import argparse
import functools
import hashlib
import itertools
import json
import math
import time
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_upgrade as up
import mra_x_evolution as evo


def exact_order(domains, factors):
    """Subset DP: minimum enumeration cost over ALL permutations, n <= 10."""
    ref.validate(domains, factors)
    vs=sorted(domains); n=len(vs)
    if n>10: raise ValueError('exact planner limited to ten variables')
    idx={v:i for i,v in enumerate(vs)}; adj=[0]*n; ds=[domains[v] for v in vs]
    for scope,_ in factors:
        for a,b in itertools.combinations(scope,2):
            i,j=idx[a],idx[b]; adj[i]|=1<<j; adj[j]|=1<<i
    full=(1<<n)-1; edges=0
    def bits(mask):
        while mask:
            bit=mask & -mask; yield bit.bit_length()-1; mask^=bit
    def boundary(mask,i):
        reached=adj[i]; pending=reached & mask; seen=0
        while pending:
            j=next(bits(pending)); seen|=1<<j; reached|=adj[j]; pending=reached & mask & ~seen
        return reached & (full ^ mask) & ~(1<<i)
    @functools.lru_cache(None)
    def dp(mask):
        nonlocal edges
        if mask==full: return 0,()
        best=None
        for i in bits(full^mask):
            edges+=1; cost=ds[i]*math.prod(ds[j] for j in bits(boundary(mask,i)))
            tail,order=dp(mask|(1<<i)); candidate=(cost+tail,(vs[i],)+order)
            if best is None or candidate<best: best=candidate
        return best
    cost,order=dp(0)
    if up.predict(domains,factors,order)[0]!=cost: raise ValueError('planner cost mismatch')
    return list(order),cost,dp.cache_info().currsize,edges


def validate_policy(p):
    # Restricted data DSL: no imports, arbitrary expressions, paths or executable text.
    if type(p) is not dict or set(p)!={'exact_max_variables','fallback','objective'}: raise ValueError('invalid policy keys')
    if type(p['exact_max_variables']) is not int or p['exact_max_variables'] not in (0,4,6,8,10): raise ValueError('invalid threshold')
    if p['fallback']!='beam16_or_predictor' or p['objective']!='enumerations': raise ValueError('unknown operation')
    return p.copy()


def baseline(d,f):
    _,b=up.choose(d,f); order,work=evo.beam(d,f,16)
    return min((b,order),key=lambda o:up.predict(d,f,o)),work


def apply(p,d,f):
    p=validate_policy(p)
    if len(d)<=p['exact_max_variables']:
        order,cost,states,edges=exact_order(d,f); return order,edges
    return baseline(d,f)


def corpus(seed):
    for i,name in enumerate(gap.FAMILIES):
        for t in range(4):
            d,variants=gap.build(name,seed*10000+100*i+t,t)
            for edit,f in variants: yield name,d,f,edit


def evaluate(p,seed):
    rows=[]
    for name,d,f,edit in corpus(seed):
        oracle=gap.oracle(d,f)
        start=time.perf_counter_ns(); order,work=apply(p,d,f); result=ref.solve(d,f,order); candidate_ns=time.perf_counter_ns()-start
        start=time.perf_counter_ns(); b,bwork=baseline(d,f); base=ref.solve(d,f,b); base_ns=time.perf_counter_ns()-start
        a,z=result['assignments_evaluated'],base['assignments_evaluated']
        ok=gap.check_result(d,f,oracle,result) and gap.check_result(d,f,oracle,base) and a<=z
        row={'family':name,'edit':edit,'instance_sha256':gap.digest(gap.instance_record(d,f)), 'candidate':a,'baseline':z,'work':work,'baseline_work':bwork,'ok':ok,'candidate_ns':candidate_ns,'baseline_ns':base_ns}
        if not ok: row['counterexample']=gap.instance_record(d,f)
        rows.append(row)
    return {'policy':p,'seed':seed,'rows':rows,'failures':sum(not r['ok'] for r in rows),**{k:sum(r[k] for r in rows) for k in ('candidate','baseline','work','baseline_work','candidate_ns','baseline_ns')}}


def audit():
    # Independent order oracle: every permutation of every labelled simple graph on four vertices,
    # with every binary/ternary domain-size pattern. Empty factor tables suffice for structural costs.
    count=permutations=0
    vs=list('abcd'); pairs=list(itertools.combinations(vs,2))
    for mask in range(64):
        f=[(s,{}) for i,s in enumerate(pairs) if mask & (1<<i)]
        for sizes in itertools.product((2,3),repeat=4):
            d=dict(zip(vs,sizes)); o,c,states,edges=exact_order(d,f)
            best=min(up.predict(d,f,p)[0] for p in itertools.permutations(vs))
            if c!=best or states!=16 or edges!=32: raise ValueError('exhaustive order check failed')
            count+=1; permutations+=24
    # Adversarial controls for policy parser.
    base={'exact_max_variables':0,'fallback':'beam16_or_predictor','objective':'enumerations'}
    bad=[{**base,'exec':'import os'},{**base,'exact_max_variables':True},{**base,'exact_max_variables':11},{**base,'fallback':'eval'},{**base,'objective':'runtime'}]
    for p in bad:
        try: validate_policy(p)
        except ValueError: pass
        else: raise ValueError('invalid policy accepted')
    training=[evaluate({**base,'exact_max_variables':n},501) for n in (0,4,6,8,10)]
    good=[r for r in training if r['failures']==0]
    if not good: raise ValueError('no valid policy')
    selected=min(good,key=lambda r:(r['candidate'],r['work'],r['policy']['exact_max_variables']))['policy']
    held=[evaluate(selected,s) for s in (502,503)]
    if any(r['failures'] for r in held): decision='REJECTED'
    elif sum(r['candidate'] for r in held)>=sum(r['baseline'] for r in held): decision='NO_GAIN'
    else: decision='REVIEW_CANDIDATE'
    # Diagnostic counterexample to beam optimality (not used to tune or select the policy).
    d=dict(zip('012345678',(3,2,3,3,3,2,3,3,3)))
    scopes=[tuple(s) for s in ('03','06','08','12','13','14','15','18','24','28','34','36','56','68','78')]
    fs=[(s,{a:sum(a)-2 for a in ref.assignments(d,s)}) for s in scopes]
    o,c,states,edges=exact_order(d,fs); b,_=baseline(d,fs)
    r=ref.solve(d,fs,o); z=ref.solve(d,fs,b); expected=gap.oracle(d,fs)
    if not (gap.check_result(d,fs,expected,r) and gap.check_result(d,fs,expected,z) and c==288 and z['assignments_evaluated']==290):
        raise ValueError('beam counterexample replay failed')
    challenge={'instance':gap.instance_record(d,fs),'exact_order':o,'beam_order':b,'exact_visits':c,'beam_visits':z['assignments_evaluated'],'optimum':expected,'dp_states':states,'dp_edges':edges}
    # Review-only data patch, not an executable source change or authorization.
    patch={'base_sha256':gap.digest(base),'operation':'replace','path':'/exact_max_variables','value':selected['exact_max_variables'],'decision':decision,'authorizes_merge':False}
    out={'beam_counterexample':challenge,'exhaustive_graph_domain_checks':count,'permutation_checks':permutations,'invalid_policy_controls':len(bad),'training':training,'heldout':held,'patch':patch,'source_sha256':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (__file__,ref.__file__,gap.__file__,up.__file__,evo.__file__)},'scope':'bounded synthetic tests; timings include planner and solver, exclude oracle; single sequential pass, not controlled performance certification; policy data only, no arbitrary code execution or theorem promotion'}
    out['evidence_sha256']=gap.digest(out)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps({'patch':r['patch'],'exhaustive_graph_domain_checks':r['exhaustive_graph_domain_checks'],'permutation_checks':r['permutation_checks'],'training':[{k:v for k,v in t.items() if k!='rows'} for t in r['training']],'heldout':[{k:v for k,v in t.items() if k!='rows'} for t in r['heldout']]},indent=2))
