"""Phase XXI: symbolic SMT obligations and independent finite-domain certificates."""
import argparse
import ctypes as ct
import ctypes.util
import hashlib
import json
from pathlib import Path
import mra_x_topology as ref
import mra_x_gap_agent as gap
import mra_x_indexed as idx
import mra_x_arbitrate as arb


def require(ok):
    if not ok: raise ValueError('formal audit failed')


class SMT:
    """Trusted Z3 shared library; every query gets a fresh context and timeout."""
    def __init__(self):
        name=ctypes.util.find_library('z3')
        if not name: raise RuntimeError('install the system Z3 shared library')
        self.z=ct.CDLL(name)
        for fn,args,result in [('Z3_mk_config',[],ct.c_void_p),('Z3_del_config',[ct.c_void_p],None),('Z3_mk_context',[ct.c_void_p],ct.c_void_p),('Z3_del_context',[ct.c_void_p],None),('Z3_eval_smtlib2_string',[ct.c_void_p,ct.c_char_p],ct.c_char_p),('Z3_get_full_version',[],ct.c_char_p)]:
            f=getattr(self.z,fn); f.argtypes=args; f.restype=result
        self.version=self.z.Z3_get_full_version().decode()

    def check(self,script,expected):
        cfg=self.z.Z3_mk_config(); ctx=self.z.Z3_mk_context(cfg); self.z.Z3_del_config(cfg)
        try:
            answer=self.z.Z3_eval_smtlib2_string(ctx,('(set-option :timeout 5000)\n'+script+'\n(check-sat)').encode()).decode().strip()
        finally: self.z.Z3_del_context(ctx)
        if answer not in ('sat','unsat'): raise RuntimeError(f'inconclusive SMT result: {answer}')
        if answer!=expected: raise ValueError(f'expected {expected}, got {answer}')
        return answer


REL='''
(declare-sort S 0)
(declare-sort X 0)
(declare-fun C (S X Int) Bool)
(declare-fun P (S Int) Bool)
(declare-fun ok (S) Bool)
(declare-fun tail (S) Int)
(declare-const m Int)
(define-fun O ((z Int)) Bool (exists ((s S) (x X) (c Int)) (and (ok s) (C s x c) (= z (+ (tail s) c)))))
(define-fun R ((z Int)) Bool (exists ((s S) (p Int)) (and (ok s) (P s p) (= z (+ (tail s) p)))))
'''
ATTAIN='(assert (forall ((s S) (p Int)) (=> (P s p) (exists ((x X)) (C s x p)))))\n'
DOM='(assert (forall ((s S) (x X) (c Int)) (=> (C s x c) (exists ((p Int)) (and (P s p) (<= p c))))))\n'


