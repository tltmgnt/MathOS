"""Phase XL: diverse deterministic release audit, independent exact component oracle.
Optional SciPy/HiGHS comparison; not a claim of independent third-party replication.
"""
import argparse
import copy
import itertools
import json
import math
import random
import sqlite3
import statistics as st
import subprocess
import sys
import time
from pathlib import Path
import mra_x_archive as a
import mra_x_system as u
import mra_x_service as s
import mra_x_routed as r
import mra_x_kernel as k
import mra_x_state as state


def oracle(d,fs,limit=250000):
    # Independent exhaustive optimization on connected components of ORIGINAL factors.
    # No elimination, projection, messages, or imported solver scoring routine.
    remaining=set(d); groups=[]; total=0; visits=0
    for scope,tab in fs:
        if not scope:
            if () not in tab: return None,0
            total+=tab[()]
    while remaining:
        group={min(remaining)}
        while True:
            enlarged=group|{v for scope,_ in fs if group.intersection(scope) for v in scope}
            if enlarged==group: break
            group=enlarged
        remaining-=group; groups.append(sorted(group))
    for group in groups:
        work=math.prod(d[v] for v in group)
        if visits+work>limit: return 'SKIP',visits
        visits+=work; terms=[(tuple(group.index(v) for v in scope),tab) for scope,tab in fs if scope and scope[0] in group]
        best=None
        for row in itertools.product(*(range(d[v]) for v in group)):
            cost=0
            for indices,tab in terms:
                key=tuple(row[i] for i in indices)
                if key not in tab: break
                cost+=tab[key]
            else:
                if best is None or cost<best: best=cost
        if best is None: return None,visits
        total+=best
    return total,visits


def corpus():
    for i,(name,n,block) in enumerate((('empty',0,1),('unary',12,1),('dense5',5,5),('quartets',24,4),('sparse5',35,5),('star',9,9),('grid',12,12),('disconnected',64,4))):
        rng=random.Random(40101+i); vs=[f'v{j:03}' for j in range(n)]; d={v:(rng.randint(1,4) if name!='grid' else 2) for v in vs}; fs={}
        def add(scope):
            tab={row:rng.randint(-9,12) for row in itertools.product(*(range(d[v]) for v in scope)) if rng.random()>(.65 if name=='sparse5' else .2)}; tab[(0,)*len(scope)]=rng.randint(-9,0); fs[str(len(fs))]=(tuple(scope),tab)
        if name=='star':
            for v in vs[:-1]: add([v,vs[-1]])
        elif name=='grid':
            for j,v in enumerate(vs):
                if j%4<3: add([v,vs[j+1]])
                if j+4<n: add([v,vs[j+4]])
        else:
            for j in range(0,n,block):
                g=vs[j:j+block]; add(g)
                if len(g)>1: add(g[::-1][:2])
        fs['constant']=((),{():-2}); first=next(iter(fs)); f=fs[first]; tab=dict(f[1]); tab[next(iter(tab))]+=3
        v=vs[0] if vs else None; edge=((v,'z'),{(0,0):-3}) if v else (('z',),{(0,):-3})
        edits=[(fs,{}),({first:(f[0],tab)},{}),({first:f},{}),({'dup':f},{}),({'dup':None},{}),({'new':edge},{'z':2}),({}, {'z':3}),({'new':None},{'z':None}),({'bad':((),{})},{}),({'bad':None},{}),({'extra_constant':((),{():4})},{}),({'extra_constant':None},{}),({},{}),({},{}),({},{}),({},{}),({},{}),({}, {})]
        yield name,d,edits


class Perf(u.System):
    def __init__(self,path,d=None): super().__init__(path,d,profile='performance')
class Protected(u.System): pass
METHODS={'full':s.Store,'routed':r.Store,'performance':Perf,'protected':Protected}


def inputs_after(d,fs,es,ds):
    for v,n in ds.items():
        if n is None: del d[v]
        else: d[v]=n
    for name,f in es.items():
        if f is None: del fs[name]
        else: fs[name]=f


def run(cls,path,domains,edits,check=False):
    store=cls(path,domains); rows=[]; d=dict(domains); fs={}; exact=0; visits=0
    for j,(es,ds) in enumerate(edits):
        q=store.apply(es,ds)['receipt']; inputs_after(d,fs,es,ds)
        if check:
            value,work=oracle(d,list(fs.values())); a.require(value!='SKIP' and value==q['optimum']); exact+=1; visits+=work
            receipt=store.get(j+1); a.require(all(q[key]==receipt[key] for key in ('optimum','problem_sha256','certificate_sha256','visits')))
        rows.append({key:q[key] for key in ('optimum','problem_sha256','certificate_sha256','visits')})
        if j==7: store=cls(path); a.require(store.version==8)
    reads=[store.get(v) for v in (3,8,18)]
    with sqlite3.connect(path) as db: pages=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
    return dict(rows=rows,reads=reads,pages=pages,oracle_checks=exact,oracle_visits=visits)


