"""Matched compact-wire and indexed replay experiments."""
import argparse
import copy
import gzip
import io
import json
import random
import statistics as st
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
import mra_x_compact as c
import mra_x_archive as a
import mra_x_stream as s
import mra_x_stream_audit as old
import mra_x_indexed as idx
import mra_x_arbitrate as arb
import mra_x_topology as ref
import mra_x_separator as sep
import mra_x_portable as portable


def streams():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,64):
            d,fs=sep.instance(26100+i*100+n,n,kind); inputs={str(j):f for j,f in enumerate(fs)}
            e=idx.Indexed(d,ref.min_fill(d,fs)); docs=[portable.export(e,e.update(inputs)['result'])]
            v=e.order[0]; f=inputs['0']; tab=dict(f[1]); row=next(iter(tab)); tab[row]+=2
            for edits in ({'0':(f[0],tab)},{'0':f},{},{'test':((v,),{})},{'test':None}): docs.append(portable.export(e,e.update(edits)['result']))
            nd=dict(d); nd[v]+=1; e,r=arb.transfer(e,nd,inputs,ref.min_fill(nd,fs)); docs.append(portable.export(e,r['result'])); docs.append(portable.export(e,e.update({})['result']))
            e,r=arb.transfer(e,d,inputs,ref.min_fill(d,fs)); docs.append(portable.export(e,r['result']))
            for edits in ({'duplicate':f},{'duplicate':None},{}): docs.append(portable.export(e,e.update(edits)['result']))
            yield f'{kind}-{n}',docs


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; controls=0; anchors={}
    for i,(name,docs) in enumerate(streams()):
        raw,index=c.encode(docs); h=a.digest(index); terminal=index['entries'][-1][2]; path=root/(name+'.ndjson'); path.write_bytes(raw); ip=root/(name+'.index.json'); ib=a.canonical(index); ip.write_bytes(ib); anchors[name]=dict(index=h,terminal=terminal)
        base=old.lines(docs); archive=a.canonical(a.pack(docs)); legacy=list(s.records(docs,interval=8)); legacyraw=old.lines(legacy); legacyend=legacy[-1]['sha256']
        result=c.verify(io.BytesIO(raw),terminal); b=old.full(io.BytesIO(base)); p=a.check(json.loads(archive)); q=s.verify(io.BytesIO(legacyraw),legacyend)
        a.require(len(result['states'])==len(b)==len(p['states'])==len(q['states']))
        for x,y,z,w in zip(result['states'],b,p['states'],q['states']):
            a.require(x==z==w and all(x[key]==y[key] for key in ('problem_sha256','optimum','variables','visits')))
        seek_states=seek_visits=prefix_visits=0
        for target in range(len(docs)):
            r=c.seek(io.BytesIO(raw),index,h,target); x=r['states'][-1]; y=b[target]
            a.require(all(x[key]==y[key] for key in ('problem_sha256','optimum','variables','visits')))
            seek_states+=len(r['states']); seek_visits+=sum(x['fresh'] for x in r['states']); prefix_visits+=sum(x['fresh'] for x in result['states'][:target+1])
        proc=subprocess.run([sys.executable,'-S',str(Path(c.__file__).resolve()),str(path),'--expect',h,'--index',str(ip),'--target','11'],capture_output=True,text=True,timeout=20); a.require(proc.returncode==0 and json.loads(proc.stdout)==c.seek(io.BytesIO(raw),index,h,11))
        gz={key:gzip.compress(value,mtime=0) for key,value in [('compact',raw),('legacy',legacyraw),('full',base),('archive',archive)]}
        funcs={'compact':lambda:c.verify(io.BytesIO(raw),terminal),'legacy':lambda:s.verify(io.BytesIO(legacyraw),legacyend),'full':lambda:old.full(io.BytesIO(base)),'archive':lambda:a.check(json.loads(archive)),'gzip_compact':lambda:c.verify(gzip.GzipFile(fileobj=io.BytesIO(gz['compact'])),terminal),'gzip_full':lambda:old.full(gzip.GzipFile(fileobj=io.BytesIO(gz['full'])))}
        times={key:[] for key in funcs}; memory={}
        for j in range(3):
            keys=list(funcs); random.Random(i*19+j).shuffle(keys)
            for key in keys:
                start=time.perf_counter_ns(); funcs[key](); times[key].append(time.perf_counter_ns()-start)
        for key,fn in funcs.items():
            tracemalloc.start(); fn(); memory[key]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        timings.append(dict(name=name,ns=times,peak_traced_bytes=memory))
        rows.append(dict(name=name,states=len(docs),feasible=sum(x['optimum'] is not None for x in b),full_visits=sum(x['visits'] for x in b),fresh_visits=sum(x['fresh'] for x in result['states']),hits=sum(x['hits'] for x in result['states']),buckets=sum(x['variables'] for x in b),seek_states=seek_states,seek_visits=seek_visits,prefix_visits=prefix_visits,peak_slots=result['peak_slots'],index_bytes=len(ib),compact_bytes=len(raw),legacy_bytes=len(legacyraw),archive_bytes=len(archive),full_bytes=len(base),gzip_compact=len(gz['compact']),gzip_legacy=len(gz['legacy']),gzip_full=len(gz['full']),gzip_archive=len(gz['archive']),interval4_bytes=len(c.encode(docs,4)[0])))
    (root/'anchors.json').write_bytes(a.canonical(anchors))
    docs=next(streams())[1]; raw,index=c.encode(docs); h=a.digest(index); terminal=index['entries'][-1][2]
    def reject(fn):
        nonlocal controls
        try: fn()
        except ValueError: controls+=1
        else: raise ValueError('invalid compact stream accepted')
    reject(lambda:c.verify(io.BytesIO(raw),'0'*64)); reject(lambda:c.verify(io.BytesIO(raw[:-1]),terminal)); reject(lambda:c.seek(io.BytesIO(raw),index,'0'*64,11)); reject(lambda:c.seek(io.BytesIO(raw),index,h,True)); reject(lambda:c.seek(io.BytesIO(raw),index,h,12))
    bad=copy.deepcopy(index); bad['entries'][8][0]+=1; reject(lambda:c.seek(io.BytesIO(raw),bad,a.digest(bad),11))
    bad=copy.deepcopy(index); bad['entries'][11][2]='0'*64; reject(lambda:c.seek(io.BytesIO(raw),bad,a.digest(bad),11))
    rec=list(c.records(docs)); bad=copy.deepcopy(rec[0]); bad['payload']['objects'][0]=0; bad['sha256']=a.digest(bad['payload']); reject(lambda:c.verify(io.BytesIO(old.lines([bad])),bad['sha256']))
    bad=copy.deepcopy(rec[0]); bad['payload']['state']['result']['optimum']=999999; bad['sha256']=a.digest(bad['payload']); reject(lambda:c.verify(io.BytesIO(old.lines([bad])),bad['sha256']))
    bad=copy.deepcopy(rec[0]); bad['payload']['state']['factors'][0]=True; bad['sha256']=a.digest(bad['payload']); reject(lambda:c.verify(io.BytesIO(old.lines([bad])),bad['sha256']))
    reject(lambda:c.verify(io.BytesIO(old.lines([rec[1],rec[0]])),rec[0]['sha256']))
    reject(lambda:c.verify(io.BytesIO(raw+b'{"x":1,"x":2}\n'),terminal))
    for key,limit in [('MAX_LINE',8),('MAX_TOTAL',8),('MAX_LIVE',1)]:
        prev=getattr(c,key); setattr(c,key,limit)
        try: reject(lambda:c.verify(io.BytesIO(raw),terminal))
        finally: setattr(c,key,prev)
    out=dict(rows=rows,controls=controls,timings=timings,scope='synthetic new seeds; matched resident bytes; index anchor required for seek; no authentication; traced allocations not RSS; no formal proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps(dict(controls=r['controls'],**{key:sum(x[key] for x in r['rows']) for key in r['rows'][0] if key!='name'}),indent=2))
