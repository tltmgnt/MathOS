"""Phase XIV: domain-aware migration and bounded durable checkpoints."""
import argparse
import copy
import hashlib
import json
import math
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
import mra_x_state as state
import mra_x_indexed as idx
import mra_x_topology as ref
import mra_x_certify as cert
import mra_x_gap_agent as gap
import mra_x_separator as sep


def require(ok):
    if not ok: raise ValueError('migration audit failed')


def key(d,v,fs):
    scope={v}|{u for s,_ in fs for u in s}
    return (tuple(sorted((u,d[u]) for u in scope)),tuple(sorted((s,tuple(sorted(t.items()))) for s,t in fs)))


def migrate(old,d,inputs):
    inputs=copy.deepcopy({k:(tuple(s),dict(t)) for k,(s,t) in inputs.items()})
    ref.validate(d,list(inputs.values()))
    if len(inputs)>1024 or any(not isinstance(k,str) or not k or len(k)>128 for k in inputs): raise ValueError('factor envelope')
    order=[v for v in old.order if v in d]+sorted(set(d)-set(old.d))
    e=idx.Indexed(d,order,old.budget); e.inputs=inputs
    for k,f in inputs.items(): e.buckets[e.dest(f[0])][('input',k)]=f
    visits=hits=full=0
    for i,v in enumerate(order):
        fs=list(e.buckets[i].values()); boundary=tuple(sorted({u for s,_ in fs for u in s}-{v}))
        count=d[v]*math.prod(d[u] for u in boundary); full+=count
        if full>e.budget: raise idx.BudgetExceeded('full budget')
        j=old.rank.get(v)
        if j is not None and key(d,v,fs)==key(old.d,v,list(old.buckets[j].values())):
            message=copy.deepcopy(old.outputs[j]); record=copy.deepcopy(old.records[j]); hits+=1
        else:
            table={}; rows=[]; visits+=count
            for row in ref.assignments(d,boundary):
                a=dict(zip(boundary,row)); best=arg=None
                for x in range(d[v]):
                    a[v]=x; cost=ref.score(fs,a)
                    if cost is not None and (best is None or cost<best): best,arg=cost,x
                if best is not None: table[row]=best; rows.append([list(row),arg])
            message=(boundary,table); record=[v,list(boundary),rows]
        e.outputs[i]=message; e.records[i]=record; e.counts[i]=count
        dest=e.dest(message[0]); require(dest>i); e.buckets[dest][('message',i)]=message
    r=e.update({})['result']
    return e,dict(result=r,actual=visits,reused=hits)


class Store(state.Store):
    def __init__(self,path,domains=None,budget=1000000,retain=4):
        if type(retain) is not int or not 1<=retain<=64: raise ValueError('retention envelope')
        self.retain=retain; super().__init__(path,domains,budget)

    def write(self,db,e,v):
        state.Store.write(db,e,v)
        db.execute('DELETE FROM checkpoints WHERE version<=?',(v-self.retain,))

    def apply(self,edits,domain_edits=None):
        d=dict(self.engine.d)
        for v,k in (domain_edits or {}).items():
            if k is None:
                if v not in d: raise ValueError('unknown variable')
                del d[v]
            else: d[v]=k
        if d==self.engine.d: return dict(super().apply(edits,domain_edits),migrated=False,reused=None)
        inputs=dict(self.engine.inputs)
        for k,f in edits.items():
            if f is None:
                if k not in inputs: raise ValueError('unknown factor')
                del inputs[k]
            else: inputs[k]=f
        candidate,r=migrate(self.engine,d,inputs)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM checkpoints').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            self.write(db,candidate,self.version+1)
        self.engine=candidate; self.version+=1
        return dict(r,version=self.version,migrated=True,rebuilt=False)


def audit():
    rows=[]; controls=0; recoveries=0
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for i,kind in enumerate(('chain','cycle','triangles')):
            for n in (8,16,32,64):
                d,f=sep.instance(14100+i*100+n,n,kind); path=root/f'{kind}-{n}.sqlite'
                a=Store(path,d); b=state.Store(root/f'base-{kind}-{n}.sqlite',d)
                v=next(iter(d)); initial={str(j):x for j,x in enumerate(f)}; edge=((v,'extra'),{(0,0):0})
                edits=[(initial,{}),({'new':edge},{'extra':2}),({}, {'extra':3}),({}, {'extra':1}),({'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0][0],{})},{}),({'0':f[0]},{}),({}, {})]
                for step,(es,ds) in enumerate(edits):
                    r=a.apply(es,ds); s=b.apply(es,ds); e=a.engine; fs=list(e.inputs.values()); q=r['result']
                    require(q==ref.solve(e.d,fs,e.order) and cert.verify_solution(e.d,fs,q)==q['assignments_evaluated'] and q['optimum']==s['result']['optimum'])
                    if n==8: require(q['optimum']==ref.brute(e.d,fs))
                    if step in (4,9):
                        before=state.snapshot(e,a.version); a=Store(path); require(state.snapshot(a.engine,a.version)==before); recoveries+=1
                    with sqlite3.connect(path) as db: require(db.execute('SELECT count(*) FROM checkpoints').fetchone()[0]==min(4,a.version+1))
                    rows.append(dict(kind=kind,n=n,step=step,migrated=r['migrated'],reused=r['reused'],actual=r['actual'],full=q['assignments_evaluated'],baseline=s['actual'],feasible=q['optimum'] is not None))
        path=root/'fault.sqlite'; a=Store(path,{'a':2}); a.apply({'f':(('a',),{(0,):1})}); before=state.snapshot(a.engine,a.version)
        # A child exits abruptly after SQL writes but before transaction commit.
        for stage in ('before','after'):
            p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--fault',str(path),stage],timeout=15)
            require(p.returncode==91); b=Store(path)
            if stage=='before': require(state.snapshot(b.engine,b.version)==before)
            else: require(b.version==before['version']+1 and b.engine.update({})['result']['optimum']==-3)
            controls+=1
        a=Store(path); before=state.snapshot(a.engine,a.version)
        for es,ds in (({}, {'a':None}),({}, {'a':0}),({'missing':None},{'b':2})):
            try: a.apply(es,ds)
            except ValueError: require(state.snapshot(Store(path).engine,a.version)==before); controls+=1
            else: raise ValueError('invalid migration accepted')
        stale=Store(path); a.apply({}, {'a':3})
        try: stale.apply({}, {'a':4})
        except state.StaleState: require(Store(path).version==a.version); controls+=1
        else: raise ValueError('stale migration accepted')
    out=dict(rows=rows,controls=controls,recoveries=recoveries,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='domain-aware exact bucket reuse; global routing scan; append new variables; bounded checkpoint row count, not database byte bound; abrupt process exit, not power failure; full restore replay')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path); p.add_argument('--fault',nargs=2); a=p.parse_args()
    if a.fault:
        path,stage=a.fault
        class Fault(Store):
            def write(self,db,e,v):
                super().write(db,e,v)
                if stage=='before': os._exit(91)
        Fault(path).apply({'f':(('a',),{(0,):-3})},{'a':3}); os._exit(91)
    if not a.output: p.error('output required')
    r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],recoveries=r['recoveries'],migrations=sum(x['migrated'] for x in r['rows']),reused=sum(x['reused'] or 0 for x in r['rows']),**{k:sum(x[k] for x in r['rows']) for k in ('actual','full','baseline','feasible')}),indent=2))
