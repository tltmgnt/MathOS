"""Phase XV: conservative migration arbitration and durable transaction telemetry."""
import argparse
import copy
import hashlib
import json
import math
import sqlite3
import tempfile
from pathlib import Path
import mra_x_state as state
import mra_x_migrate as mig
import mra_x_indexed as idx
import mra_x_topology as ref
import mra_x_upgrade as up
import mra_x_certify as cert
import mra_x_gap_agent as gap
import mra_x_separator as sep


def require(ok):
    if not ok: raise ValueError('arbitration check failed')


def estimate(old,d,inputs,order):
    """Upper bound on kernel visits; unknown projected contents force predicted misses."""
    active=list(inputs.values()); upper=full=hits=0
    for v in order:
        fs=[(s,t) for s,t in active if v in s]; active=[(s,t) for s,t in active if v not in s]
        boundary=tuple(sorted({u for s,_ in fs for u in s}-{v}))
        count=d[v]*math.prod(d[u] for u in boundary); full+=count
        j=old.rank.get(v)
        if j is not None and all(t is not None for _,t in fs) and mig.key(d,v,fs)==mig.key(old.d,v,list(old.buckets[j].values())):
            message=old.outputs[j]; hits+=1
        else:
            upper+=count; message=(boundary,None)
        active.append(message)
    return upper,full,hits


def transfer(old,d,inputs,order):
    """Same exact content/domain compatibility rule as Phase XIV, arbitrary valid order."""
    e=idx.Indexed(d,order,old.budget); e.inputs=copy.deepcopy(inputs)
    for k,f in e.inputs.items(): e.buckets[e.dest(f[0])][('input',k)]=f
    visits=hits=full=0
    for i,v in enumerate(order):
        fs=list(e.buckets[i].values()); boundary=tuple(sorted({u for s,_ in fs for u in s}-{v}))
        count=d[v]*math.prod(d[u] for u in boundary); full+=count
        if full>e.budget: raise idx.BudgetExceeded('full budget')
        j=old.rank.get(v)
        if j is not None and mig.key(d,v,fs)==mig.key(old.d,v,list(old.buckets[j].values())):
            message=copy.deepcopy(old.outputs[j]); record=copy.deepcopy(old.records[j]); hits+=1
        else:
            visits+=count; table={}; rows=[]
            for row in ref.assignments(d,boundary):
                a=dict(zip(boundary,row)); best=arg=None
                for x in range(d[v]):
                    a[v]=x; c=ref.score(fs,a)
                    if c is not None and (best is None or c<best): best,arg=c,x
                if best is not None: table[row]=best; rows.append([list(row),arg])
            message=(boundary,table); record=[v,list(boundary),rows]
        e.outputs[i]=message; e.records[i]=record; e.counts[i]=count
        dest=e.dest(boundary); require(dest>i); e.buckets[dest][('message',i)]=message
    return e,dict(result=e.update({})['result'],actual=visits,reused=hits)


class Store(mig.Store):
    def __init__(self,path,domains=None,budget=1000000,retain=4):
        super().__init__(path,domains,budget,retain)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS arbitration (version INTEGER PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL)')

    def apply(self,edits,domain_edits=None):
        d=dict(self.engine.d); inputs=dict(self.engine.inputs)
        for v,k in (domain_edits or {}).items():
            if k is None:
                if v not in d: raise ValueError('unknown variable')
                del d[v]
            else: d[v]=k
        for k,f in edits.items():
            if not isinstance(k,str) or not k or len(k)>128: raise ValueError('factor ID')
            if f is None:
                if k not in inputs: raise ValueError('unknown factor')
                del inputs[k]
            else: inputs[k]=(tuple(f[0]),dict(f[1]))
        if len(inputs)>1024: raise ValueError('factor limit')
        ref.validate(d,list(inputs.values()))
        # Validate admission before any potentially expensive planning.
        idx.Indexed(d,sorted(d),self.engine.budget)
        if d==self.engine.d:
            candidate=copy.deepcopy(self.engine); r=candidate.update(edits)
            selected='indexed'; options={}; bound=r['actual']
        else:
            stable=[v for v in self.engine.order if v in d]+sorted(set(d)-set(self.engine.d))
            fresh=ref.min_fill(d,list(inputs.values()))
            options={}
            for label,o in (('preserve',stable),('reorder',fresh)):
                upper,full,hits=estimate(self.engine,d,inputs,o)
                options[label]=dict(upper=upper,full=full,hits=hits,order=o)
            options['rebuild']=dict(upper=options['reorder']['full'],full=options['reorder']['full'],hits=0,order=fresh)
            viable=[k for k,x in options.items() if x['full']<=self.engine.budget]
            if not viable: raise idx.BudgetExceeded('no viable order')
            # Prefer smaller future full cost at equal upper bound, then simpler rebuild.
            selected=min(viable,key=lambda k:(options[k]['upper'],options[k]['full'],('rebuild','reorder','preserve').index(k)))
            choice=options[selected]; bound=choice['upper']
            if selected=='rebuild':
                candidate=idx.Indexed(d,choice['order'],self.engine.budget); r=candidate.update(inputs)
            else: candidate,r=transfer(self.engine,d,inputs,choice['order'])
            require(r['actual']<=bound and r['result']['assignments_evaluated']==choice['full'])
        v=self.version+1
        telemetry=dict(version=v,selected=selected,options=options,bound=bound,actual=r['actual'],full=r['result']['assignments_evaluated'])
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM checkpoints').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            self.write(db,candidate,v)
            db.execute('INSERT INTO arbitration VALUES (?,?,?)',(v,gap.digest(telemetry),gap.canonical(telemetry)))
            db.execute('DELETE FROM arbitration WHERE version<=?',(v-self.retain,))
        self.engine=candidate; self.version=v
        return dict(r,decision=telemetry)

    def history(self):
        with sqlite3.connect(self.path) as db:
            rows=db.execute('SELECT version,digest,payload FROM arbitration ORDER BY version').fetchall()
        out=[]
        for v,h,raw in rows:
            p=json.loads(raw); require(p['version']==v and gap.digest(p)==h); out.append(p)
        return out


