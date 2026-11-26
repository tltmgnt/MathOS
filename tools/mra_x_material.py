"""Phase XXXIX: identity-bound packed-factor reuse and verified publication."""
import sqlite3
from types import MappingProxyType as ReadOnly
import mra_x_archive as a
import mra_x_share as sh
import mra_x_singlepass as sp
import mra_x_service as s
import mra_x_state as state


def cache(owned,snap=None):
    """Private packed values of checked immutable objects, with strong references."""
    out={}
    def put(f,p): out[id(f)]=(f,p if p is not None else state.pack(f))
    for i,(name,f) in enumerate(sorted(owned.inputs.items())):
        put(f,None if snap is None else snap['inputs'][i][1])
    for i,f in enumerate(owned.outputs):
        put(f,None if snap is None else snap['outputs'][i])
    return ReadOnly(out)


def materialize(e,result,v,d,inputs,budget,prior):
    a.fields(result,'order trace optimum witness induced_width assignments_evaluated')
    a.require(type(e.budget) is int and e.budget==budget and sp.same(e.d,d) and e.inputs==inputs)
    hits=misses=0
    def pack(f):
        nonlocal hits,misses
        old=prior.get(id(f))
        # No hash or value-only match; old immutable object must be identical.
        if old is not None and old[0] is f:
            hits+=1; return old[1]
        misses+=1; return state.pack(f)
    snap=dict(schema=1,version=v,domains=e.d,order=list(e.order),budget=e.budget,
              inputs=[[name,pack(f)] for name,f in sorted(e.inputs.items())],
              outputs=[pack(f) for f in e.outputs],records=e.records,counts=e.counts)
    a.require(sp.same(result['trace'],snap['records']) and sp.same(result['order'],snap['order']))
    doc=sp.document(snap,{key:value for key,value in result.items() if key not in ('order','trace')})
    return snap,doc,dict(packed_hits=hits,packed_misses=misses)


class Store(sh.Store):
    """Cache is process-private; its mutable packed lists never leave this pipeline."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._packed=cache(self._owned)

    def apply(self,edits,domain_edits=None):
        work=self._owned.working(detach=bool(domain_edits)); p=s.t.prepare(work,edits,domain_edits or {})
        d,inputs,_,action,_=p
        if action=='indexed': candidate,z=work,work.update(edits)
        else: candidate,z=s.t.execute(work,edits,p,action)
        v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            snap,doc,material=materialize(candidate,z['result'],v,d,inputs,work.budget,self._packed)
            e,q,staged=sp.checked(snap,doc,self._receipts)
            owned,checked,stats=sh.capture(e,self._owned,staged,self._receipts)
            packed=cache(owned,snap)
            self.persist(db,snap,doc,q)
        self._owned=owned; self._checked_receipts=checked; self._packed=packed; self.version=v
        return dict(version=v,action=action,actual=z['actual'],receipt=q,sharing=stats,material=material)
