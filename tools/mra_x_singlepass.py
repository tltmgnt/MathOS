"""Phase XXXIV: shared checked representation and reduced compression workspace."""
import sqlite3
import zlib
from pathlib import Path
import mra_x_archive as a
import mra_x_dense as dense
import mra_x_kernel as k
import mra_x_release as rel
import mra_x_routed as r
import mra_x_service as s
import mra_x_state as state


def same(x,y):
    """Exact typed equality for JSON values; no bool/int coercion."""
    if type(x) is not type(y): return False
    if x is y: return True
    if type(x) is list: return len(x)==len(y) and all(same(i,j) for i,j in zip(x,y))
    if type(x) is dict: return x.keys()==y.keys() and all(same(x[key],y[key]) for key in x)
    return x==y


def document(snap,summary):
    a.fields(summary,'optimum witness induced_width assignments_evaluated')
    return dict(schema=1,problem=dict(domains=snap['domains'],factors=[f for _,f in snap['inputs']]),result=dict(summary,order=snap['order'],trace=snap['records']),messages=snap['outputs'])


def from_candidate(e,result,v,d,inputs,budget):
    a.fields(result,'order trace optimum witness induced_width assignments_evaluated')
    a.require(type(e.budget) is int and e.budget==budget and same(e.d,d) and e.inputs==inputs)
    snap=state.snapshot(e,v)
    a.require(same(result['trace'],snap['records']) and same(result['order'],snap['order']))
    # Prepared inputs were already strictly validated; routed verifier checks actual snapshot types.
    doc=document(snap,{key:value for key,value in result.items() if key not in ('order','trace')})
    return snap,doc


def checked(snap,doc,receipts):
    e,receipt,staged=r.verify(snap,doc,receipts,shared=True)
    raw=a.canonical(doc); a.require(len(raw)<=k.MAX_BYTES)
    receipt['certificate_sha256']=r.sha(raw)
    return e,receipt,staged


def encode(snap,doc):
    raw=a.canonical(dict(snapshot=snap,result={key:value for key,value in doc['result'].items() if key not in ('order','trace')}))
    # The enclosing manifest bounds the included snapshot as well.
    a.require(len(raw)<=k.MAX_BYTES)
    z=zlib.compressobj(1,zlib.DEFLATED,15,3); blob=z.compress(raw)+z.flush()
    a.require(len(blob)<=k.MAX_BYTES)
    return r.sha(raw),blob


class Store(rel.Store):
    """Same compressed database format; no trust in persisted receipt keys."""
    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        if domains is None: a.require(self.path.is_file())
        with sqlite3.connect(self.path) as db:
            self.schema(db); db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM dense_versions ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                a.require(domains is not None); e=s.t.initial(domains,budget); result=e.update({})['result']
                snap,doc=from_candidate(e,result,0,e.d,e.inputs,budget); e,receipt,receipts=checked(snap,doc,{})
                self.persist(db,snap,doc,receipt)
            else:
                a.require(domains is None); snap,doc=self.load(db,row); e,receipt,receipts=checked(snap,doc,{})
        self.engine=e; self.version=snap['version']; self._receipts=receipts; self.seed=receipt

    def load(self,db,row):
        v,h,blob,reads=row; a.require(type(reads) is int and 0<=reads<=s.MAX_READS)
        m=dense.unpack(blob,h); a.fields(m,'snapshot result'); snap=m['snapshot']
        a.require(type(snap['version']) is int and snap['version']==v)
        return snap,document(snap,m['result'])

    def persist(self,db,snap,doc,receipt):
        h,blob=encode(snap,doc); v=snap['version']
        db.execute('INSERT INTO dense_versions VALUES (?,?,?,0)',(v,h,blob))
        db.execute('DELETE FROM dense_versions WHERE version<=?',(v-s.MAX_HISTORY,))
        receipt['manifest_bytes']=len(blob)

    def apply(self,edits,domain_edits=None):
        p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,z=s.t.execute(self.engine,edits,p,action); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM dense_versions').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            snap,doc=from_candidate(candidate,z['result'],v,d,inputs,self.engine.budget)
            e,receipt,staged=checked(snap,doc,self._receipts); self.persist(db,snap,doc,receipt)
        self.engine=e; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=z['actual'],receipt=receipt)

    def get(self,v):
        a.require(type(v) is int and v>=0)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM dense_versions WHERE version=?',(v,)).fetchone(); a.require(row is not None)
            snap,doc=self.load(db,row); _,q,_=checked(snap,doc,{})
            db.execute('UPDATE dense_versions SET reads=min(reads+1,?) WHERE version=?',(s.MAX_READS,v))
        return {key:q[key] for key in ('problem_sha256','certificate_sha256','optimum','variables','visits','lookups')}

    def history(self):
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN'); rows=db.execute('SELECT * FROM dense_versions ORDER BY version').fetchall()
            a.require(1<=len(rows)<=s.MAX_HISTORY and all(y[0]==x[0]+1 for x,y in zip(rows,rows[1:])))
            docs=[]
            for row in rows:
                snap,doc=self.load(db,row); checked(snap,doc,{}); docs.append(doc)
        return [x[0] for x in rows],docs,[x[-1]+1 for x in rows]