def audit():
    rows=[]; controls=0; reopens=0
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for i,kind in enumerate(('chain','cycle','triangles')):
            for n in (8,16,32,64):
                d,f=sep.instance(15100+i*100+n,n,kind); v=next(iter(d)); initial={str(j):x for j,x in enumerate(f)}
                edge=((v,'extra'),{(0,0):0}); other=((list(d)[-1],'extra'),{(0,0):1})
                stream=[(initial,{}),({'new':edge},{'extra':2}),({}, {'extra':3}),({'other':other},{}),({'other':None,'new':None},{'extra':None}),({}, {v:d[v]+1}),({}, {v:d[v]}),({'0':(f[0][0],{})},{}),({'0':f[0]},{}),({}, {})]
                path=root/'candidate.sqlite'
                a=Store(path,d); b=state.Store(root/'rebuild.sqlite',d); c=mig.Store(root/'preserve.sqlite',d)
                for step,(es,ds) in enumerate(stream):
                    x=a.apply(es,ds); y=b.apply(es,ds); z=c.apply(es,ds); e=a.engine; fs=list(e.inputs.values()); r=x['result']; t=x['decision']
                    require(r==ref.solve(e.d,fs,e.order) and cert.verify_solution(e.d,fs,r)==r['assignments_evaluated'])
                    require(r['optimum']==y['result']['optimum']==z['result']['optimum'])
                    if n==8: require(r['optimum']==ref.brute(e.d,fs))
                    require(a.history()[-1]==t and len(a.history())<=4)
                    if step in (4,9):
                        before=state.snapshot(e,a.version); hist=a.history(); a=Store(path); require(state.snapshot(a.engine,a.version)==before and a.history()==hist); reopens+=1
                    rows.append(dict(kind=kind,n=n,step=step,selected=t['selected'],actual=x['actual'],bound=t['bound'],full=t['full'],rebuild=y['actual'],preserve=z['actual'],feasible=r['optimum'] is not None))
                for p in root.glob('*.sqlite'): p.unlink()
        path=root/'control.sqlite'; a=Store(path,{'a':2},budget=8); a.apply({'f':(('a',),{(1,):0})}); old=state.snapshot(a.engine,a.version); history=a.history()
        for es,ds in (({}, {'a':1}),({}, {'a':None}),({'g':(('a','b'),{(0,0):0})},{'b':4})):
            try: a.apply(es,ds)
            except ValueError: require(state.snapshot(Store(path).engine,a.version)==old and a.history()==history); controls+=1
            else: raise ValueError('invalid migration accepted')
        stale=Store(path); a.apply({})
        try: stale.apply({})
        except state.StaleState: require(Store(path).version==a.version); controls+=1
        else: raise ValueError('stale writer accepted')
        with sqlite3.connect(path) as db: db.execute('UPDATE arbitration SET digest=? WHERE version=?',('0'*64,a.version))
        try: a.history()
        except ValueError: controls+=1
        else: raise ValueError('bad history accepted')
    out=dict(rows=rows,controls=controls,reopens=reopens,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('mra_x_*.py'))},scope='online deterministic enumeration-bound arbitration; retained telemetry not learned policy; local synthetic comparison; no runtime guarantee or formal proof')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],reopens=r['reopens'],**{k:sum(x[k] for x in r['rows']) for k in ('actual','bound','full','rebuild','preserve','feasible')}),indent=2))
