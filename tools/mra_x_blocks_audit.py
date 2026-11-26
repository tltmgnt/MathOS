"""Matched file retrieval: compressed blocks, raw compact and gzip full certificates."""
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
from pathlib import Path
import mra_x_blocks as b
import mra_x_archive as a
import mra_x_compact as c
import mra_x_kernel as k
import mra_x_indexed as idx
import mra_x_arbitrate as arb
import mra_x_topology as ref
import mra_x_separator as sep
import mra_x_portable as portable


def streams():
    for i,kind in enumerate(('chain','cycle','triangles')):
        for n in (12,48):
            d,fs=sep.instance(27100+i*100+n,n,kind); inputs={str(j):f for j,f in enumerate(fs)}
            e=idx.Indexed(d,ref.min_fill(d,fs)); docs=[portable.export(e,e.update(inputs)['result'])]
            v=e.order[0]; f=inputs['0']; tab=dict(f[1]); row=next(iter(tab)); tab[row]+=2
            for edits in ({'0':(f[0],tab)},{'0':f},{},{'test':((v,),{})},{'test':None}): docs.append(portable.export(e,e.update(edits)['result']))
            nd=dict(d); nd[v]+=1; e,r=arb.transfer(e,nd,inputs,ref.min_fill(nd,fs)); docs.append(portable.export(e,r['result'])); docs.append(portable.export(e,e.update({})['result']))
            e,r=arb.transfer(e,d,inputs,ref.min_fill(d,fs)); docs.append(portable.export(e,r['result']))
            for edits in ({'duplicate':f},{'duplicate':None},{}): docs.append(portable.export(e,e.update(edits)['result']))
            yield f'{kind}-{n}',docs


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]; controls=0
    for i,(name,docs) in enumerate(streams()):
        # Profile is supplied, not inferred from the eventual test requests.
        demand=[1]*12 if i%2==0 else [1]*8+[8]*4; queries=3 if i%2==0 else 30
        chosen,(data,index),scores=b.select(docs,demand,queries); expected=a.digest(index)
        raw,rawindex=c.encode(docs,8); fixed,fixedindex=b.encode(docs,8)
        hashes=[k.digest(doc) for doc in docs]; full=gzip.compress(b''.join(a.canonical(doc)+b'\n' for doc in docs),mtime=0)
        enc={'adaptive':(data,index),'fixed8':(fixed,fixedindex),'raw8':(raw,rawindex),'gzip_full':(full,{'targets':hashes})}; paths={}; anchors={}
        for label,(payload,manifest) in enc.items():
            path=root/f'{name}-{label}.bin'; ip=root/f'{name}-{label}.json'; path.write_bytes(payload); ip.write_bytes(a.canonical(manifest)); paths[label]=(path,ip); anchors[label]=a.digest(manifest)
        def retrieve(label,target):
            path,ip=paths[label]; manifest=a.load(ip); anchor=anchors[label]
            with path.open('rb') as fp:
                if label=='raw8': return c.seek(fp,manifest,anchor,target)
                if label!='gzip_full': return b.seek(fp,manifest,anchor,target)
                a.require(a.digest(manifest)==anchor)
                with gzip.GzipFile(fileobj=fp) as gz:
                    for j in range(target+1): doc,size=c.read(gz); a.require(size>0)
                a.require(k.digest(doc)==manifest['targets'][target]); return dict(states=[k.check(doc)])
        baseline=[k.check(doc) for doc in docs]
        for target in range(12):
            for label in enc:
                x=retrieve(label,target)['states'][-1]; y=baseline[target]; a.require(all(x[key]==y[key] for key in ('problem_sha256','optimum','variables','visits')))
        rng=random.Random(27700+i); targets=rng.choices(range(12),weights=demand,k=12)
        metrics={label:dict(records=0,fresh=0,compressed_read=0) for label in enc}
        for target in targets:
            for label in enc:
                r=retrieve(label,target); metrics[label]['records']+=len(r['states']); metrics[label]['fresh']+=sum(x.get('fresh',x['visits']) for x in r['states']); metrics[label]['compressed_read']+=r.get('compressed_read',0)
        times={key:[] for key in enc}
        for rep in range(3):
            labels=list(enc); random.Random(i*19+rep).shuffle(labels)
            for label in labels:
                start=time.perf_counter_ns()
                for target in targets: retrieve(label,target)
                times[label].append(time.perf_counter_ns()-start)
        timings.append(dict(name=name,ns=times))
        proc=subprocess.run([sys.executable,'-S',str(Path(b.__file__).resolve()),str(paths['adaptive'][0]),str(paths['adaptive'][1]),'--expect',expected,'--target','11'],capture_output=True,text=True,timeout=20)
        a.require(proc.returncode==0 and json.loads(proc.stdout)==retrieve('adaptive',11))
        rows.append(dict(name=name,states=len(docs),feasible=sum(x['optimum'] is not None for x in baseline),chosen=chosen,profile=demand,expected_queries=queries,scores=scores,targets=targets,storage={key:sum(p.stat().st_size for p in paths[key]) for key in enc},metrics=metrics,anchors=anchors))
    docs=next(streams())[1]; data,index=b.encode(docs,4); h=a.digest(index)
    def reject(fn):
        nonlocal controls
        try: fn()
        except (ValueError,b.zlib.error): controls+=1
        else: raise ValueError('accepted corrupt block')
    reject(lambda:b.seek(io.BytesIO(data),index,'0'*64,0)); reject(lambda:b.seek(io.BytesIO(data),index,h,True)); reject(lambda:b.seek(io.BytesIO(data),index,h,12)); reject(lambda:b.seek(io.BytesIO(data[:-1]),index,h,11)); reject(lambda:b.seek(io.BytesIO(bytes([data[0]^1])+data[1:]),index,h,0))
    for field,value in [(2,1),(4,1),(0,1),(5,'0'*64)]:
        bad=copy.deepcopy(index); bad['blocks'][0][field]=value; reject(lambda:b.seek(io.BytesIO(data),bad,a.digest(bad),0))
    reject(lambda:b.decompress(b.zlib.compress(b'x'*100),1)); reject(lambda:b.decompress(b.zlib.compress(b'x')+b'extra',1)); reject(lambda:b.decompress(b.zlib.compress(b'x')[:-1],1))
    reject(lambda:b.select(docs,[0]*12,1)); reject(lambda:b.select(docs,[1]*12,-1))
    out=dict(rows=rows,controls=controls,timings=timings,scope='synthetic supplied demand; separate sampled requests; warm local file opens and index parsing included; no cold-cache or RSS claim; gzip full verifies target only; trusted manifest anchor required')
    out['evidence_sha256']=a.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); r=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(r)); print(json.dumps(dict(controls=r['controls'],streams=len(r['rows']),chosen=[x['chosen'] for x in r['rows']]),indent=2))
