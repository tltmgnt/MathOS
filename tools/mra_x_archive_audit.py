"""Generate new archive streams and compare with Phase XXIII full verification."""
import argparse
import copy
import gzip
import json
import math
import random
import statistics as st
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
import mra_x_archive as a
import mra_x_kernel as k
import mra_x_portable as portable
import mra_x_indexed as idx
import mra_x_arbitrate as arb
import mra_x_topology as ref
import mra_x_separator as sep


def streams():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (8,32,64,128):
            d,fs=sep.instance(24100+i*100+n,n,kind); e=idx.Indexed(d,ref.min_fill(d,fs)); inputs={str(j):f for j,f in enumerate(fs)}
            docs=[portable.export(e,e.update(inputs)['result'])]
            v=e.order[0]; f=inputs['0']; table=dict(f[1]); row=next(iter(table)); table[row]+=3
            for edits in ({'0':(f[0],table)},{'0':f},{}, {'test':((v,),{})},{'test':None}): docs.append(portable.export(e,e.update(edits)['result']))
            nd=dict(d); nd[v]=d[v]+1; e,r=arb.transfer(e,nd,inputs,ref.min_fill(nd,fs)); docs.append(portable.export(e,r['result']))
            docs.append(portable.export(e,e.update({})['result']))
            yield f'{kind}-{n}',docs


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; controls=0
    for i,(name,docs) in enumerate(streams()):
        archive=a.pack(docs); raw=a.canonical(archive); full=a.canonical(docs); path=root/(name+'.json'); path.write_bytes(raw)
        result=a.check(archive,a.digest(archive)); baseline=[k.check(d,k.digest(d['problem'])) for d in docs]
        for x,y in zip(result['states'],baseline): a.require(all(x[key]==y[key] for key in ('problem_sha256','optimum','variables','visits')))
        p=subprocess.run([sys.executable,'-I','-S',str(Path(a.__file__).resolve()),str(path),'--expect-archive',a.digest(archive)],capture_output=True,text=True,timeout=20); a.require(p.returncode==0 and json.loads(p.stdout)==result)
        rows.append(dict(name=name,states=len(docs),objects=len(archive['objects']),references=sum(len(s['factors'])+len(s['proofs']) for s in archive['states']),raw_bytes=len(raw),full_bytes=len(full),gzip_archive=len(gzip.compress(raw,mtime=0)),gzip_full=len(gzip.compress(full,mtime=0)),full_visits=sum(x['visits'] for x in baseline),fresh_visits=sum(x['fresh'] for x in result['states']),full_lookups=sum(x['lookups'] for x in baseline),archive_lookups=sum(x['lookups'] for x in result['states']),hits=sum(x['hits'] for x in result['states']),buckets=sum(x['variables'] for x in result['states']),feasible=sum(x['optimum'] is not None for x in result['states'])))
        def full_check(): return [k.check(d) for d in json.loads(full)]
        def archive_check(): return a.check(json.loads(raw))
        funcs={'full':full_check,'archive':archive_check}; times={key:[] for key in funcs}; memory={}
        for j in range(5):
            order=list(funcs); random.Random(i*17+j).shuffle(order)
            for key in order:
                start=time.perf_counter_ns(); funcs[key](); times[key].append(time.perf_counter_ns()-start)
        for key,fn in funcs.items():
            tracemalloc.start(); fn(); memory[key]=tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        timings.append(dict(name=name,ns=times,peak_traced_bytes=memory))
    e=idx.Indexed({'a':2,'b':2},['a','b']); r=e.update({'f':(('a','b'),{(0,0):0,(1,0):0,(1,1):2})})['result']; doc=portable.export(e,r); good=a.pack([doc,doc]); a.require(a.check(good)['states'][1]['hits']==2)
    def reject(x,expected=None):
        nonlocal controls
        try: a.check(x,expected)
        except ValueError: controls+=1
        else: raise ValueError('invalid archive accepted')
    reject(good,'0'*64)
    bad=copy.deepcopy(good); bad['objects'][0][0]='0'*64; reject(bad)
    bad=copy.deepcopy(good); bad['states'][1]['proofs'][0]=True; reject(bad)
    bad=copy.deepcopy(good); bad['states'][1]['proofs'][0]=len(bad['objects']); reject(bad)
    bad=copy.deepcopy(good); bad['objects'].append(bad['objects'][0]); reject(bad)
    bad=copy.deepcopy(good); bad['objects'].append([a.digest([]),[]]); reject(bad)
    # Rehash altered objects with internally consistent manifests; hashes cannot authorize invalid math.
    for mode in ('cost','tie','missing','domain','factor','witness','count'):
        bad=copy.deepcopy(doc)
        if mode=='cost': bad['messages'][0][1][0][1]+=1
        if mode=='tie': bad['result']['trace'][0][2][0][1]=1
        if mode=='missing': bad['messages'][0][1].pop(); bad['result']['trace'][0][2].pop()
        if mode=='domain': bad['problem']['domains']['a']=1
        if mode=='factor': bad['problem']['factors'][0][1][0][1]+=1
        if mode=='witness': bad['result']['witness']['a']=1
        if mode=='count': bad['result']['assignments_evaluated']+=1
        reject(a.pack([doc,bad]))
    # Exact multiset, not set: a duplicate factor must invalidate old receipt.
    bad=copy.deepcopy(doc); bad['problem']['factors']*=2; reject(a.pack([doc,bad]))
    reject(a.pack([doc]*129))
    for raw in (b'{"schema":1,"schema":1}',b' '* (a.MAX_BYTES+1)):
        path=root/'bad.json'; path.write_bytes(raw)
        try: a.load(path)
        except ValueError: controls+=1
        else: raise ValueError('invalid file accepted')
        path.unlink()
    # Deliberately lower the work limits to exercise refusal without huge allocations.
    for key,value in (('MAX_VISITS',1),('MAX_LOOKUPS',1),('MAX_ARCHIVE_VISITS',8)):
        old=getattr(a,key); setattr(a,key,value)
        try: reject(good)
        finally: setattr(a,key,old)
    ratios=[st.median(x['ns']['archive'])/st.median(x['ns']['full']) for x in timings]
    out=dict(rows=rows,controls=controls,timings=timings,geomean_ratio=math.exp(st.mean(map(math.log,ratios))),worst_ratio=max(ratios),scope='new synthetic streams; full archive replay from untrusted storage; exact receipts only within replay; timings include JSON decode and verification, exclude I/O and generation; traced memory not RSS')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps(dict(controls=r['controls'],geomean_ratio=r['geomean_ratio'],worst_ratio=r['worst_ratio'],**{key:sum(x[key] for x in r['rows']) for key in r['rows'][0] if key!='name'}),indent=2))
