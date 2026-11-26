"""Phase XXXII: compact integer-addressed SQLite proof persistence."""
import json
import sqlite3
import zlib
from pathlib import Path
import mra_x_archive as a
import mra_x_cas as cas
import mra_x_kernel as k
import mra_x_routed as r
import mra_x_service as s
import mra_x_state as state


def compress(raw):
    a.require(len(raw)<=k.MAX_BYTES)
    return zlib.compress(raw,1)


def unpack(blob,digest):
    a.require(type(blob) is bytes and len(blob)<=k.MAX_BYTES)
    z=zlib.decompressobj(); raw=z.decompress(blob,k.MAX_BYTES+1)
    a.require(len(raw)<=k.MAX_BYTES and z.eof and not z.unused_data and not z.unconsumed_tail and r.sha(raw)==digest)
    m=json.loads(raw,object_pairs_hook=a.unique); a.require(a.canonical(m)==raw); return m


def refs(m):
    a.fields(m,'schema version domains order budget counts inputs proofs result')
    ins,ps=m['inputs'],m['proofs']
    a.require(type(ins) is list and len(ins)<=1024 and type(ps) is list and len(ps)<=128)
    a.require(all(type(x) is list and len(x)==2 for x in ins))
    ids=[x[1] for x in ins]+ps
    a.require(all(type(x) is int and x>0 for x in ids)); return set(ids)


def reconstruct(m,objects):
    a.require(refs(m)==set(objects))
    ins=[[name,objects[i]] for name,i in m['inputs']]; ps=[objects[i] for i in m['proofs']]
    a.require(all(type(x) is list and len(x)==2 for x in ps))
    snap={key:m[key] for key in ('schema','version','domains','order','budget','counts')}
    snap.update(inputs=ins,outputs=[x[0] for x in ps],records=[x[1] for x in ps])
    a.fields(m['result'],'optimum witness induced_width assignments_evaluated')
    doc=dict(schema=1,problem=dict(domains=m['domains'],factors=[f for _,f in ins]),result=dict(m['result'],order=m['order'],trace=snap['records']),messages=snap['outputs'])
    a.require(len(a.canonical(snap))<=k.MAX_BYTES and len(a.canonical(doc))<=k.MAX_BYTES)
    return snap,doc


def manifest(row):
    v,h,blob,reads=row
    a.require(type(reads) is int and 0<=reads<=s.MAX_READS)
    m=unpack(blob,h); a.require(type(m['version']) is int and m['version']==v); return m


def batches(keys):
    keys=list(keys)
    for i in range(0,len(keys),400): yield keys[i:i+400]


