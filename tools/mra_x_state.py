"""Phase XIII: durable versioned mathematical state and online edits."""
import argparse
import copy
import json
import sqlite3
import tempfile
from pathlib import Path
import mra_x_topology as ref
import mra_x_indexed as idx
import mra_x_certify as cert
import mra_x_gap_agent as gap
import mra_x_separator as sep


def require(ok):
    if not ok: raise ValueError('state audit failed')


def pack(f):
    s,t=f
    return [list(s),[[list(a),c] for a,c in sorted(t.items())]]


def unpack(f):
    s,rows=f
    t={tuple(a):c for a,c in rows}
    require(len(t)==len(rows))
    return tuple(s),t


def snapshot(e,version):
    return dict(schema=1,version=version,domains=e.d,order=list(e.order),budget=e.budget,
                inputs=[[k,pack(f)] for k,f in sorted(e.inputs.items())],
                outputs=[pack(f) for f in e.outputs],records=e.records,counts=e.counts)


def restore(p):
    # Full replay validates all stored numerical messages, not only the final optimum.
    require(p['schema']==1 and type(p['version']) is int and p['version']>=0)
    e=idx.Indexed(p['domains'],p['order'],p['budget'])
    inputs={k:unpack(f) for k,f in p['inputs']}; require(len(inputs)==len(p['inputs']))
    r=e.update(inputs)['result']; require(snapshot(e,p['version'])==p)
    require(cert.verify_solution(e.d,list(inputs.values()),r)==r['assignments_evaluated'])
    return e


class StaleState(ValueError):
    pass


class Store:
    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS checkpoints (version INTEGER PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT version,digest,payload FROM checkpoints ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                if domains is None: raise ValueError('initial domains required')
                e=idx.Indexed(dict(sorted(domains.items())),sorted(domains),budget); e.update({})
                self.version=0; self.engine=e; self.write(db,e,0)
            else:
                if domains is not None: raise ValueError('existing store requires reopen')
                v,h,raw=row; p=json.loads(raw); require(gap.digest(p)==h and p['version']==v)
                self.engine=restore(p); self.version=v

    @staticmethod
    def write(db,e,v):
        p=snapshot(e,v); db.execute('INSERT INTO checkpoints VALUES (?,?,?)',(v,gap.digest(p),gap.canonical(p)))

    def apply(self,edits,domain_edits=None):
        d=dict(self.engine.d); domain_edits=domain_edits or {}
        for v,k in domain_edits.items():
            if k is None:
                if v not in d: raise ValueError('unknown variable')
                del d[v]
            else: d[v]=k
        if d==self.engine.d:
            candidate=copy.deepcopy(self.engine); r=candidate.update(edits); rebuilt=False
        else:
            inputs=dict(self.engine.inputs)
            for name,f in edits.items():
                if f is None:
                    if name not in inputs: raise ValueError('unknown factor')
                    del inputs[name]
                else: inputs[name]=f
            d=dict(sorted(d.items())); ref.validate(d,list(inputs.values()))
            candidate=idx.Indexed(d,ref.min_fill(d,list(inputs.values())),self.engine.budget)
            r=candidate.update(inputs); rebuilt=True
        # Compare-and-swap: never overwrite a newer durable checkpoint.
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            latest=db.execute('SELECT max(version) FROM checkpoints').fetchone()[0]
            if latest!=self.version: raise StaleState('reopen before updating')
            self.write(db,candidate,self.version+1)
        self.engine=candidate; self.version+=1
        return dict(r,version=self.version,rebuilt=rebuilt)


def audit():
    rows=[]; controls=0; restarts=0
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for i,kind in enumerate(('chain','cycle','triangles')):
            for n in (8,16,32,64):
                d,f=sep.instance(13100+i*100+n,n,kind); path=root/f'{kind}-{n}.sqlite'
                store=Store(path,d); initial={str(j):x for j,x in enumerate(f)}
                v=next(iter(d)); a=initial['0']; changes=[(initial,{}),({'0':(a[0],{})},{}),({'0':a},{}),({},{}),({'new':((v,'extra'),{(0,0):0})},{'extra':2}),({}, {'extra':3}),({'new':None},{'extra':None}),({'0':None},{}),({'0':a},{}),({}, {})]
                for step,(edits,de) in enumerate(changes):
                    r=store.apply(edits,de); e=store.engine; result=r['result']; fs=list(e.inputs.values())
                    require(result==ref.solve(e.d,fs,e.order) and cert.verify_solution(e.d,fs,result)==result['assignments_evaluated'])
                    if n==8: require(result['optimum']==ref.brute(e.d,fs))
                    if step in (3,5,8):
                        before=snapshot(e,store.version); store=Store(path); require(snapshot(store.engine,store.version)==before); restarts+=1
                    rows.append(dict(kind=kind,n=n,step=step,variables=len(e.d),version=r['version'],rebuilt=r['rebuilt'],actual=r['actual'],full=result['assignments_evaluated'],feasible=result['optimum'] is not None))
        path=root/'controls.sqlite'; a=Store(path,{'a':2,'b':2},budget=8); a.apply({'f':(('a',),{(1,):0})}); stale=Store(path); before=snapshot(a.engine,a.version)
        for edits,de in (({}, {'a':1}),({}, {'a':None}),({'missing':None},{}),({'g':(('a','b','c'),{(0,0,0):0})},{'c':4})):
            try: a.apply(edits,de)
            except ValueError: require(snapshot(a.engine,a.version)==before and snapshot(Store(path).engine,a.version)==before); controls+=1
            else: raise ValueError('invalid transaction accepted')
        a.apply({});
        try: stale.apply({})
        except StaleState: require(stale.version==before['version'] and Store(path).version==a.version); controls+=1
        else: raise ValueError('stale writer accepted')
        # Tamper with a stored numerical message and recompute its digest: replay must reject.
        with sqlite3.connect(path) as db:
            v,raw=db.execute('SELECT version,payload FROM checkpoints ORDER BY version DESC LIMIT 1').fetchone(); p=json.loads(raw); p['outputs'][0][1][0][1]+=1
            db.execute('UPDATE checkpoints SET digest=?,payload=? WHERE version=?',(gap.digest(p),gap.canonical(p),v))
        try: Store(path)
        except ValueError: controls+=1
        else: raise ValueError('tampered state accepted')
        # Separate digest-only corruption control.
        path=root/'digest.sqlite'; Store(path,{})
        with sqlite3.connect(path) as db: db.execute('UPDATE checkpoints SET digest=?',('0'*64,))
        try: Store(path)
        except ValueError: controls+=1
        else: raise ValueError('bad digest accepted')
    out=dict(rows=rows,restarts=restarts,controls=controls,scope='SQLite append-only checkpoint history; full verified replay on restart; domain edits rebuild; ordinary edits use indexed repair; no speedup or security/authentication claim; trusted local database; no mechanized proof')
    out['evidence_sha256']=gap.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=audit()
    with a.output.open('x') as f: json.dump(r,f,indent=2)
    print(json.dumps(dict(cases=len(r['rows']),restarts=r['restarts'],controls=r['controls'],**{k:sum(x[k] for x in r['rows']) for k in ('rebuilt','actual','full','feasible')}),indent=2))
