"""Phase XXXI: transactional content-addressed mathematical checkpoints."""
import json
import sqlite3
from pathlib import Path
import mra_x_archive as a
import mra_x_compact as c
import mra_x_kernel as k
import mra_x_routed as r
import mra_x_service as s
import mra_x_state as state


def connect(path):
    db=sqlite3.connect(path); db.execute('PRAGMA foreign_keys=ON'); return db


def encode(snap,doc):
    objects={}
    def add(value):
        raw=a.canonical(value); h=r.sha(raw); a.require(len(raw)<=k.MAX_BYTES)
        a.require(h not in objects or objects[h]==raw); objects[h]=raw; return h
    m={key:snap[key] for key in ('schema','version','domains','order','budget','counts')}
    m['inputs']=[[name,add(f)] for name,f in snap['inputs']]
    m['proofs']=[add([f,w]) for f,w in zip(snap['outputs'],snap['records'])]
    m['result']={key:value for key,value in doc['result'].items() if key not in ('order','trace')}
    return m,objects


def load(db,row):
    v,h,raw,reads=row; a.require(len(raw)<=k.MAX_BYTES and type(reads) is int and 0<=reads<=s.MAX_READS)
    m=json.loads(raw,object_pairs_hook=a.unique); a.require(r.sha(raw)==h and a.canonical(m)==raw)
    a.fields(m,'schema version domains order budget counts inputs proofs result')
    a.require(type(m['version']) is int and m['version']==v)
    a.require(type(m['inputs']) is list and len(m['inputs'])<=1024 and type(m['proofs']) is list and len(m['proofs'])<=128)
    a.require(all(type(x) is list and len(x)==2 and c.hash_valid(x[1]) for x in m['inputs']) and all(c.hash_valid(x) for x in m['proofs']))
    keys={x[1] for x in m['inputs']}|set(m['proofs']); objects={}; size=0
    for key,payload in db.execute('SELECT o.hash,o.payload FROM cas_objects o JOIN cas_refs f ON o.hash=f.hash WHERE f.version=?',(v,)):
        a.require(key in keys and len(payload)<=k.MAX_BYTES and r.sha(payload)==key)
        size+=len(payload); a.require(size<=2*k.MAX_BYTES)
        obj=json.loads(payload,object_pairs_hook=a.unique); a.require(a.canonical(obj)==payload); objects[key]=obj
    a.require(set(objects)==keys)
    inputs=[[name,objects[key]] for name,key in m['inputs']]; proofs=[objects[key] for key in m['proofs']]
    a.require(all(type(x) is list and len(x)==2 for x in proofs))
    snap={key:m[key] for key in ('schema','version','domains','order','budget','counts')}
    snap.update(inputs=inputs,outputs=[x[0] for x in proofs],records=[x[1] for x in proofs])
    a.fields(m['result'],'optimum witness induced_width assignments_evaluated')
    result=dict(m['result'],order=m['order'],trace=snap['records'])
    doc=dict(schema=1,problem=dict(domains=m['domains'],factors=[f for _,f in inputs]),result=result,messages=snap['outputs'])
    a.require(len(a.canonical(snap))<=k.MAX_BYTES and len(a.canonical(doc))<=k.MAX_BYTES)
    return snap,doc


def persist(db,snap,doc,receipt):
    # Preserve the earlier portable certificate envelope even though it is not stored twice.
    sr=a.canonical(snap); cr=a.canonical(doc); a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES)
    m,objects=encode(snap,doc); raw=a.canonical(m); a.require(len(raw)<=k.MAX_BYTES)
    existing={}; keys=list(objects)
    for i in range(0,len(keys),400):
        chunk=keys[i:i+400]
        existing.update(db.execute('SELECT hash,payload FROM cas_objects WHERE hash IN ('+','.join('?' for _ in chunk)+')',chunk))
    a.require(all(objects[h]==value for h,value in existing.items()))
    new=[(h,v) for h,v in objects.items() if h not in existing]
    db.executemany('INSERT INTO cas_objects VALUES (?,?)',new)
    v=snap['version']; db.execute('INSERT INTO cas_versions VALUES (?,?,?,0)',(v,r.sha(raw),raw))
    db.executemany('INSERT INTO cas_refs VALUES (?,?)',[(v,h) for h in objects])
    db.execute('DELETE FROM cas_versions WHERE version<=?',(v-s.MAX_HISTORY,))
    db.execute('DELETE FROM cas_objects WHERE NOT EXISTS (SELECT 1 FROM cas_refs WHERE cas_refs.hash=cas_objects.hash)')
    receipt.update(certificate_sha256=r.sha(cr),new_objects=len(new),reused_objects=len(existing),new_bytes=sum(len(x[1]) for x in new),manifest_bytes=len(raw))


class Store:
    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        with connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS cas_objects (hash TEXT PRIMARY KEY, payload BLOB NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS cas_versions (version INTEGER PRIMARY KEY, hash TEXT NOT NULL, manifest BLOB NOT NULL, reads INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS cas_refs (version INTEGER REFERENCES cas_versions ON DELETE CASCADE, hash TEXT REFERENCES cas_objects, PRIMARY KEY(version,hash))')
            db.execute('CREATE INDEX IF NOT EXISTS cas_ref_hash ON cas_refs(hash)')
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM cas_versions ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                a.require(domains is not None); e=s.t.initial(domains,budget); doc=s.certificate(e,e.update({})['result']); snap=state.snapshot(e,0)
                e,receipt,receipts=r.verify(snap,doc,{}); persist(db,snap,doc,receipt)
            else:
                a.require(domains is None); snap,doc=load(db,row); e,receipt,receipts=r.verify(snap,doc,{})
                receipt['certificate_sha256']=a.digest(doc)
        self.engine=e; self.version=snap['version']; self._receipts=receipts; self.seed=receipt

    def apply(self,edits,domain_edits=None):
        p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,z=s.t.execute(self.engine,edits,p,action); v=self.version+1
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM cas_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            doc=s.certificate(candidate,z['result']); snap=state.snapshot(candidate,v)
            a.require(a.canonical([snap['domains'],snap['inputs']])==a.canonical([d,[[name,state.pack(f)] for name,f in sorted(inputs.items())]]) and type(snap['budget']) is int and snap['budget']==self.engine.budget)
            e,receipt,staged=r.verify(snap,doc,self._receipts); persist(db,snap,doc,receipt)
        self.engine=e; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=z['actual'],receipt=receipt)

    def get(self,v):
        a.require(type(v) is int and v>=0)
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM cas_versions WHERE version=?',(v,)).fetchone(); a.require(row is not None)
            snap,doc=load(db,row); _,checked,_=r.verify(snap,doc,{})
            receipt={key:checked[key] for key in ('problem_sha256','optimum','variables','visits','lookups')}; receipt['certificate_sha256']=a.digest(doc)
            db.execute('UPDATE cas_versions SET reads=min(reads+1,?) WHERE version=?',(s.MAX_READS,v))
        return receipt

    def history(self):
        with connect(self.path) as db:
            db.execute('BEGIN'); rows=db.execute('SELECT * FROM cas_versions ORDER BY version').fetchall()
            a.require(1<=len(rows)<=s.MAX_HISTORY and all(y[0]==x[0]+1 for x,y in zip(rows,rows[1:])))
            docs=[]
            for row in rows:
                snap,doc=load(db,row); r.verify(snap,doc,{}); docs.append(doc)
        return [x[0] for x in rows],docs,[x[-1]+1 for x in rows]
