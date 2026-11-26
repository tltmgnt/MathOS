"""Phase XXXVII: read-only committed mathematical state and explicit working copies."""
from dataclasses import dataclass
from types import MappingProxyType as ReadOnly
import sqlite3
import mra_x_archive as a
import mra_x_indexed as idx
import mra_x_singlepass as sp
import mra_x_service as s
import mra_x_state as state


def freeze_record(rec):
    v,b,rows=rec
    return (v,tuple(b),tuple((tuple(row),x) for row,x in rows))


def thaw_record(rec):
    v,b,rows=rec
    return [v,list(b),[[list(row),x] for row,x in rows]]


@dataclass(frozen=True,slots=True)
class Owned:
    d: object
    order: tuple
    rank: object
    budget: int
    inputs: object
    buckets: tuple
    outputs: tuple
    records: tuple
    counts: tuple

    @classmethod
    def capture(cls,e):
        # Only called on independently checked engines. Copy backing dictionaries;
        # no retained mutable reference can change a published mathematical value.
        memo={}
        def factor(f):
            if id(f) not in memo: memo[id(f)]=(tuple(f[0]),ReadOnly(dict(f[1])))
            return memo[id(f)]
        return cls(ReadOnly(dict(e.d)),tuple(e.order),ReadOnly(dict(e.rank)),e.budget,
                   ReadOnly({name:factor(f) for name,f in e.inputs.items()}),
                   tuple(ReadOnly({key:factor(f) for key,f in b.items()}) for b in e.buckets),
                   tuple(factor(f) for f in e.outputs),tuple(freeze_record(rec) for rec in e.records),tuple(e.counts))

    def working(self,detach=False):
        # Private outer containers; share read-only factors/routes only on ordinary edits.
        e=idx.Indexed(dict(self.d),self.order,self.budget)
        e.records=[thaw_record(rec) for rec in self.records]; e.counts=list(self.counts)
        if not detach:
            e.inputs=dict(self.inputs); e.buckets=list(self.buckets); e.outputs=list(self.outputs)
        else:
            memo={}
            def factor(f):
                if id(f) not in memo: memo[id(f)]=(f[0],dict(f[1]))
                return memo[id(f)]
            e.inputs={name:factor(f) for name,f in self.inputs.items()}
            e.buckets=[{key:factor(f) for key,f in b.items()} for b in self.buckets]
            e.outputs=[factor(f) for f in self.outputs]
        return e


class Store(sp.Store):
    """Same disk format; inspection returns a detached mutable copy, never live state."""
    @property
    def engine(self): return self._owned.working(detach=True)

    @engine.setter
    def engine(self,e):
        if hasattr(self,'_owned'): raise AttributeError('committed engine is read-only')
        self._owned=Owned.capture(e)

    @property
    def _receipts(self): return self._checked_receipts

    @_receipts.setter
    def _receipts(self,value):
        if hasattr(self,'_checked_receipts'): raise AttributeError('committed receipts are read-only')
        self._checked_receipts=ReadOnly(dict(value))

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
            owned=Owned.capture(e); checked=ReadOnly(dict(staged))
            self.persist(db,snap,doc,q)
        self._owned=owned; self._checked_receipts=checked; self.version=v
        return dict(version=v,action=action,actual=z['actual'],receipt=q)
