"""Phase XXXVI: trusted copy-on-write staging and transaction profiling."""
import copy
import sqlite3
import time
import mra_x_singlepass as sp
import mra_x_service as s
import mra_x_state as state


def execute(old,edits,prepared,action,*,fork=True):
    """Private speculative engine; Indexed.update replaces rather than mutates shared data.

    No concurrent mutation, arbitrary hooks, or exposure of the speculative engine.
    Migrations retain the original deep-copy/transfer path. The verifier rebuilds
    the committed engine from checked mathematical content, not the fork's routes.
    """
    start=time.perf_counter_ns()
    if action!='indexed':
        new,result=s.t.execute(old,edits,prepared,action)
        return new,result,dict(forked=False,clone_ns=0,execute_ns=time.perf_counter_ns()-start)
    new=copy.copy(old) if fork else copy.deepcopy(old)
    cloned=time.perf_counter_ns(); result=new.update(edits)
    return new,result,dict(forked=fork,clone_ns=cloned-start,execute_ns=time.perf_counter_ns()-cloned)


class Store(sp.Store):
    use_fork=True

    def apply(self,edits,domain_edits=None):
        start=time.perf_counter_ns(); p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        prepared=time.perf_counter_ns(); candidate,z,profile=execute(self.engine,edits,p,action,fork=self.use_fork)
        solved=time.perf_counter_ns(); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            locked=time.perf_counter_ns(); snap,doc=sp.from_candidate(candidate,z['result'],v,d,inputs,self.engine.budget)
            materialized=time.perf_counter_ns(); e,q,staged=sp.checked(snap,doc,self._receipts)
            checked=time.perf_counter_ns(); self.persist(db,snap,doc,q)
        finished=time.perf_counter_ns()
        self.engine=e; self.version=v; self._receipts=staged
        profile.update(prepare_ns=prepared-start,lock_ns=locked-solved,materialize_ns=materialized-locked,verify_ns=checked-materialized,persist_ns=finished-checked)
        return dict(version=v,action=action,actual=z['actual'],receipt=q,profile=profile)


class Deep(Store):
    """Matched profiling control: same pipeline, original deep-copy staging."""
    use_fork=False
