"""Phase XXVIII: unified proof representation and standalone retrieval dispatcher."""
import argparse
import hashlib
import io
import json
import zlib
from pathlib import Path
import mra_x_archive as a
import mra_x_blocks as b
import mra_x_compact as c
import mra_x_kernel as k

MAX_HISTORY=16
MAX_READS=1000000
FORMATS=('gzip','archive','raw8','block1','block2','block4','block8','block16')


def package(versions,docs,kind):
    a.require(kind in FORMATS and 1<=len(docs)==len(versions)<=MAX_HISTORY)
    visits=[d['result']['assignments_evaluated'] for d in docs]
    a.require(all(len(a.canonical(d))+1<=c.MAX_LINE for d in docs))
    if kind=='gzip':
        raw=b''.join(a.canonical(d)+b'\n' for d in docs); a.require(len(raw)<=b.MAX_BLOCK)
        data=zlib.compress(raw,6,wbits=31); index=dict(size=len(data),raw=len(raw),sha256=hashlib.sha256(data).hexdigest(),targets=[k.digest(d) for d in docs])
    elif kind=='archive':
        a.require(sum(visits)<=a.MAX_ARCHIVE_VISITS)
        data=a.canonical(a.pack(docs)); a.require(len(data)<=a.MAX_BYTES); index=dict(size=len(data),sha256=hashlib.sha256(data).hexdigest())
    else:
        n=8 if kind=='raw8' else int(kind[5:])
        a.require(all(sum(visits[i:i+n])<=a.MAX_ARCHIVE_VISITS for i in range(0,len(visits),n)))
        raw,check=c.encode(docs,n); a.require(all(x[1]<=c.MAX_LINE for x in check['entries']))
        if kind=='raw8': data,index=raw,check
        else: data,index=b.encode(docs,n)
    manifest=dict(schema=1,kind=kind,versions=versions,index=index)
    a.require(len(data)<=c.MAX_TOTAL and len(a.canonical(manifest))<=a.MAX_BYTES)
    return data,manifest


def retrieve(fp,manifest,anchor,version):
    a.require(c.hash_valid(anchor) and a.digest(manifest)==anchor); a.fields(manifest,'schema kind versions index')
    kind=manifest['kind']; versions=manifest['versions']; index=manifest['index']
    a.require(type(manifest['schema']) is int and manifest['schema']==1 and kind in FORMATS and type(versions) is list and 1<=len(versions)<=MAX_HISTORY and all(type(v) is int and v>=0 for v in versions) and all(y==x+1 for x,y in zip(versions,versions[1:])))
    a.require(type(version) is int and version in versions); target=versions.index(version); fp.seek(0)
    if kind=='raw8':
        a.require(len(index['entries'])==len(versions)); r=c.seek(fp,index,a.digest(index),target); receipt=r['states'][-1]; read=r['bytes']; work=sum(x['fresh'] for x in r['states']); records=len(r['states'])
    elif kind.startswith('block'):
        a.require(index['interval']==int(kind[5:]) and len(index['targets'])==len(versions)); r=b.seek(fp,index,a.digest(index),target); receipt=r['states'][-1]; read=r['compressed_read']; work=sum(x['fresh'] for x in r['states']); records=len(r['states'])
    else:
        a.fields(index,'size sha256' if kind=='archive' else 'size raw sha256 targets'); size=index['size']; a.require(type(size) is int and 1<=size<=b.MAX_BLOCK)
        data=fp.read(size); a.require(len(data)==size and hashlib.sha256(data).hexdigest()==index['sha256']); read=size
        if kind=='archive':
            r=a.check(json.loads(data,object_pairs_hook=a.unique)); a.require(len(r['states'])==len(versions)); receipt=r['states'][target]; work=sum(x['fresh'] for x in r['states']); records=len(r['states'])
        else:
            limit=index['raw']; a.require(type(limit) is int and 1<=limit<=b.MAX_BLOCK and len(index['targets'])==len(versions))
            z=zlib.decompressobj(31); raw=z.decompress(data,limit+1); a.require(len(raw)==limit and z.eof and not z.unused_data and not z.unconsumed_tail)
            stream=io.BytesIO(raw)
            for _ in range(target+1): doc,size=c.read(stream); a.require(size>0)
            a.require(k.digest(doc)==index['targets'][target]); receipt=k.check(doc); work=receipt['visits']; records=1
    return dict(version=version,receipt={key:receipt[key] for key in ('problem_sha256','optimum','variables','visits')},fresh=work,records=records,payload_read=read)


def select(versions,docs,demand,queries):
    a.require(len(demand)==len(docs) and all(type(x) is int and 1<=x<=MAX_READS+1 for x in demand) and type(queries) is int and 0<=queries<=10000)
    mass=sum(demand); candidates=[]; best=None; chosen=None; visits=[d['result']['assignments_evaluated'] for d in docs]
    for kind in FORMATS:
        try: data,m=package(versions,docs,kind)
        except ValueError: continue
        index=m['index']; overhead=len(a.canonical(m)); stored=len(data)+overhead; weighted=0
        for i,w in enumerate(demand):
            if kind=='gzip': read=len(data); work=visits[i]
            elif kind=='archive': read=len(data); work=sum(visits)
            elif kind=='raw8':
                lo=i//8*8; entries=index['entries']; read=sum(x[1] for x in entries[lo:i+1]); work=sum(visits[lo:i+1])
            else:
                n=index['interval']; lo=i//n*n; read=index['blocks'][i//n][3]; work=sum(visits[lo:i+1])
            weighted+=w*(read+overhead+4*work)
        score=mass*stored+queries*weighted; candidates.append(dict(kind=kind,stored=stored,weighted=weighted,score=score))
        if best is None or score<best: best=score; chosen=(data,m)
    a.require(chosen is not None); return chosen,candidates


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('file',type=Path); p.add_argument('manifest',type=Path); p.add_argument('--expect',required=True); p.add_argument('--version',type=int,required=True); args=p.parse_args()
    try:
        with args.file.open('rb') as fp: print(json.dumps(retrieve(fp,a.load(args.manifest),args.expect,args.version),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError,OSError,zlib.error) as e: p.exit(1,'rejected: '+str(e)+'\n')