def export_checks(path,root,name):
    x=Protected(path); doc=x.certificate(x.version); dest=root/f'{name}.json'; dest.write_bytes(a.canonical(doc)); expected=k.check(doc)
    proc=subprocess.run([sys.executable,'-I','-S',str(Path(k.__file__).resolve()),str(dest),'--expect-problem',expected['problem_sha256']],capture_output=True,timeout=20,check=True)
    a.require(json.loads(proc.stdout)==expected)
    count=0; forms=[]
    for kind in ('auto','gzip','block4'):
        p=x.export(kind=kind,anticipated_reads=6); forms.append(p['manifest']['kind'])
        for v in (3,8,18):
            result=u.retrieve(p,v,p['anchor']); receipt=x.get(v); a.require(all(result['receipt'][key]==receipt[key] for key in result['receipt'])); count+=1
    return dict(checks=count,formats=forms,standalone=1)


def controls(root):
    path=root/'control.sqlite'; x=Protected(path,{'a':2}); total=0
    x.apply({'f':(('a',),{(0,):0})},expected_version=0); q=x.get(1)
    def reject(fn):
        nonlocal total
        try: fn()
        except (ValueError,TypeError,KeyError,AttributeError): total+=1
        else: raise ValueError('bad operation accepted')
    reject(lambda:u.System(root/'missing.sqlite')); a.require(not (root/'missing.sqlite').exists())
    reject(lambda:u.System(path,profile='unknown')); reject(lambda:x.apply({},expected_version=0)); reject(lambda:x.apply({},expected_version=True))
    reject(lambda:x.apply({'f':(('a',),{(0,):False})})); reject(lambda:x.apply({}, {'a':0})); reject(lambda:x.get(99))
    reject(lambda:x.export(kind='unknown')); reject(lambda:x.export(anticipated_reads=-1)); reject(lambda:setattr(x,'profile','performance'))
    doc=x.certificate(1); doc['result']['optimum']=99; a.require(x.get(1)==q and x.certificate(1)['result']['optimum']==0); total+=1
    p=x.export(kind='gzip'); reject(lambda:u.retrieve(p,1,'0'*64)); bad=dict(p,payload=b'x'+p['payload'][1:]); reject(lambda:u.retrieve(bad,1,p['anchor']))
    y=Perf(path); y.apply({},expected_version=1); reject(lambda:x.apply({},expected_version=1)); a.require(x.version==1 and y.version==2)
    x=Protected(path); a.require(x.get(2)==y.get(2)); total+=1
    return total


def audit(root):
    root=root.resolve(); root.mkdir(); rows=[]; timings=[]
    for i,(name,d,edits) in enumerate(corpus()):
        results={key:run(cls,root/f'{name}-{key}.sqlite',d,edits,True) for key,cls in METHODS.items()}
        for key in METHODS:
            a.require(results[key]['rows']==results['full']['rows'] and results[key]['reads']==results['full']['reads'])
        export=export_checks(root/f'{name}-protected.sqlite',root,name); rows.append(dict(name=name,methods=results,export=export)); ns={key:[] for key in METHODS}
        for rep in range(3):
            labels=list(METHODS); random.Random(400+i*17+rep).shuffle(labels)
            for key in labels:
                path=root/f'timing-{i}-{rep}-{key}.sqlite'; start=time.perf_counter_ns(); run(METHODS[key],path,d,edits); ns[key].append(time.perf_counter_ns()-start); path.unlink()
        timings.append(dict(name=name,ns=ns))
    ratios={mode:{base:[st.median(x['ns'][mode])/st.median(x['ns'][base]) for x in timings] for base in ('full','routed')} for mode in ('performance','protected')}
    geo={mode:{base:math.exp(st.mean(map(math.log,v))) for base,v in rr.items()} for mode,rr in ratios.items()}; worst={mode:{base:max(v) for base,v in rr.items()} for mode,rr in ratios.items()}; physical={mode:sum(x['methods'][mode]['pages'] for x in rows)/sum(x['methods']['routed']['pages'] for x in rows) for mode in ratios}; n=controls(root)
    out=dict(rows=rows,controls=n,timings=timings,geomean=geo,worst=worst,physical_ratio=physical,decisions={mode:'REVIEW_CANDIDATE' if n==15 and max(geo[mode].values())<=.9 and max(worst[mode].values())<=1.2 and physical[mode]<=.5 else 'NO_PROMOTION' for mode in ratios},scope='synthetic bounded independent exhaustive component oracle; three randomized timed batches per mode/stream; includes create, 18 edits, reopen, three historical reads and page accounting; extra audit/export excluded; no independent replication, physical RE-X or formal program proof')
    out['evidence_sha256']=a.digest(out); return out

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); args=p.parse_args(); out=audit(args.directory); (args.directory/'evidence.json').write_bytes(a.canonical(out)); print({key:out[key] for key in ('controls','geomean','worst','physical_ratio','decisions')})
