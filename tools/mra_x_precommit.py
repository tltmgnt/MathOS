"""Phase XXIX: transactional incremental portable certificate verification."""
import sqlite3
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_service as s
import mra_x_state as state


def verify(doc,expected,receipts):
    a.fields(doc,'schema problem result messages')
    a.require(type(doc['schema']) is int and doc['schema']==1)
    a.fields(doc['problem'],'domains factors')
    a.require(a.canonical(doc['problem'])==a.canonical(expected))
    p=doc['problem']; r=dict(doc['result']); trace=r.pop('trace'); messages=doc['messages']
    a.require(type(trace) is list and type(messages) is list and len(trace)==len(messages)==len(p['domains']))
    fs=p['factors']; a.require(type(fs) is list and len(fs)<=1024)
    objects=fs+[[m,w] for m,w in zip(messages,trace)]
    manifest=dict(domains=p['domains'],factors=list(range(len(fs))),proofs=list(range(len(fs),len(objects))),result=r,problem_sha256=a.digest(expected))
    result,staged=a.verify_state(manifest,objects.__getitem__,receipts,a.MAX_VISITS)
    result['certificate_sha256']=a.digest(doc)
    return result,staged


class Store(s.Store):
    """Previous committed state receipts are trusted process memory, never disk data."""
    def __init__(self,path,domains=None,budget=1000000):
        super().__init__(path,domains,budget)
        # Parent performs full create/reopen checks; independently seed the receipt chain.
        doc=s.certificate(self.engine,self.engine.update({})['result'])
        self.seed,self._receipts=verify(doc,s.problem(self.engine.d,self.engine.inputs),{})

    def apply(self,edits,domain_edits=None):
        p=s.t.prepare(self.engine,edits,domain_edits or {}); d,inputs,_,action,_=p
        candidate,r=s.t.execute(self.engine,edits,p,action); v=self.version+1
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT max(version) FROM verified').fetchone()[0]!=self.version: raise state.StaleState('reopen')
            doc=s.certificate(candidate,r['result']); snap=state.snapshot(candidate,v)
            sr=a.canonical(snap); cr=a.canonical(doc)
            a.require(len(sr)<=k.MAX_BYTES and len(cr)<=k.MAX_BYTES)
            # Bind the checked certificate to the exact snapshot and prepared input.
            a.require(doc['problem']==dict(domains=snap['domains'],factors=[f for _,f in snap['inputs']]))
            a.require(doc['messages']==snap['outputs'] and doc['result']['trace']==snap['records'] and doc['result']['order']==snap['order'])
            receipt,staged=verify(doc,s.problem(d,inputs),self._receipts)
            db.execute('INSERT INTO verified VALUES (?,?,?,?,?,0)',(v,a.digest(snap),sr,a.digest(doc),cr))
            db.execute('DELETE FROM verified WHERE version<=?',(v-s.MAX_HISTORY,))
        # Publish receipts only after the database context commits successfully.
        self.engine=candidate; self.version=v; self._receipts=staged
        return dict(version=v,action=action,actual=r['actual'],receipt=receipt)
