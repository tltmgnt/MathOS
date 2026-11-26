"""Phase XXXVIII: structural sharing of independently checked immutable state."""
import sqlite3
from types import MappingProxyType as ReadOnly
import mra_x_owned as o
import mra_x_singlepass as sp
import mra_x_service as s
import mra_x_state as state


def capture(e,old,staged,previous):
    """Only checked engines and their exact checker receipts enter this function."""
    stats=dict(factors_reused=0,factors_new=0,records_reused=0,records_new=0,routes_reused=0,routes_new=0,receipts_reused=0)
    oldrank=old.rank; memo={}
    def factor(f,prior):
        if f==prior:
            frozen=prior; stats['factors_reused']+=1
        else:
            frozen=(f[0],ReadOnly(dict(f[1]))); stats['factors_new']+=1
        memo[id(f)]=frozen
        return frozen
    def mapping(data,prior):
        return prior if data==prior else ReadOnly(data)
    ins={name:factor(f,old.inputs.get(name)) for name,f in e.inputs.items()}
    outputs=[]; records=[]; receipts={}
    for i,v in enumerate(e.order):
        j=oldrank.get(v); prior=old.outputs[j] if j is not None else None
        outputs.append(factor(e.outputs[i],prior))
        key=staged[v]
        if key==previous.get(v): key=previous[v]; stats['receipts_reused']+=1
        receipts[v]=key
        # Checker requires canonical trace row order and exact integer args;
        # its final key component is exactly the immutable witness-row tuple.
        rec=(v,outputs[-1][0],key[-1])
        if j is not None and rec==old.records[j]:
            rec=old.records[j]; stats['records_reused']+=1
        else: stats['records_new']+=1
        records.append(rec)
    routes=[]; same_order=e.order==old.order
    for i,b in enumerate(e.buckets):
        data={key:memo[id(f)] for key,f in b.items()}
        prior=old.buckets[i] if same_order else None
        if prior is not None and data==prior:
            routes.append(prior); stats['routes_reused']+=1
        else:
            routes.append(ReadOnly(data)); stats['routes_new']+=1
    owned=o.Owned(mapping(dict(e.d),old.d),old.order if same_order else e.order,
                  mapping(dict(e.rank),old.rank),e.budget,mapping(ins,old.inputs),
                  tuple(routes),tuple(outputs),tuple(records),tuple(e.counts))
    return owned,ReadOnly(receipts),stats


class Store(o.Store):
    """Share only verified immutable values, retaining previous ownership protections."""
    def apply(self,edits,domain_edits=None):
        work=self._owned.working(detach=bool(domain_edits)); p=s.t.prepare(work,edits,domain_edits or {})
        d,inputs,_,action,_=p
        if action=='indexed': candidate,z=work,work.update(edits)
        else: candidate,z=s.t.execute(work,edits,p,action)
        v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            snap,doc=sp.from_candidate(candidate,z['result'],v,d,inputs,work.budget)
            e,q,staged=sp.checked(snap,doc,self._receipts)
            owned,checked,stats=capture(e,self._owned,staged,self._receipts)
            self.persist(db,snap,doc,q)
        self._owned=owned; self._checked_receipts=checked; self.version=v
        return dict(version=v,action=action,actual=z['actual'],receipt=q,sharing=stats)
