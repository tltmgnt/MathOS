"""Phase XXVIII: verified transactions and unified, demand-aware proof retrieval."""
import json
import sqlite3
from pathlib import Path
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_state as state
import mra_x_temporal as t

from mra_x_storage import MAX_HISTORY, MAX_READS


def problem(d,inputs):
    return dict(domains=d,factors=[state.pack(f) for _,f in sorted(inputs.items())])


def certificate(e,r):
    return dict(schema=1,problem=problem(e.d,e.inputs),result=r,messages=[state.pack(f) for f in e.outputs])


def read_row(row):
    v,sh,sraw,ch,craw,reads=row
    a.require(len(sraw)<=k.MAX_BYTES and len(craw)<=k.MAX_BYTES and type(reads) is int and 0<=reads<=MAX_READS)
    snap=json.loads(sraw,object_pairs_hook=a.unique); doc=json.loads(craw,object_pairs_hook=a.unique)
    a.require(a.digest(snap)==sh and a.digest(doc)==ch and snap['version']==v)
    a.require(doc['problem']==dict(domains=snap['domains'],factors=[f for _,f in snap['inputs']]))
    a.require(doc['messages']==snap['outputs'] and doc['result']['trace']==snap['records'] and doc['result']['order']==snap['order'])
    receipt=k.check(doc); return snap,doc,receipt


class Store:
    def __init__(self,path,domains=None,budget=1000000):
        self.path=Path(path)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS verified (version INTEGER PRIMARY KEY, sh TEXT, snapshot BLOB, ch TEXT, certificate BLOB, reads INTEGER NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM verified ORDER BY version DESC LIMIT 1').fetchone()
            if row is None:
                a.require(domains is not None); e=t.initial(domains,budget); r=e.update({})['result']; self.write(db,e,r,0,problem(domains,{})); self.engine=e; self.version=0
            else:
                a.require(domains is None); p,doc,_=read_row(row); self.engine=state.restore(p); self.version=row[0]
                a.require(certificate(self.engine,self.engine.update({})['result'])==doc)

    @staticmethod
    def write(db,e,r,v,expected):
        doc=certificate(e,r); receipt=k.check(doc,a.digest(expected)); snap=state.snapshot(e,v)
        sr=a.canonical(snap); cr=a.canonical(doc); a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES)
        db.execute('INSERT INTO verified VALUES (?,?,?,?,?,0)',(v,a.digest(snap),sr,a.digest(doc),cr))
        db.execute('DELETE FROM verified WHERE version<=?',(v-MAX_HISTORY,)); return receipt

    def apply(self,edits,domain_edits=None):
        p=t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,r=t.execute(self.engine,edits,p,action); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM verified').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            receipt=self.write(db,candidate,r['result'],v,problem(d,inputs))
        self.engine=candidate; self.version=v
        return dict(version=v,action=action,actual=r['actual'],receipt=receipt)

    def get(self,v):
        a.require(type(v) is int and v>=0)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE'); row=db.execute('SELECT * FROM verified WHERE version=?',(v,)).fetchone(); a.require(row is not None)
            _,_,receipt=read_row(row)
            db.execute('UPDATE verified SET reads=min(reads+1,?) WHERE version=?',(MAX_READS,v))
        return receipt

    def history(self):
        with sqlite3.connect(self.path) as db: rows=db.execute('SELECT * FROM verified ORDER BY version').fetchall()
        a.require(1<=len(rows)<=MAX_HISTORY and all(y[0]==x[0]+1 for x,y in zip(rows,rows[1:])))
        docs=[read_row(row)[1] for row in rows]
        return [r[0] for r in rows],docs,[r[-1]+1 for r in rows]
