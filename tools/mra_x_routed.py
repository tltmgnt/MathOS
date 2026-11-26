"""Phase XXX: independently routed certificate checking and checked state restoration."""
import hashlib
import itertools
import json
import math
import sqlite3
import time
from pathlib import Path
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_service as s
import mra_x_indexed as idx
import mra_x_state as state


def sha(raw): return hashlib.sha256(raw).hexdigest()


def verify(snap,doc,receipts):
    """Build all routes independently; only reuse exact verified local obligations."""
    a.fields(snap,'schema version domains order budget inputs outputs records counts')
    a.require(type(snap['schema']) is int and snap['schema']==1 and type(snap['version']) is int and snap['version']>=0)
    a.fields(doc,'schema problem result messages'); a.require(type(doc['schema']) is int and doc['schema']==1)
    d=snap['domains']; order=snap['order']; r=doc['result']
    a.require(type(d) is dict and len(d)<=128 and all(type(v) is str and 0<len(v)<=128 and type(n) is int and 1<=n<=4 for v,n in d.items()))
    a.require(type(order) is list and all(type(v) is str for v in order) and len(order)==len(d) and set(order)==set(d))
    a.fields(r,'order optimum witness induced_width assignments_evaluated trace')
    inputs=snap['inputs']; outputs=snap['outputs']; records=snap['records']; counts=snap['counts']
    a.require(type(inputs) is list and len(inputs)<=1024 and all(type(x) is list and len(x)==2 and type(x[0]) is str and 0<len(x[0])<=128 for x in inputs))
    names=[x[0] for x in inputs]; a.require(names==sorted(set(names)))
    a.require(all(type(x) is list and len(x)==len(order) for x in (outputs,records,counts)))
    # Canonical equality prevents Python's bool/int equality from masking corruption.
    problem=dict(domains=d,factors=[f for _,f in inputs])
    a.require(a.canonical(doc['problem'])==a.canonical(problem) and a.canonical([doc['messages'],r['trace'],r['order']])==a.canonical([outputs,records,order]))
    e=idx.Indexed(d,order,snap['budget']); routes=e.buckets; rank=e.rank; n=e.n
    routing=visits=fresh=hits=lookups=width=0; staged={}; back=[]
    def put(key,f,after=-1):
        nonlocal routing
        dest=min((rank[v] for v in f[0]),default=n); a.require(dest>after)
        routes[dest][key]=f; routing+=1
    for name,f in inputs:
        decoded=a.factor(d,f); e.inputs[name]=decoded; put(('input',name),decoded)
    def cost(fs,assignment):
        nonlocal lookups
        total=0
        for scope,tab in fs:
            lookups+=1; a.require(lookups<=a.MAX_LOOKUPS)
            v=tab.get(tuple(assignment[u] for u in scope))
            if v is None: return None
            total+=v
        return total
    for i,v in enumerate(order):
        bucket=list(routes[i].values()); boundary=tuple(sorted({u for scope,_ in bucket for u in scope}-{v}))
        width=max(width,len(boundary)); count=d[v]*math.prod(d[u] for u in boundary); visits+=count
        a.require(type(counts[i]) is int and counts[i]==count and visits<=min(a.MAX_VISITS,e.budget))
        ms,tab=a.factor(d,outputs[i]); a.require(ms==boundary)
        rec=records[i]; a.require(type(rec) is list and len(rec)==3 and rec[:2]==[v,list(boundary)] and type(rec[2]) is list)
        args={}
        for row in rec[2]:
            a.require(type(row) is list and len(row)==2); ar,x=row
            a.require(type(ar) is list and len(ar)==len(boundary) and all(type(y) is int and 0<=y<d[u] for u,y in zip(boundary,ar)) and type(x) is int and 0<=x<d[v])
            ar=tuple(ar); a.require(ar not in args); args[ar]=x
        # Preserve canonical trace order for the restored engine.
        a.require(list(args)==sorted(tab) and set(args)==set(tab))
        key=(tuple((u,d[u]) for u in (v,)+boundary),tuple(sorted((scope,tuple(sorted(table.items()))) for scope,table in bucket)),tuple(sorted(tab.items())),tuple(sorted(args.items())))
        if receipts.get(v)==key: hits+=1
        else:
            fresh+=count
            for row in itertools.product(*(range(d[u]) for u in boundary)):
                assignment=dict(zip(boundary,row)); claim=tab.get(row); attained=False
                for x in range(d[v]):
                    assignment[v]=x; val=cost(bucket,assignment)
                    if val is None: continue
                    a.require(claim is not None and (val,x)>=(claim,args[row]))
                    if (val,x)==(claim,args[row]): attained=True
                a.require(attained==(claim is not None))
        staged[v]=key; back.append((v,boundary,args)); e.outputs[i]=(ms,tab); e.records[i]=rec; e.counts[i]=count
        put(('message',i),e.outputs[i],i)
    optimum=cost(routes[n].values(),{})
    a.require(r['optimum'] is None if optimum is None else a.integer(r['optimum']) and r['optimum']==optimum)
    a.require(type(r['induced_width']) is int and r['induced_width']==width and type(r['assignments_evaluated']) is int and r['assignments_evaluated']==visits)
    if optimum is None: a.require(r['witness'] is None)
    else:
        assignment={}
        for v,boundary,args in reversed(back): assignment[v]=args[tuple(assignment[u] for u in boundary)]
        a.require(type(r['witness']) is dict and all(type(x) is int for x in r['witness'].values()) and assignment==r['witness'] and cost(e.inputs.values(),assignment)==optimum)
    return e,dict(problem_sha256=a.digest(problem),optimum=optimum,variables=n,visits=visits,fresh=fresh,hits=hits,lookups=lookups,routes=routing),staged