class Store:
    """No reference table; bounded retained manifests define reachability."""
    def schema(self,db):
        db.execute('CREATE TABLE IF NOT EXISTS dense_objects (id INTEGER PRIMARY KEY, hash BLOB UNIQUE NOT NULL, payload BLOB NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS dense_versions (version INTEGER PRIMARY KEY, hash TEXT NOT NULL, manifest BLOB NOT NULL, reads INTEGER NOT NULL)')

    def load(self,db,row):
        m=manifest(row); ids=refs(m); objects={}; size=0
        for chunk in batches(ids):
            for i,h,raw in db.execute('SELECT id,hash,payload FROM dense_objects WHERE id IN ('+','.join('?' for _ in chunk)+')',chunk):
                size+=len(raw); a.require(size<=2*k.MAX_BYTES and bytes.fromhex(r.sha(raw))==h)
                obj=json.loads(raw,object_pairs_hook=a.unique); a.require(a.canonical(obj)==raw); objects[i]=obj
        return reconstruct(m,objects)

    def persist(self,db,snap,doc,receipt):
        sr=a.canonical(snap); cr=a.canonical(doc); a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES)
        m,objects=cas.encode(snap,doc); ids={}
        for chunk in batches(objects):
            for i,h,raw in db.execute('SELECT id,hash,payload FROM dense_objects WHERE hash IN ('+','.join('?' for _ in chunk)+')',[bytes.fromhex(x) for x in chunk]):
                key=h.hex(); a.require(objects[key]==raw); ids[key]=i
        new=[(bytes.fromhex(h),raw) for h,raw in objects.items() if h not in ids]
        for h,raw in new: ids[h.hex()]=db.execute('INSERT INTO dense_objects(hash,payload) VALUES (?,?)',(h,raw)).lastrowid
        m['inputs']=[[name,ids[h]] for name,h in m['inputs']]; m['proofs']=[ids[h] for h in m['proofs']]
        raw=a.canonical(m); blob=compress(raw); v=snap['version']
        db.execute('INSERT INTO dense_versions VALUES (?,?,?,0)',(v,r.sha(raw),blob))
        deleted=db.execute('DELETE FROM dense_versions WHERE version<=?',(v-s.MAX_HISTORY,)).rowcount
        if deleted:
            live=set()
            for row in db.execute('SELECT * FROM dense_versions'): live.update(refs(manifest(row)))
            present={x[0] for x in db.execute('SELECT id FROM dense_objects')}; a.require(live<=present)
            db.executemany('DELETE FROM dense_objects WHERE id=?',[(i,) for i in present-live])
        receipt.update(certificate_sha256=r.sha(cr),new_objects=len(new),reused_objects=len(objects)-len(new),new_bytes=sum(len(x[1]) for x in new),manifest_bytes=len(blob))

    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        with sqlite3.connect(self.path) as db:
            self.schema(db); db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM dense_versions ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                a.require(domains is not None); e=s.t.initial(domains,budget); doc=s.certificate(e,e.update({})['result']); snap=state.snapshot(e,0)
                e,receipt,receipts=r.verify(snap,doc,{}); self.persist(db,snap,doc,receipt)
            else:
                a.require(domains is None); snap,doc=self.load(db,row); e,receipt,receipts=r.verify(snap,doc,{}); receipt['certificate_sha256']=a.digest(doc)
        self.engine=e; self.version=snap['version']; self._receipts=receipts; self.seed=receipt

    def apply(self,edits,domain_edits=None):
        p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,z=s.t.execute(self.engine,edits,p,action); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            doc=s.certificate(candidate,z['result']); snap=state.snapshot(candidate,v)
            a.require(a.canonical([snap['domains'],snap['inputs']])==a.canonical([d,[[name,state.pack(f)] for name,f in sorted(inputs.items())]]) and type(snap['budget']) is int and snap['budget']==self.engine.budget)
            e,receipt,staged=r.verify(snap,doc,self._receipts); self.persist(db,snap,doc,receipt)
        self.engine=e; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=z['actual'],receipt=receipt)

    def get(self,v):
        a.require(type(v) is int and v>=0)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM dense_versions WHERE version=?',(v,)).fetchone(); a.require(row is not None)
            snap,doc=self.load(db,row); _,checked,_=r.verify(snap,doc,{})
            receipt={key:checked[key] for key in ('problem_sha256','optimum','variables','visits','lookups')}; receipt['certificate_sha256']=a.digest(doc)
            db.execute('UPDATE dense_versions SET reads=min(reads+1,?) WHERE version=?',(s.MAX_READS,v))
        return receipt

    def history(self):
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN'); rows=db.execute('SELECT * FROM dense_versions ORDER BY version').fetchall()
            a.require(1<=len(rows)<=s.MAX_HISTORY and all(y[0]==x[0]+1 for x,y in zip(rows,rows[1:])))
            docs=[]
            for row in rows:
                snap,doc=self.load(db,row); r.verify(snap,doc,{}); docs.append(doc)
        return [x[0] for x in rows],docs,[x[-1]+1 for x in rows]


class Compressed(Store):
    """Stronger baseline: one compressed self-contained snapshot per version."""
    def schema(self,db):
        db.execute('CREATE TABLE IF NOT EXISTS dense_versions (version INTEGER PRIMARY KEY, hash TEXT NOT NULL, manifest BLOB NOT NULL, reads INTEGER NOT NULL)')

    def persist(self,db,snap,doc,receipt):
        cr=a.canonical(doc); a.require(len(cr)<=k.MAX_BYTES and len(a.canonical(snap))<=k.MAX_BYTES)
        raw=a.canonical(dict(snapshot=snap,result={key:v for key,v in doc['result'].items() if key not in ('order','trace')})); blob=compress(raw); v=snap['version']
        db.execute('INSERT INTO dense_versions VALUES (?,?,?,0)',(v,r.sha(raw),blob)); db.execute('DELETE FROM dense_versions WHERE version<=?',(v-s.MAX_HISTORY,))
        receipt.update(certificate_sha256=r.sha(cr),manifest_bytes=len(blob))

    def load(self,db,row):
        v,h,blob,reads=row; a.require(type(reads) is int and 0<=reads<=s.MAX_READS)
        m=unpack(blob,h); a.fields(m,'snapshot result'); snap=m['snapshot']; a.require(type(snap['version']) is int and snap['version']==v)
        a.fields(m['result'],'optimum witness induced_width assignments_evaluated')
        doc=dict(schema=1,problem=dict(domains=snap['domains'],factors=[f for _,f in snap['inputs']]),result=dict(m['result'],order=snap['order'],trace=snap['records']),messages=snap['outputs'])
        a.require(len(a.canonical(doc))<=k.MAX_BYTES); return snap,doc
