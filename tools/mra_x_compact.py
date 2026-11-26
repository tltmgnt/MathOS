"""Phase XXVI: compact positional references and anchored indexed replay."""
import argparse
import json
from pathlib import Path
import mra_x_archive as a

MAX_LINE=8_000_000
MAX_TOTAL=64_000_000
MAX_LIVE=1152
ZERO='0'*64


def records(docs,interval=8):
    a.require(type(interval) is int and 1<=interval<=128)
    old={}; previous=ZERO
    for i,doc in enumerate(docs):
        a.require(i<a.MAX_STATES)
        p=a.pack([doc]); state=p['states'][0]; checkpoint=i%interval==0
        current={}; objects=[]
        for j,(h,obj) in enumerate(p['objects']):
            key=a.canonical(obj); current[key]=j
            objects.append(old[key] if not checkpoint and key in old else obj)
        payload=dict(schema=2,index=i,previous=previous,checkpoint=checkpoint,objects=objects,state=state)
        previous=a.digest(payload); yield dict(payload=payload,sha256=previous); old=current


def encode(docs,interval=8):
    chunks=[]; entries=[]; offset=0
    for record in records(docs,interval):
        raw=a.canonical(record)+b'\n'; p=record['payload']
        entries.append([offset,len(raw),record['sha256'],p['checkpoint']]); chunks.append(raw); offset+=len(raw)
    a.require(bool(entries) and offset<=MAX_TOTAL)
    return b''.join(chunks),dict(schema=1,entries=entries)


def read(fp):
    raw=fp.readline(MAX_LINE+1)
    if not raw: return None,0
    a.require(len(raw)<=MAX_LINE and raw.endswith(b'\n'))
    return json.loads(raw,object_pairs_hook=a.unique),len(raw)


def hash_valid(h):
    return type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h)


def verify(fp,expected,*,start=0,count=None):
    a.require(hash_valid(expected) and type(start) is int and 0<=start<a.MAX_STATES)
    a.require(count is None or type(count) is int and 1<=count<=a.MAX_STATES-start)
    a.require(start==0 or count is not None)
    old=[]; receipts={}; results=[]; previous=ZERO; total=cumulative=peak=0
    while count is None or len(results)<count:
        record,size=read(fp)
        if not size: break
        total+=size; i=start+len(results); a.require(total<=MAX_TOTAL and i<a.MAX_STATES)
        a.fields(record,'payload sha256'); p=record['payload']; a.fields(p,'schema index previous checkpoint objects state')
        h=a.digest(p); a.require(record['sha256']==h and type(p['schema']) is int and p['schema']==2 and type(p['index']) is int and p['index']==i and type(p['checkpoint']) is bool and hash_valid(p['previous']))
        if not results:
            a.require(p['checkpoint']); previous=p['previous'] if start else ZERO
        a.require(p['previous']==previous)
        if p['checkpoint']: old=[]
        objects=p['objects']; a.require(type(objects) is list and len(objects)<=MAX_LIVE)
        current=[]
        for obj in objects:
            if type(obj) is int:
                a.require(0<=obj<len(old)); current.append(old[obj])
            else:
                a.require(type(obj) is list); current.append(obj)
        peak=max(peak,len(old)+len(current)); state=p['state']; a.fields(state,'domains factors proofs result problem_sha256')
        fs,ps=state['factors'],state['proofs']; a.require(type(fs) is list and len(fs)<=1024 and type(ps) is list and len(ps)<=128)
        a.require(all(type(j) is int and 0<=j<len(current) for j in fs+ps) and set(fs+ps)==set(range(len(current))))
        result,receipts=a.verify_state(state,current.__getitem__,receipts,a.MAX_ARCHIVE_VISITS-cumulative)
        cumulative+=result['visits']; results.append(result); old=current; previous=h
    a.require(bool(results) and previous==expected and (count is None or len(results)==count))
    return dict(states=results,terminal_sha256=previous,peak_slots=peak,bytes=total)


def validate_index(index,expected):
    a.require(hash_valid(expected) and a.digest(index)==expected)
    a.fields(index,'schema entries'); entries=index['entries']
    a.require(type(index['schema']) is int and index['schema']==1 and type(entries) is list and 1<=len(entries)<=a.MAX_STATES)
    offset=0
    for entry in entries:
        a.require(type(entry) is list and len(entry)==4); pos,size,h,cp=entry
        a.require(type(pos) is int and pos==offset and type(size) is int and 1<=size<=MAX_LINE and hash_valid(h) and type(cp) is bool)
        offset+=size; a.require(offset<=MAX_TOTAL)
    a.require(entries[0][3]); return entries


def seek(fp,index,expected,target):
    entries=validate_index(index,expected); a.require(type(target) is int and 0<=target<len(entries))
    start=max(i for i in range(target+1) if entries[i][3]); fp.seek(entries[start][0])
    result=verify(fp,entries[target][2],start=start,count=target-start+1)
    a.require(fp.tell()==entries[target][0]+entries[target][1])
    return dict(start=start,target=target,**result)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('file',type=Path); p.add_argument('--expect',required=True); p.add_argument('--index',type=Path); p.add_argument('--target',type=int); args=p.parse_args()
    try:
        with args.file.open('rb') as fp:
            a.require((args.index is None)==(args.target is None))
            result=verify(fp,args.expect) if args.index is None else seek(fp,a.load(args.index),args.expect,args.target)
        print(json.dumps(result,sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError) as e: p.exit(1,'rejected: '+str(e)+'\n')