class Store(s.Store):
    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS verified (version INTEGER PRIMARY KEY, sh TEXT, snapshot BLOB, ch TEXT, certificate BLOB, reads INTEGER NOT NULL)')
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM verified ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                a.require(domains is not None); e=s.t.initial(domains,budget); doc=s.certificate(e,e.update({})['result']); snap=state.snapshot(e,0)
                e,receipt,receipts=verify(snap,doc,{})
                self.persist(db,0,snap,doc,receipt)
            else:
                a.require(domains is None); v,sh,sr,ch,cr,reads=row
                a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES and type(reads) is int and 0<=reads<=s.MAX_READS)
                snap=json.loads(sr,object_pairs_hook=a.unique); doc=json.loads(cr,object_pairs_hook=a.unique)
                a.require(a.digest(snap)==sh and a.digest(doc)==ch and snap['version']==v)
                e,receipt,receipts=verify(snap,doc,{}); receipt['certificate_sha256']=ch
        self.engine=e; self.version=snap['version']; self._receipts=receipts; self.seed=receipt

    @staticmethod
    def persist(db,v,snap,doc,receipt):
        sr=a.canonical(snap); cr=a.canonical(doc); a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES)
        ch=sha(cr); receipt['certificate_sha256']=ch
        db.execute('INSERT INTO verified VALUES (?,?,?,?,?,0)',(v,sha(sr),sr,ch,cr))
        db.execute('DELETE FROM verified WHERE version<=?',(v-s.MAX_HISTORY,))

    def apply(self,edits,domain_edits=None):
        start=time.perf_counter_ns(); p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,r=s.t.execute(self.engine,edits,p,action); v=self.version+1; solved=time.perf_counter_ns()
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM verified').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            doc=s.certificate(candidate,r['result']); snap=state.snapshot(candidate,v)
            a.require(a.canonical([snap['domains'],snap['inputs']])==a.canonical([d,[[name,state.pack(f)] for name,f in sorted(inputs.items())]]) and type(snap['budget']) is int and snap['budget']==self.engine.budget)
            e,receipt,staged=verify(snap,doc,self._receipts); checked=time.perf_counter_ns()
            self.persist(db,v,snap,doc,receipt)
        self.engine=e; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=r['actual'],receipt=receipt,profile_ns=dict(solver=solved-start,gate=checked-solved,persist=time.perf_counter_ns()-checked))
