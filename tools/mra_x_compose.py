"""Phase XXII: compositional SMT certificates with exact incremental reuse."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import mra_x_formal as formal
import mra_x_gap_agent as gap
import mra_x_topology as ref
import mra_x_indexed as idx
import mra_x_arbitrate as arb
import mra_x_separator as sep

require=formal.require


def signature(d,v,bucket,message,rows):
    scope={v}|{u for s,_ in bucket for u in s}
    return (tuple(sorted((u,d[u]) for u in scope)),
            tuple(sorted((s,tuple(sorted(tab.items()))) for s,tab in bucket)),
            (message[0],tuple(sorted(message[1].items()))),
            tuple((tuple(row),x) for row,x in rows))


def value(fs,a):
    costs=[tab.get(tuple(a[v] for v in s)) for s,tab in fs]
    return None if None in costs else sum(costs)


class Checker:
    """Trusted in-process receipts only. A failed check never updates receipts."""
    def __init__(self,smt): self.smt=smt; self.receipts={}

    def verify(self,d,fs,r,messages):
        ref.validate(d,fs); order=r['order']; trace=r['trace']
        require(len(order)==len(d)==len(trace)==len(messages) and set(order)==set(d))
        active=list(fs); receipts={}; queries=hits=visits=width=attainment=0; back=[]
        for i,v in enumerate(order):
            bucket=[f for f in active if v in f[0]]; active=[f for f in active if v not in f[0]]
            boundary=tuple(sorted({u for s,_ in bucket for u in s}-{v})); scope=(v,)+boundary
            message=messages[i]; s,table=message; record=trace[i]
            require(s==boundary and record[0]==v and record[1]==list(boundary))
            ref.validate(d,[message]); rows=record[2]; args={}
            for row,x in rows:
                require(type(x) is int and 0<=x<d[v] and all(type(z) is int for z in row))
                require(tuple(row) not in args); args[tuple(row)]=x
            require(list(args)==sorted(table) and set(args)==set(table))
            key=signature(d,v,bucket,message,rows)
            if self.receipts.get(v)==key: hits+=1
            else:
                # Attainment: each claimed row has its specified feasible witness.
                for row,c in table.items():
                    a=dict(zip(boundary,row)); a[v]=args[row]; require(value(bucket,a)==c); attainment+=1
                # Dominance, completeness and deterministic tie break for every feasible assignment.
                script,vs=formal.encode({u:d[u] for u in scope},bucket); clauses=[]
                for row,c in sorted(table.items()):
                    conditions=[f'(= {vs[u]} {formal.integer(x)})' for u,x in zip(boundary,row)]
                    z=formal.integer(c); arg=formal.integer(args[row])
                    conditions.append(f'(or (> total {z}) (and (= total {z}) (>= {vs[v]} {arg})))')
                    clauses.append(formal.conjunction(conditions))
                covered='(or '+' '.join(clauses)+')' if clauses else 'false'
                self.smt.check(script+'(assert (not '+covered+'))','unsat'); queries+=1
            receipts[v]=key; back.append((v,boundary,args)); active.append(message)
            visits+=math.prod(d[u] for u in scope); width=max(width,len(boundary))
        require(all(not s for s,_ in active)); optimum=value(active,{})
        require(r['optimum'] is None if optimum is None else type(r['optimum']) is int and r['optimum']==optimum)
        require(type(r['assignments_evaluated']) is int and r['assignments_evaluated']==visits and type(r['induced_width']) is int and r['induced_width']==width)
        if optimum is None: require(r['witness'] is None)
        else:
            witness={}
            for v,s,args in reversed(back): witness[v]=args[tuple(witness[u] for u in s)]
            require(isinstance(r['witness'],dict) and all(type(x) is int for x in r['witness'].values()) and witness==r['witness'] and value(fs,witness)==optimum)
        self.receipts=receipts
        return dict(queries=queries,hits=hits,attainment=attainment,buckets=len(order))


def symbolic(smt):
    cases=[('forward_rank_queue','(declare-const a Int)(declare-const b Int)(declare-const c Int)(assert (< a b))(assert (<= b c))(assert (>= a c))','unsat'),
           ('lower_bound_composition','(declare-const a Int)(declare-const b Int)(declare-const c Int)(declare-const tail Int)(assert (<= a b))(assert (<= b c))(assert (> (+ a tail) (+ c tail)))','unsat'),
           ('witness_cost_lift','(declare-const before Int)(declare-const after Int)(declare-const p Int)(declare-const tail Int)(assert (= before (+ p tail)))(assert (= after (+ p tail)))(assert (not (= before after)))','unsat')]
    return [dict(name=n,result=smt.check(s,w),sha256=hashlib.sha256(s.encode()).hexdigest()) for n,s,w in cases]


def audit():
    smt=formal.SMT(); lemmas=symbolic(smt); rows=[]; global_queries=0; controls=0
    def check(c,e,r,label,stage,global_check=False):
        nonlocal global_queries
        fs=list(e.inputs.values()); a=c.verify(e.d,fs,r,e.outputs)
        if global_check: global_queries+=formal.verify(smt,e.d,fs,r)
        rows.append(dict(case=label,stage=stage,variables=len(e.d),feasible=r['optimum'] is not None,**a))
    for i,kind in enumerate(gap.FAMILIES):
        for j in range(2):
            d,variants=gap.build(kind,22100+i*100+j,j); fs=variants[0][1]; inputs={str(k):f for k,f in enumerate(fs)}
            e=idx.Indexed(d,ref.min_fill(d,fs)); c=Checker(smt); label=f'{kind}:{j}'
            r=e.update(inputs)['result']; check(c,e,r,label,'initial',True)
            r=e.update({})['result']; check(c,e,r,label,'repeat'); require(rows[-1]['queries']==0)
            nd=dict(d); nd[e.order[0]]+=1; e,x=arb.transfer(e,nd,inputs,ref.min_fill(nd,fs)); check(c,e,x['result'],label,'migration',True)
            for stage,edits in (('forbid',{'test':((e.order[-1],),{})}),('remove',{'test':None})):
                r=e.update(edits)['result']; check(c,e,r,label,stage)
    d,fs=sep.instance(22999,128,'chain'); e=idx.Indexed(d,ref.min_fill(d,fs)); c=Checker(smt)
    r=e.update({str(k):f for k,f in enumerate(fs)})['result']; check(c,e,r,'large_chain','initial')
    r=e.update({'test':((e.order[0],),{(0,):0})})['result']; check(c,e,r,'large_chain','local_edit')
    for d,fs in (({},[]),({},[((),{})]),({'a':1},[])):
        e=idx.Indexed(d,sorted(d)); r=e.update({str(k):f for k,f in enumerate(fs)})['result']; check(Checker(smt),e,r,'boundary','initial',True)
    d={'a':2,'b':2}; fs=[(('a','b'),{(0,0):0,(1,0):0,(1,1):2})]; e=idx.Indexed(d,['a','b']); r=e.update({'f':fs[0]})['result']; c=Checker(smt); c.verify(d,fs,r,e.outputs); old=copy.deepcopy(c.receipts)
    for kind in ('wrong_cost','missing_row','nonminimal','tie','bad_scope','bad_witness','bad_count','bad_order','bool_arg'):
        q=copy.deepcopy(r); m=copy.deepcopy(e.outputs)
        if kind=='wrong_cost': m[0][1][(0,)]=1
        if kind=='missing_row': del m[0][1][(1,)]; q['trace'][0][2].pop()
        if kind=='nonminimal': m[1][1][()]=2; q['trace'][1][2][0][1]=1
        if kind=='tie': q['trace'][0][2][0][1]=1
        if kind=='bad_scope': m[0]=((),m[0][1])
        if kind=='bad_witness': q['witness']['a']=1
        if kind=='bad_count': q['assignments_evaluated']+=1
        if kind=='bad_order': q['order'].reverse()
        if kind=='bool_arg': q['trace'][0][2][0][1]=False
        try: c.verify(d,fs,q,m)
        except ValueError: require(c.receipts==old); controls+=1
        else: raise ValueError('accepted '+kind)
    require(c.verify(d,fs,r,e.outputs)['hits']==2)
    out=dict(rows=rows,lemmas=lemmas,global_queries=global_queries,controls=controls,z3=smt.version,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='local SMT certificate chain with exact trusted receipt reuse; all output tables checked; abstract arithmetic lemmas only, not Python refinement or physical machine proof')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),global_queries=r['global_queries'],controls=r['controls'],**{k:sum(x[k] for x in r['rows']) for k in ('queries','hits','attainment','buckets','feasible')}),indent=2))
