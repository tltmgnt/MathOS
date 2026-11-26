"""Matched synthesis/replay audit; repeated read scenarios are in-process."""
import argparse
import copy
import itertools
import json
import random
import statistics as st
import subprocess
import sys
import time
from pathlib import Path
import mra_x_boundproof as p
import mra_x_boundproof_generate as old
import mra_x_proofarbitrate as q
import mra_x_kernel as k
import mra_x_system_audit as v
import mra_x_indexed as idx
import mra_x_topology as ref
import mra_x_service as s
import mra_x_state as state
from mra_x_formal import SMT


def make(d,fs):
    inputs={f'{j:04}':f for j,f in enumerate(fs)}
    e=idx.Indexed(d,ref.min_fill(d,fs)); doc=s.certificate(e,e.update(inputs)['result'])
    value,_=v.oracle(d,fs); assert value!='SKIP' and value==doc['result']['optimum']
    expected=p.digest(dict(domains=d,factors=[state.pack(f) for f in fs]))
    assert k.check(doc,expected)['optimum']==value
    return doc,expected,value


def corpus():
    for name,domains,edits in v.corpus():
        d=dict(domains); fs={}
        for j,(es,ds) in enumerate(edits,1):
            v.inputs_after(d,fs,es,ds)
            yield f'{name}-{j:02}',*make(dict(d),[f for _,f in sorted(fs.items())])
    for i in range(72):
        rng=random.Random(42100+i); n=2+i%5; d={f'x{j}':rng.randint(1,3) for j in range(n)}; vs=list(d); fs=[]
        for _ in range(1+i%7):
            scope=tuple(rng.sample(vs,rng.randint(1,min(n,4))))
            fs.append((scope,{row:rng.randint(-15,15) for row in itertools.product(*(range(d[x]) for x in scope)) if rng.random()<.65}))
        if i%5==0: fs.append(fs[0])
        yield f'random-{i:02}',*make(d,fs)
    for i in range(24):
        rng=random.Random(42900+i); n=7+i%6; vs=[f'x{j:02}' for j in range(n)]; d=dict.fromkeys(vs,2); fs=[]
        for j in range(n-1):
            # Full tables, conflicting local minima, chain/cycle plus unary penalties.
            fs.append(((vs[j],vs[j+1]),{row:rng.randint(-7,9) for row in itertools.product(range(2),repeat=2)}))
        if i%2: fs.append(((vs[-1],vs[0]),{row:rng.randint(-7,9) for row in itertools.product(range(2),repeat=2)}))
        for x in vs: fs.append(((x,),{(0,):rng.randint(-4,4),(1,):rng.randint(-4,4)}))
        yield f'conflict-{i:02}',*make(d,fs)


def timed(mode,doc,expected,reads):
    start=time.perf_counter_ns(); stats={}; kind='partition'; reason='direct'
    if mode=='elimination': proof=doc; kind='elimination'; receipt=k.check(proof,expected)
    elif mode=='original': proof=old.generate(doc); receipt=p.check(proof,expected)
    elif mode in ('cached','adaptive'):
        search=q.Search(nodes=p.MAX_NODES,work=p.MAX_ROWS,entries=100000)
        proof=q.generate(doc,search,adaptive=mode=='adaptive'); receipt=p.check(proof,expected); stats=search.stats()
    elif mode=='selector':
        result=q.select(doc,expected,reads=reads); proof,receipt,kind,reason,stats=(result[x] for x in ('proof','receipt','kind','reason','search'))
    else: raise AssertionError(mode)
    first=time.perf_counter_ns()-start; checker=p.check if kind=='partition' else k.check
    for _ in range(reads-1): assert checker(proof,expected)==receipt
    total=time.perf_counter_ns()-start
    return dict(kind=kind,reason=reason,bytes=len(p.canonical(proof)),receipt=receipt,search=stats),dict(first_ns=first,total_ns=total)