def obligations():
    # Split the global minimum equivalence into attainment and lower-bound obligations.
    olow='(assert (forall ((s S)(x X)(c Int)) (=> (and (ok s)(C s x c)) (<= m (+ (tail s) c)))))\n'
    rlow='(assert (forall ((s S)(p Int)) (=> (and (ok s)(P s p)) (<= m (+ (tail s) p)))))\n'
    yield 'original_min_attainment',REL+ATTAIN+DOM+olow+'(assert (O m))(assert (not (R m)))','unsat'
    yield 'original_min_lower_bound',REL+ATTAIN+olow+'(declare-const s S)(declare-const p Int)(assert (and (ok s)(P s p)(> m (+ (tail s) p))))','unsat'
    yield 'projected_min_attainment',REL+ATTAIN+'(assert (R m))(assert (not (O m)))','unsat'
    yield 'projected_min_lower_bound',REL+DOM+rlow+'(declare-const s S)(declare-const x X)(declare-const c Int)(assert (and (ok s)(C s x c)(> m (+ (tail s) c))))','unsat'
    yield 'original_to_projected_feasibility',REL+DOM+'(declare-const s S)(declare-const x X)(declare-const c Int)(assert (and (ok s)(C s x c)))(assert (not (exists ((s S)(p Int)) (and (ok s)(P s p)))))','unsat'
    yield 'projected_to_original_feasibility',REL+ATTAIN+'(declare-const s S)(declare-const p Int)(assert (and (ok s)(P s p)))(assert (not (exists ((s S)(x X)(c Int)) (and (ok s)(C s x c)))))','unsat'
    yield 'witness_lift',REL+ATTAIN+'''(declare-const s S)(declare-const p Int)
(assert (P s p))(assert (not (exists ((x X)) (C s x p))))''','unsat'
    # Arbitrary integer costs and ascending tie-breaking index.
    fold='''(declare-const have Bool)(declare-const valid Bool)(declare-const old Int)(declare-const x Int)
(declare-const arg Int)(declare-const i Int)(declare-const earlier Int)(declare-const ec Int)(declare-const ef Bool)
(assert (=> have (< arg i)))(assert (< earlier i))
(assert (=> ef (and have (<= old ec) (=> (= old ec) (<= arg earlier)))))
(define-fun replace () Bool (and valid (or (not have) (< x old))))
(define-fun found () Bool (or have valid))
(define-fun best () Int (ite replace x old))
(define-fun witness () Int (ite replace i arg))\n'''
    for name,goal in [('fold_prior_lower_bound','(=> ef (and found (<= best ec) (=> (= best ec) (<= witness earlier))))'),('fold_candidate_lower_bound','(=> valid (and found (<= best x) (=> (= best x) (<= witness i))))'),('fold_attainment','(=> found (or (and have (= best old) (= witness arg)) (and valid (= best x) (= witness i))))'),('fold_empty_prefix','(=> (not have) (and (= found valid) (=> valid (and (= best x) (= witness i)))))')]:
        yield name,fold+'(assert (not '+goal+'))','unsat'
    cache='''(declare-sort S 0)(declare-fun A (S Int Int) Bool)(declare-fun B (S Int Int) Bool)
(declare-const s S)(declare-const x Int)(declare-const c Int)
(assert (forall ((s S)(x Int)(c Int)) (= (A s x c) (B s x c))))
(define-fun bestA () Bool (and (A s x c) (forall ((y Int)(k Int)) (=> (A s y k) (or (< c k) (and (= c k) (<= x y)))))))
(define-fun bestB () Bool (and (B s x c) (forall ((y Int)(k Int)) (=> (B s y k) (or (< c k) (and (= c k) (<= x y)))))))\n'''
    yield 'cache_argmin_equivalence',cache+'(assert (not (= bestA bestB)))','unsat'
    routing='''(declare-const consumer Int)(declare-const oldDest Int)(declare-const newDest Int)
(declare-const oldValue Int)(declare-const newValue Int)(declare-const oldPresent Bool)(declare-const newPresent Bool)
(define-fun op () Bool (and oldPresent (= oldDest consumer)))
(define-fun np () Bool (and newPresent (= newDest consumer)))
(define-fun changed () Bool (or (not (= oldPresent newPresent)) (and oldPresent newPresent (or (not (= oldDest newDest)) (not (= oldValue newValue))))))
(define-fun dirty () Bool (and changed (or op np)))\n'''
    yield 'clean_consumer_input_unchanged',routing+'(assert (not dirty))(assert (or (not (= op np)) (and op np (not (= oldValue newValue)))))','unsat'
    # An induction step for a path lower bound, independent of path length.
    yield 'order_potential_induction_step','''(declare-const p Int)(declare-const q Int)(declare-const edge Int)(declare-const suffix Int)
(assert (<= p (+ edge q)))(assert (<= q suffix))(assert (> p (+ edge suffix)))''','unsat'
    # Deliberately weakened assumptions must admit countermodels, not prove vacuously.
    yield 'missing_attainment_countermodel',REL+DOM+'(assert (exists ((s S)) (and (ok s) (P s 0))))(assert (forall ((s S)(x X)(c Int)) (not (C s x c))))','sat'
    yield 'missing_dominance_countermodel',REL+ATTAIN+'(assert (exists ((s S)(x X)) (and (ok s) (C s x 0))))(assert (forall ((s S)(p Int)) (not (P s p))))','sat'
    yield 'missing_invalidation_countermodel',routing+'(assert op)(assert np)(assert (not (= oldValue newValue)))','sat'


def integer(x):
    require(type(x) is int)
    return str(x) if x>=0 else f'(- {-x})'


def conjunction(xs):
    return '(and '+' '.join(xs)+')' if xs else 'true'


