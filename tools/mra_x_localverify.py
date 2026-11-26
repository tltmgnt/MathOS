"""Phase XXXV: copy-on-write independently checked routes at fixed domains/order."""
import itertools
import math
import sqlite3
import zlib
import mra_x_archive as a
import mra_x_indexed as idx
import mra_x_kernel as k
import mra_x_routed as r
import mra_x_singlepass as sp
import mra_x_service as s
import mra_x_state as state


def verify(snap,doc,old,receipts):
    # Migrations and recovery use the full independent routing checker.
    if not sp.same(snap['domains'],old.d) or snap['order']!=list(old.order):
        e,q,staged=sp.checked(snap,doc,receipts)
        q.update(local=False,rewired=q['routes'],keys_built=e.n)
        return e,q,staged
    a.fields(snap,'schema version domains order budget inputs outputs records counts')
    a.require(type(snap['schema']) is int and snap['schema']==1 and type(snap['version']) is int and snap['version']>=0 and type(snap['budget']) is int and snap['budget']==old.budget)
    a.fields(doc,'schema problem result messages'); a.require(type(doc['schema']) is int and doc['schema']==1)
    d=snap['domains']; order=snap['order']; result=doc['result']; inputs=snap['inputs']; outputs=snap['outputs']; records=snap['records']; counts=snap['counts']; n=old.n
    a.require(type(order) is list and all(type(v) is str for v in order))
    a.fields(result,'order optimum witness induced_width assignments_evaluated trace')
    a.require(type(inputs) is list and len(inputs)<=1024 and all(type(x) is list and len(x)==2 and type(x[0]) is str and 0<len(x[0])<=128 for x in inputs))
    names=[x[0] for x in inputs]; a.require(names==sorted(set(names)))
    a.require(all(type(x) is list and len(x)==n for x in (outputs,records,counts)))
    p=doc['problem']; a.fields(p,'domains factors')
    a.require(p['domains'] is d and type(p['factors']) is list and len(p['factors'])==len(inputs) and all(f is item[1] for f,item in zip(p['factors'],inputs)))
    a.require(doc['messages'] is outputs and result['trace'] is records and result['order'] is order)
    e=idx.Indexed(d,order,old.budget); routes=old.buckets[:]; e.buckets=routes
    dirty=set(); rewired=keys_built=visits=fresh=hits=lookups=width=0; staged={}; back=[]
    def change(key,prior,new,after=-1):
        nonlocal rewired
        if prior==new: return
        for f,insert in ((prior,False),(new,True)):
            if f is None: continue
            dest=e.dest(f[0]); a.require(dest>after)
            if dest not in dirty: routes[dest]=routes[dest].copy(); dirty.add(dest)
            if insert: routes[dest][key]=f
            else: del routes[dest][key]
            rewired+=1
    for name,f in inputs:
        decoded=a.factor(d,f); e.inputs[name]=decoded
        change(('input',name),old.inputs.get(name),decoded)
    for name in old.inputs.keys()-e.inputs.keys(): change(('input',name),old.inputs[name],None)
    def cost(fs,assignment):
        nonlocal lookups
        total=0
        for scope,tab in fs:
            lookups+=1; a.require(lookups<=a.MAX_LOOKUPS)
            val=tab.get(tuple(assignment[u] for u in scope))
            if val is None: return None
            total+=val
        return total
    for i,v in enumerate(order):
        bucket=routes[i].values()
        boundary=old.outputs[i][0] if i not in dirty else tuple(sorted({u for scope,_ in bucket for u in scope}-{v}))
        width=max(width,len(boundary)); count=d[v]*math.prod(d[u] for u in boundary); visits+=count
        a.require(type(counts[i]) is int and counts[i]==count and visits<=min(a.MAX_VISITS,e.budget))
        ms,tab=a.factor(d,outputs[i]); a.require(ms==boundary)
        rec=records[i]; a.require(type(rec) is list and len(rec)==3 and rec[:2]==[v,list(boundary)] and type(rec[2]) is list)
        args={}
        for row in rec[2]:
            a.require(type(row) is list and len(row)==2); ar,x=row
            a.require(type(ar) is list and len(ar)==len(boundary) and all(type(y) is int and 0<=y<d[u] for u,y in zip(boundary,ar)) and type(x) is int and 0<=x<d[v])
            ar=tuple(ar); a.require(ar not in args); args[ar]=x
        a.require(list(args)==sorted(tab) and set(args)==set(tab))
        new=(ms,tab)
        if i not in dirty and new==old.outputs[i] and sp.same(rec,old.records[i]):
            key=receipts[v]  # previously verified exact bucket and proof, unchanged
        else:
            keys_built+=1
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
        staged[v]=key; back.append((v,boundary,args)); e.outputs[i]=new; e.records[i]=rec; e.counts[i]=count
        change(('message',i),old.outputs[i],new,i)
    optimum=cost(routes[n].values(),{})
    a.require(result['optimum'] is None if optimum is None else a.integer(result['optimum']) and result['optimum']==optimum)
    a.require(type(result['induced_width']) is int and result['induced_width']==width and type(result['assignments_evaluated']) is int and result['assignments_evaluated']==visits)
    if optimum is None: a.require(result['witness'] is None)
    else:
        assignment={}
        for v,boundary,args in reversed(back): assignment[v]=args[tuple(assignment[u] for u in boundary)]
        a.require(type(result['witness']) is dict and all(type(x) is int for x in result['witness'].values()) and assignment==result['witness'] and cost(e.inputs.values(),assignment)==optimum)
    raw=a.canonical(doc); a.require(len(raw)<=k.MAX_BYTES)
    q=dict(problem_sha256=a.digest(p),certificate_sha256=r.sha(raw),optimum=optimum,variables=n,visits=visits,fresh=fresh,hits=hits,lookups=lookups,local=True,rewired=rewired,keys_built=keys_built)
    return e,q,staged


class Store(sp.Store):
    def apply(self,edits,domain_edits=None):
        p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,z=s.t.execute(self.engine,edits,p,action); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            snap,doc=sp.from_candidate(candidate,z['result'],v,d,inputs,self.engine.budget)
            e,q,staged=verify(snap,doc,self.engine,self._receipts); self.persist(db,snap,doc,q)
        self.engine=e; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=z['actual'],receipt=q)


class Adaptive(Store):
    """Fixed size-based heuristic, not a learned compression policy."""
    def persist(self,db,snap,doc,receipt):
        raw=a.canonical(dict(snapshot=snap,result={key:value for key,value in doc['result'].items() if key not in ('order','trace')}))
        a.require(len(raw)<=k.MAX_BYTES)
        level=3 if len(raw)<=16384 else 5
        z=zlib.compressobj(1,zlib.DEFLATED,15,level); blob=z.compress(raw)+z.flush(); a.require(len(blob)<=k.MAX_BYTES)
        v=snap['version']; db.execute('INSERT INTO dense_versions VALUES (?,?,?,0)',(v,r.sha(raw),blob)); db.execute('DELETE FROM dense_versions WHERE version<=?',(v-s.MAX_HISTORY,))
        receipt.update(manifest_bytes=len(blob),memlevel=level)
