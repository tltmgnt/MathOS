"""Phase XLI: original-factor proofs, symbolic obligations, and falsification audit."""
import argparse
import copy
import itertools
import json
import random
import subprocess
import sys
import time
from pathlib import Path
import mra_x_boundproof as p
import mra_x_boundproof_generate as g
import mra_x_system as u
import mra_x_system_audit as v
import mra_x_indexed as idx
import mra_x_service as s
import mra_x_state as state
import mra_x_kernel as k
import mra_x_topology as ref
from mra_x_formal import SMT


def obligations():
    # Mathematical rules, not a refinement proof of the Python code.
    yield 'sum_lower_bounds', '''(declare-const a Int)(declare-const b Int)(declare-const x Int)(declare-const y Int)
(assert (<= a x))(assert (<= b y))(assert (> (+ a b) (+ x y)))''', 'unsat'
    yield 'compatible_row_bound', '''(declare-sort Row 0)(declare-fun compatible (Row) Bool)(declare-fun cost (Row) Int)(declare-const l Int)(declare-const w Row)
(assert (forall ((r Row)) (=> (compatible r) (<= l (cost r)))))
(assert (compatible w))(assert (> l (cost w)))''','unsat'
    yield 'dead_leaf', '''(declare-sort Row 0)(declare-fun compatible (Row) Bool)(declare-const w Row)
(assert (forall ((r Row)) (not (compatible r))))(assert (compatible w))''','unsat'
    yield 'complete_partition', '''(declare-sort A 0)(declare-fun val (A) Int)(declare-fun feasible (A) Bool)(declare-fun cost (A) Int)(declare-const n Int)(declare-const b Int)(declare-const w A)
(assert (forall ((a A)) (=> (feasible a) (and (<= 0 (val a)) (< (val a) n)))))
(assert (forall ((i Int)(a A)) (=> (and (<= 0 i) (< i n) (feasible a) (= (val a) i)) (<= b (cost a)))))
(assert (feasible w))(assert (< (cost w) b))''','unsat'
    yield 'witness_and_lower_bound', '''(declare-sort A 0)(declare-fun feasible (A) Bool)(declare-fun cost (A) Int)(declare-const w A)(declare-const b Int)(declare-const a A)
(assert (feasible w))(assert (= (cost w) b))(assert (forall ((x A)) (=> (feasible x) (<= b (cost x)))))
(assert (feasible a))(assert (< (cost a) (cost w)))''','unsat'
    yield 'infeasible_component', '''(declare-sort A 0)(declare-sort C 0)(declare-fun restrict (A) C)(declare-fun global (A) Bool)(declare-fun local (C) Bool)(declare-const w A)
(assert (forall ((a A)) (=> (global a) (local (restrict a)))))
(assert (forall ((c C)) (not (local c))))(assert (global w))''','unsat'
    yield 'missing_branch_countermodel', '''(declare-const v Int)(declare-const cost Int)(assert (and (<= 0 v) (< v 2)))(assert (=> (= v 0) (>= cost 0)))(assert (< cost 0))''','sat'
    yield 'invalid_bound_countermodel', '''(declare-const a Int)(declare-const x Int)(assert (> a x))''','sat'


