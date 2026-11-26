"""Phase XXVII: bounded compressed checkpoint blocks and demand-based selection."""
import argparse
import hashlib
import io
import json
import zlib
from pathlib import Path
import mra_x_archive as a
import mra_x_compact as c

INTERVALS=(1,2,4,8,16)
MAX_BLOCK=16_000_000


def encode(docs,interval):
    a.require(type(interval) is int and interval in INTERVALS)
    raw,index=c.encode(docs,interval); entries=index['entries']; blocks=[]; chunks=[]; offset=0
    for start in range(0,len(entries),interval):
        stop=min(start+interval,len(entries)); lo=entries[start][0]; hi=entries[stop-1][0]+entries[stop-1][1]
        data=raw[lo:hi]; compressed=zlib.compress(data,6)
        a.require(len(data)<=MAX_BLOCK and len(compressed)<=MAX_BLOCK)
        blocks.append([start,stop,offset,len(compressed),len(data),hashlib.sha256(compressed).hexdigest()])
        chunks.append(compressed); offset+=len(compressed)
    a.require(offset<=c.MAX_TOTAL)
    return b''.join(chunks),dict(schema=1,interval=interval,blocks=blocks,targets=[e[2] for e in entries])


def validate(index,anchor):
    a.require(c.hash_valid(anchor) and a.digest(index)==anchor)
    a.fields(index,'schema interval blocks targets'); n=index['interval']; blocks=index['blocks']; targets=index['targets']
    a.require(type(index['schema']) is int and index['schema']==1 and type(n) is int and n in INTERVALS)
    a.require(type(targets) is list and 1<=len(targets)<=a.MAX_STATES and all(c.hash_valid(h) for h in targets))
    a.require(type(blocks) is list and len(blocks)==(len(targets)+n-1)//n)
    offset=0
    for i,b in enumerate(blocks):
        a.require(type(b) is list and len(b)==6); start,stop,pos,size,raw,h=b
        a.require(all(type(x) is int for x in b[:5]) and start==i*n and stop==min(start+n,len(targets)) and pos==offset and 1<=size<=MAX_BLOCK and 1<=raw<=MAX_BLOCK and c.hash_valid(h))
        offset+=size; a.require(offset<=c.MAX_TOTAL)
    return blocks,targets


def decompress(data,size):
    a.require(type(size) is int and 1<=size<=MAX_BLOCK)
    d=zlib.decompressobj(); raw=d.decompress(data,size+1)
    a.require(len(raw)==size and d.eof and not d.unused_data and not d.unconsumed_tail)
    return raw


def seek(fp,index,anchor,target):
    blocks,targets=validate(index,anchor); a.require(type(target) is int and 0<=target<len(targets))
    start,stop,pos,size,raw_size,h=blocks[target//index['interval']]
    fp.seek(pos); data=fp.read(size); a.require(len(data)==size and hashlib.sha256(data).hexdigest()==h)
    raw=decompress(data,raw_size)
    r=c.verify(io.BytesIO(raw),targets[target],start=start,count=target-start+1)
    return dict(start=start,target=target,compressed_read=size,decompressed_bytes=len(raw),**r)


def select(docs,demand,queries):
    """Minimize stored bytes plus projected compressed bytes read, not runtime."""
    a.require(len(demand)==len(docs) and all(type(x) is int and x>=0 for x in demand) and sum(demand)>0)
    a.require(type(queries) is int and 0<=queries<=10000)
    candidates=[]; encodings={}; mass=sum(demand)
    for interval in INTERVALS:
        raw,index=encode(docs,interval); stored=len(raw)+len(a.canonical(index))
        weighted=sum(demand[t]*index['blocks'][t//interval][3] for t in range(len(docs)))
        score=mass*stored+queries*weighted
        candidates.append(dict(interval=interval,stored=stored,weighted_read=weighted,score=score)); encodings[interval]=(raw,index)
    best=min(candidates,key=lambda x:(x['score'],x['interval']))['interval']
    return best,encodings[best],candidates


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('file',type=Path); p.add_argument('index',type=Path); p.add_argument('--expect',required=True); p.add_argument('--target',required=True,type=int); args=p.parse_args()
    try:
        with args.file.open('rb') as f: print(json.dumps(seek(f,a.load(args.index),args.expect,args.target),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError,zlib.error) as e: p.exit(1,'rejected: '+str(e)+'\n')
