"""Phase XXV: bounded streaming proof replay with independently anchored checkpoints."""
import argparse
import json
from pathlib import Path
import mra_x_archive as a

MAX_LINE=8_000_000
MAX_TOTAL=64_000_000
MAX_LIVE=1152
ZERO='0'*64


def records(docs,interval=4):
    a.require(type(interval) is int and 1<=interval<=128)
    live={}; last=ZERO
    for i,doc in enumerate(docs):
        packed=a.pack([doc]); objects=packed['objects']; state=packed['states'][0]
        keys=[h for h,_ in objects]; current=dict(objects); checkpoint=i%interval==0
        delta={h:v for h,v in objects if checkpoint or h not in live}
        for h in current.keys() & live.keys(): a.require(a.canonical(current[h])==a.canonical(live[h]))
        state['factors']=[keys[j] for j in state['factors']]; state['proofs']=[keys[j] for j in state['proofs']]
        payload=dict(schema=1,index=i,previous=last,checkpoint=checkpoint,objects=delta,state=state)
        last=a.digest(payload); yield dict(payload=payload,sha256=last); live=current


def read_line(fp):
    raw=fp.readline(MAX_LINE+1)
    if not raw: return None,0
    a.require(len(raw)<=MAX_LINE and raw.endswith(b'\n'))
    return json.loads(raw,object_pairs_hook=a.unique),len(raw)


def verify(fp,expected,*,checkpoint=False):
    """Return receipts only after the entire supplied stream matches its trusted terminal hash."""
    a.require(type(expected) is str and len(expected)==64)
    live={}; receipts={}; results=[]; previous=ZERO; index=0; total=0; cumulative=0; peak=0
    while True:
        record,size=read_line(fp)
        if not size: break
        total+=size; a.require(total<=MAX_TOTAL and len(results)<a.MAX_STATES)
        a.fields(record,'payload sha256'); p=record['payload']; a.fields(p,'schema index previous checkpoint objects state')
        h=a.digest(p); a.require(record['sha256']==h and type(p['schema']) is int and p['schema']==1 and type(p['index']) is int and 0<=p['index']<a.MAX_STATES and type(p['checkpoint']) is bool)
        if checkpoint and not results:
            a.require(p['checkpoint']); index=p['index']; previous=p['previous']
        a.require(p['index']==index and p['previous']==previous and (index!=0 or p['checkpoint']))
        a.require(type(p['previous']) is str and len(p['previous'])==64)
        delta=p['objects']; a.require(type(delta) is dict and len(delta)<=MAX_LIVE)
        if p['checkpoint']: live={}
        for key,obj in delta.items(): a.require(key not in live and a.digest(obj)==key)
        merged={**live,**delta}; state=p['state']; a.fields(state,'domains factors proofs result problem_sha256')
        fs,ps=state['factors'],state['proofs']; a.require(type(fs) is list and len(fs)<=1024 and type(ps) is list and len(ps)<=128 and all(type(x) is str and x in merged for x in fs+ps))
        needed=set(fs+ps); a.require(set(delta)<=needed and len(needed)<=MAX_LIVE)
        peak=max(peak,len(merged)); live={key:merged[key] for key in needed}
        # Use the same local checker as Phase XXIV; the private helper consumes only validated objects.
        result,receipts=a.verify_state(state,live.__getitem__,receipts,a.MAX_ARCHIVE_VISITS-cumulative)
        cumulative+=result['visits']; results.append(result); previous=h; index+=1
    a.require(bool(results) and previous==expected and (not checkpoint or len(results)==1))
    return dict(states=results,terminal_sha256=previous,peak_objects=peak,bytes=total)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('file',type=Path); p.add_argument('--expect',required=True); p.add_argument('--checkpoint',action='store_true'); args=p.parse_args()
    try:
        with args.file.open('rb') as fp: print(json.dumps(verify(fp,args.expect,checkpoint=args.checkpoint),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError) as e: p.exit(1,'rejected: '+str(e)+'\n')