def audit(root):
    root.mkdir(); proofdir=root/'proofs'; proofdir.mkdir(); rows=[]; timing=[]
    def check(doc, expected, label, value, *, save=False):
        assert doc['result']['optimum']==value
        t=time.perf_counter_ns(); proof=g.generate(doc); built=time.perf_counter_ns()-t
        t=time.perf_counter_ns(); receipt=p.check(proof,expected); replay=time.perf_counter_ns()-t
        t=time.perf_counter_ns(); baseline=k.check(doc,expected); old=time.perf_counter_ns()-t
        assert receipt['optimum']==baseline['optimum']==value
        raw=p.canonical(proof); row=dict(name=label,**receipt,proof_bytes=len(raw),elimination_bytes=len(p.canonical(doc)),elimination_visits=baseline['visits'])
        if save:
            path=proofdir/(label+'.json'); path.write_bytes(raw)
            child=subprocess.run([sys.executable,'-I','-S',str(Path(p.__file__).resolve()),str(path),'--expect-problem',expected],check=True,capture_output=True,timeout=20)
            assert json.loads(child.stdout)==receipt
        rows.append(row); timing.append(dict(name=label,generate_ns=built,partition_check_ns=replay,elimination_check_ns=old))
    for name,domains,edits in v.corpus():
        system=u.System(root/(name+'.sqlite'),domains,profile='performance'); d=dict(domains); fs={}
        for j,(es,ds) in enumerate(edits,1):
            receipt=system.apply(es,ds,expected_version=j-1)['receipt']; v.inputs_after(d,fs,es,ds)
            value,_=v.oracle(d,list(fs.values())); assert value!='SKIP'
            expected=p.digest(dict(domains=d,factors=[state.pack(f) for _,f in sorted(fs.items())])); assert receipt['problem_sha256']==expected
            check(system.certificate(j),expected,f'{name}-{j:02}',value,save=j==18)
    # Fresh seed set: randomly ordered high-arity scopes, sparse tables, negative costs,
    # repeated factors and nontrivial infeasibility without an empty constant.
    for i in range(72):
        rng=random.Random(41100+i); n=2+i%5; d={f'x{j}':rng.randint(1,3) for j in range(n)}; vs=list(d); fs=[]
        for _ in range(1+i%7):
            scope=tuple(rng.sample(vs,rng.randint(1,min(4,n))))
            tab={row:rng.randint(-15,15) for row in itertools.product(*(range(d[x]) for x in scope)) if rng.random()<.65}
            fs.append((scope,tab))
        if i%5==0: fs.append(fs[0])
        if i%6==0: fs.extend([((vs[0],),{(0,):0}),((vs[0],),{(1,):0} if d[vs[0]]>1 else {})])
        e=idx.Indexed(d,ref.min_fill(d,fs)); result=e.update({f'{j:03}':f for j,f in enumerate(fs)})['result']; doc=s.certificate(e,result)
        value,_=v.oracle(d,fs); assert value!='SKIP'
        check(doc,p.digest(dict(domains=d,factors=[state.pack(f) for f in fs])),f'random-{i:02}',value,save=i in (0,1,2,3))
    # Minimal two-variable case where separate factor minima are not jointly attainable.
    d={'x':2,'y':2}; fs=[(('x',),{(0,):0,(1,):5}),(('x','y'),{(0,0):5,(0,1):5,(1,0):0,(1,1):0})]; e=idx.Indexed(d,['x','y']); doc=s.certificate(e,e.update({'0':fs[0],'1':fs[1]})['result']); proof=g.generate(doc); assert proof['proofs'][0][1][0]=='x'
    controls=[]
    def reject(name,change):
        bad=copy.deepcopy(proof); change(bad)
        try: p.check(bad,p.digest(proof['problem']))
        except (ValueError,KeyError,TypeError): controls.append(name)
        else: raise AssertionError(name)
    reject('missing_branch',lambda q:q['proofs'][0][1][1].pop())
    reject('false_bound',lambda q:q['proofs'][0].__setitem__(1,1))
    reject('false_dead',lambda q:q['proofs'][0].__setitem__(1,0))
    reject('repeat_variable',lambda q:q['proofs'][0][1][1].__setitem__(0,['x',[1,1]]))
    reject('unknown_variable',lambda q:q['proofs'][0][1].__setitem__(0,'z'))
    reject('boolean_leaf',lambda q:q['proofs'][0][1][1].__setitem__(0,True))
    reject('wrong_optimum',lambda q:q.__setitem__('optimum',4))
    reject('boolean_witness',lambda q:q['witness'].__setitem__('x',False))
    reject('missing_component',lambda q:q['proofs'].clear())
    reject('wrong_component',lambda q:q['proofs'][0].__setitem__(0,1))
    reject('forged_infeasibility',lambda q:q.update(optimum=None,witness=None))
    reject('wrong_problem_anchor',lambda q:q['problem']['factors'][0][1][0].__setitem__(1,3))
    # An actual infeasible component, with all individual original factors nonempty.
    d={'x':2}; fs=[(('x',),{(0,):0}),(('x',),{(1,):0})]; e=idx.Indexed(d,['x']); doc=s.certificate(e,e.update({'0':fs[0],'1':fs[1]})['result']); unsat=g.generate(doc); assert p.check(unsat)['optimum'] is None
    try: bad=copy.deepcopy(unsat); bad['proofs'][0][1]=1; p.check(bad)
    except ValueError: controls.append('infeasible_false_bound')
    else: raise AssertionError('infeasible_false_bound')
    try: p.unique([('a',1),('a',2)])
    except ValueError: controls.append('duplicate_json_key')
    else: raise AssertionError('duplicate_json_key')
    smt=SMT(); symbolic=[dict(name=name,result=smt.check(script,expected),formula_sha256=p.digest(script)) for name,script,expected in obligations()]
    out=dict(rows=rows,controls=controls,symbolic=symbolic,z3_version=smt.version,standalone=12,timing=timing,scope='original-factor partition proof certificates; same local environment; symbolic rules checked under explicit axioms, no program refinement proof; timing is one in-process check per state, not matched end-to-end performance')
    out['evidence_sha256']=p.digest(out); return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--directory',type=Path,required=True); args=ap.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(p.canonical(out)); print(json.dumps(dict(states=len(out['rows']),controls=len(out['controls']),symbolic=out['symbolic'],nodes=sum(x['nodes'] for x in out['rows']),rows=sum(x['row_checks'] for x in out['rows'])),indent=2))