def encode(d,fs):
    # Independent direct extensional relation; does not use elimination or backpointers.
    ref.validate(d,fs); vs={v:f'v{i}' for i,v in enumerate(sorted(d))}; lines=[]
    for v,x in vs.items(): lines.extend([f'(declare-const {x} Int)',f'(assert (and (<= 0 {x}) (< {x} {d[v]})))'])
    for i,(s,tab) in enumerate(fs):
        cost=f'c{i}'; lines.append(f'(declare-const {cost} Int)'); rows=[]
        for a,c in sorted(tab.items()): rows.append(conjunction([f'(= {vs[v]} {integer(x)})' for v,x in zip(s,a)]+[f'(= {cost} {integer(c)})']))
        lines.append('(assert '+('(or '+' '.join(rows)+')' if rows else 'false')+')')
    total='(+ 0 '+' '.join(f'c{i}' for i in range(len(fs)))+')' if fs else '0'
    lines.append(f'(define-fun total () Int {total})')
    return '\n'.join(lines)+'\n',vs


def verify(smt,d,fs,r):
    formula,vs=encode(d,fs); optimum=r['optimum']; witness=r['witness']
    if optimum is None:
        require(witness is None); smt.check(formula,'unsat'); return 1
    require(type(optimum) is int and isinstance(witness,dict) and set(witness)==set(d))
    require(all(type(witness[v]) is int and 0<=witness[v]<d[v] for v in d))
    value=integer(optimum)
    smt.check(formula+'(assert (= total '+value+'))\n'+'\n'.join(f'(assert (= {vs[v]} {integer(witness[v])}))' for v in d),'sat')
    smt.check(formula+'(assert (< total '+value+'))','unsat'); return 2


def audit():
    smt=SMT(); symbolic=[]
    for name,script,expected in obligations():
        symbolic.append(dict(name=name,result=smt.check(script,expected),sha256=hashlib.sha256(script.encode()).hexdigest()))
    rows=[]; checks=0; controls=0
    for i,kind in enumerate(gap.FAMILIES):
        for j in range(4):
            d,variants=gap.build(kind,21100+i*100+j,j); fs=variants[0][1]; order=ref.min_fill(d,fs); e=idx.Indexed(d,order)
            inputs={str(k):f for k,f in enumerate(fs)}; result=e.update(inputs)['result']
            q=verify(smt,d,fs,result); checks+=q; require(result==ref.solve(d,fs,order))
            rows.append(dict(family=kind,stage='indexed',feasible=result['optimum'] is not None,queries=q,optimum=result['optimum']))
            # Domain expansion with reordered migration and exact cache compatibility.
            nd=dict(d); nd[order[0]]+=1; fresh=ref.min_fill(nd,fs)
            upper,full,hits=arb.estimate(e,nd,inputs,fresh); new,x=arb.transfer(e,nd,inputs,fresh)
            require(x['actual']<=upper and x['result']['assignments_evaluated']==full and x['result']==ref.solve(nd,fs,fresh))
            q=verify(smt,nd,fs,x['result']); checks+=q
            rows.append(dict(family=kind,stage='migration',feasible=x['result']['optimum'] is not None,queries=q,optimum=x['result']['optimum']))
            # Online factor insertion and removal exercise the dirty-bucket scheduler.
            edit=( (fresh[-1],), {} )
            for stage,es in (('insert_forbidden',{'test':edit}),('remove_forbidden',{'test':None})):
                r=new.update(es)['result']; active=list(new.inputs.values())
                require(r==ref.solve(nd,active,fresh)); q=verify(smt,nd,active,r); checks+=q
                rows.append(dict(family=kind,stage=stage,feasible=r['optimum'] is not None,queries=q,optimum=r['optimum']))
    for d,fs in (({},[]),({},[((),{})]),({'a':1},[])):
        r=ref.solve(d,fs); q=verify(smt,d,fs,r); checks+=q; rows.append(dict(family='boundary',stage='reference',feasible=r['optimum'] is not None,queries=q,optimum=r['optimum']))
    d={'a':2}; fs=[(('a',),{(0,):-2,(1,):3})]
    for bad in (dict(optimum=3,witness={'a':1}),dict(optimum=-3,witness={'a':0}),dict(optimum=None,witness=None),dict(optimum=-2,witness={'a':1}),dict(optimum=-2,witness={'a':False})):
        try: verify(smt,d,fs,bad)
        except ValueError: controls+=1
        else: raise ValueError('invalid certificate accepted')
    out=dict(z3_version=smt.version,symbolic=symbolic,rows=rows,queries=checks,controls=controls,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='SMT-checked mathematical lemmas under explicit axioms and independent instance certificates; trusted Z3, no exported proof objects or Lean kernel proof; not end-to-end program or physical RE-X verification')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(symbolic=r['symbolic'],cases=len(r['rows']),queries=r['queries'],controls=r['controls'],feasible=sum(x['feasible'] for x in r['rows']),z3=r['z3_version']),indent=2))