def controls(root):
    d={'x':2,'y':2}; fs=[(('x',),{(0,):0,(1,):5}),(('x','y'),{(0,0):5,(0,1):5,(1,0):0,(1,1):0})]; doc,expected,_=make(d,fs); done=[]
    def reject(name,fn):
        try: fn()
        except (ValueError,TypeError,KeyError): done.append(name)
        else: raise AssertionError(name)
    for name,kw in [('node_budget',dict(nodes=1)),('work_budget',dict(work=1))]:
        r=q.select(doc,expected,**kw); assert r['kind']=='elimination' and r['reason']=='search_refused' and r['receipt']['optimum']==5; done.append(name)
    r=q.select(doc,expected,reads=1); assert r['kind']=='elimination' and r['search']['work']==0; done.append('single_read')
    r=q.select(doc,expected,entries=1); assert r['receipt']['optimum']==5 and r['search']['cache_entries']<=1; done.append('bounded_cache')
    reject('wrong_anchor',lambda:q.select(doc,'0'*64)); reject('bool_reads',lambda:q.select(doc,expected,reads=True)); reject('zero_work',lambda:q.select(doc,expected,work=0))
    bad=copy.deepcopy(doc); bad['result']['optimum']=4; reject('false_optimum',lambda:q.select(bad,expected))
    bad=copy.deepcopy(doc); bad['result']['witness']['x']=False; reject('bool_witness',lambda:q.select(bad,expected))
    bad=copy.deepcopy(doc); bad['result'].update(optimum=None,witness=None); reject('false_infeasible',lambda:q.select(bad,expected))
    search=q.Search(); proof=q.generate(doc,search); reject('search_reuse',lambda:q.generate(doc,search))
    bad=copy.deepcopy(proof); bad['proofs'][0][1][1].pop(); reject('missing_branch',lambda:p.check(bad,expected))
    # A partition certifies the objective, NOT the integrity of an elimination trace.
    bad=copy.deepcopy(doc); bad['result']['trace'].clear(); r=q.select(bad,expected); assert r['kind']=='partition' and r['receipt']['optimum']==5; done.append('claim_not_trace')
    path=root/'proof.json'; path.write_bytes(p.canonical(proof)); proc=subprocess.run([sys.executable,'-I','-S',str(Path(p.__file__).resolve()),str(path),'--expect-problem',expected],capture_output=True,check=True,timeout=20); assert json.loads(proc.stdout)==p.check(proof,expected); done.append('standalone')
    return done


def symbolic():
    smt=SMT(); cases=[('sorted_first_match','''(declare-const i Int)(declare-const j Int)(declare-const a Int)(declare-const b Int)
(assert (<= i j))(assert (=> (<= i j) (<= a b)))(assert (> a b))''','unsat'),('cache_compatible_rows','''(declare-sort R 0)(declare-fun A (R) Bool)(declare-fun B (R) Bool)(declare-const r R)
(assert (forall ((x R)) (= (A x) (B x))))(assert (A r))(assert (not (B r)))''','unsat'),('unsorted_countermodel','''(declare-const a Int)(declare-const b Int)(assert (> a b))''','sat')]
    return smt.version,[dict(name=name,result=smt.check(formula,expected),formula_sha256=p.digest(formula)) for name,formula,expected in cases]


def audit(root):
    root.mkdir(); rows=[]; timings=[]; modes=['elimination','original','cached','adaptive','selector']
    for i,(name,doc,expected,value) in enumerate(corpus()):
        data={}; ns={mode:[] for mode in modes}
        for repeat in range(3):
            labels=list(modes); random.Random(42000+i*7+repeat).shuffle(labels)
            for mode in labels:
                result,t=timed(mode,doc,expected,4)
                assert result['receipt']['optimum']==value and result['receipt']['problem_sha256']==expected
                if mode in data: assert data[mode]==result
                data[mode]=result; ns[mode].append(t)
        assert data['original']['receipt']==data['cached']['receipt']
        rows.append(dict(name=name,optimum=value,methods=data)); timings.append(dict(name=name,ns=ns))
    version,obligations=symbolic()
    totals={mode:{key:sum(st.median(t['ns'][mode][i][key] for i in range(3)) for t in timings) for key in ('first_ns','total_ns')} for mode in modes}
    out=dict(rows=rows,controls=controls(root),timings=timings,totals_ns=totals,z3=version,symbolic=obligations,scope='three randomized-order in-process repeats per state; four checks including first accepted proof; existing elimination certificate available; excludes solving, IO and transaction costs; search limits count queries and examined rows, not sorting, parsing, votes, checker work or elapsed time')
    out['evidence_sha256']=p.digest(out); return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--directory',type=Path,required=True); args=ap.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(p.canonical(out)); print(json.dumps(dict(states=len(out['rows']),controls=len(out['controls']),totals_ns=out['totals_ns']),indent=2))
