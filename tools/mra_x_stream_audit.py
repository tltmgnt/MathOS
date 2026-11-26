"""Matched streaming proof benchmarks and checkpoint controls."""
import argparse
import copy
import gzip
import io
import json
import random
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
import mra_x_stream as s
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_archive_audit as previous


def lines(records): return b''.join(a.canonical(r)+b'\n' for r in records)


def full(fp):
    out=[]
    while True:
        doc,size=s.read_line(fp)
        if not size: break
        out.append(k.check(doc))
    return out


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; times=[]; controls=0; anchors={}
    for i,(name,source) in enumerate(previous.streams()):
        if name.endswith(('-64','-128')): continue
        docs=source*2  # matched 16-state history; repeated motifs, not independent cases
        records=list(s.records(docs,interval=4)); raw=lines(records); terminal=records[-1]['sha256']; plain=lines(docs); archive=a.canonical(a.pack(docs)); zg=gzip.compress(raw,mtime=0); zp=gzip.compress(plain,mtime=0)
        (root/(name+'.ndjson')).write_bytes(raw); anchors[name]=dict(terminal=terminal,checkpoints={str(r['payload']['index']):r['sha256'] for r in records if r['payload']['checkpoint']})
        result=s.verify(io.BytesIO(raw),terminal); base=full(io.BytesIO(plain)); old=a.check(json.loads(archive))
        for x,y,z in zip(result['states'],base,old['states']): a.require(all(x[key]==y[key]==z[key] for key in ('problem_sha256','optimum','variables','visits')) and x==z)
        checkpoints=0
        for j,r in enumerate(records):
            if r['payload']['checkpoint']:
                q=s.verify(io.BytesIO(lines([r])),r['sha256'],checkpoint=True)['states'][0]; a.require(q['hits']==0 and q['fresh']==q['visits'] and all(q[key]==base[j][key] for key in ('problem_sha256','optimum','variables','visits'))); checkpoints+=1
        p=subprocess.run([sys.executable,'-S',str(Path(s.__file__).resolve()),str(root/(name+'.ndjson')),'--expect',terminal],capture_output=True,text=True,timeout=30); a.require(p.returncode==0 and json.loads(p.stdout)==result)
        funcs={'stream':lambda:s.verify(io.BytesIO(raw),terminal),'full':lambda:full(io.BytesIO(plain)),'archive':lambda:a.check(json.loads(archive)),'gzip_stream':lambda:s.verify(gzip.GzipFile(fileobj=io.BytesIO(zg)),terminal),'gzip_full':lambda:full(gzip.GzipFile(fileobj=io.BytesIO(zp)))}
        timings={key:[] for key in funcs}; memory={}
        for j in range(2):
            labels=list(funcs); random.Random(i*19+j).shuffle(labels)
            for key in labels:
                start=time.perf_counter_ns(); funcs[key](); timings[key].append(time.perf_counter_ns()-start)
        for key,fn in funcs.items():
            tracemalloc.start(); fn(); memory[key]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        times.append(dict(name=name,ns=timings,peak_traced_bytes=memory))
        rows.append(dict(name=name,states=len(docs),checkpoints=checkpoints,feasible=sum(x['optimum'] is not None for x in base),full_visits=sum(x['visits'] for x in base),fresh_visits=sum(x['fresh'] for x in result['states']),hits=sum(x['hits'] for x in result['states']),buckets=sum(x['variables'] for x in base),peak_objects=result['peak_objects'],archive_objects=len(json.loads(archive)['objects']),stream_bytes=len(raw),full_bytes=len(plain),archive_bytes=len(archive),gzip_stream_bytes=len(zg),gzip_full_bytes=len(zp),gzip_archive_bytes=len(gzip.compress(archive,mtime=0))))
    (root/'anchors.json').write_bytes(a.canonical(anchors))
    doc=next(previous.streams())[1][0]; rec=list(s.records([doc]*3)); good=lines(rec); terminal=rec[-1]['sha256']; a.require(s.verify(io.BytesIO(good),terminal)['states'][-1]['hits']==len(doc['problem']['domains']))
    def reject(raw,expected=terminal,checkpoint=False):
        nonlocal controls
        try: s.verify(io.BytesIO(raw),expected,checkpoint=checkpoint)
        except ValueError: controls+=1
        else: raise ValueError('invalid stream accepted')
    reject(good,'0'*64); reject(lines(rec[:-1])); reject(lines(rec[1:])); reject(lines([rec[0],rec[2],rec[1]])); reject(good[:-1]); reject(good+b'{"x":1,"x":2}\n'); reject(lines([rec[1]]),rec[1]['sha256'],True)
    bad=copy.deepcopy(rec); bad[1]['payload']['state']['result']['optimum']=123456
    for j in (1,2): bad[j]['payload']['previous']=bad[j-1]['sha256']; bad[j]['sha256']=a.digest(bad[j]['payload'])
    reject(lines(bad),bad[-1]['sha256'])
    bad=copy.deepcopy(rec); bad[1]['payload']['objects']={'0'*64:[]}; bad[1]['sha256']=a.digest(bad[1]['payload']); reject(lines(bad[:2]),bad[1]['sha256'])
    for key,limit in (('MAX_LINE',8),('MAX_TOTAL',8),('MAX_LIVE',1)):
        old=getattr(s,key); setattr(s,key,limit)
        try: reject(good)
        finally: setattr(s,key,old)
    out=dict(rows=rows,controls=controls,timings=times,scope='matched resident byte streams; gzip decode included, disk I/O and generation excluded; peak traced allocation not RSS; repeated Phase XXIV motifs; trusted terminal/checkpoint anchors required; no authenticated storage or program proof')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps(dict(controls=r['controls'],**{key:sum(x[key] for x in r['rows']) for key in r['rows'][0] if key!='name'}),indent=2))
