"""Disjoint seeded training/calibration/test; frozen model, measured pipeline."""
import argparse
import copy
import itertools
import json
import random
import statistics as st
import time
from pathlib import Path
from unittest.mock import patch
import mra_x_boundproof as p
import mra_x_kernel as k
import mra_x_proofarbitrate as q
import mra_x_proofarbitrate_audit as old
import mra_x_proofeconomics as e


def corpus(split):
    offset,count={'train':(43100,12),'calibrate':(44100,6),'test':(45100,12)}[split]
    for family in ('unary','blocks','sparse','chain','cycle','frustrated'):
        for i in (range(0,count,2) if split=='test' else range(count)):
            rng=random.Random(offset+100*('unary','blocks','sparse','chain','cycle','frustrated').index(family)+i)
            n=8+i%7; vs=[f'x{j:02}' for j in range(n)]; d=dict.fromkeys(vs,2); fs=[]
            def add(scope,sparse=False):
                tab={r:rng.randint(-8,9) for r in itertools.product(*(range(d[v]) for v in scope)) if not sparse or rng.random()<.45}
                fs.append((tuple(scope),tab))
            if family in ('unary','blocks','sparse'):
                b={'unary':1,'blocks':4,'sparse':5}[family]
                for j in range(0,n,b):
                    group=vs[j:j+b]; add(group,family=='sparse'); add(group[:1],family=='sparse')
            else:
                for j in range(n-1): add(vs[j:j+2])
                if family!='chain': add([vs[-1],vs[0]])
                if family=='frustrated':
                    for j in range(n-2): add(vs[j:j+3])
                for v in vs: add([v])
            if i%7==0: fs.append(((),{}))
            yield f'{family}-{i:02}',*old.make(d,fs)


def observe(doc,expected):
    times={'first':[],'replay':[],'baseline':[]}; kind=None
    for repeat in range(5):
        order=['elimination','attempt']; random.Random(43+repeat).shuffle(order)
        for mode in order:
            t=time.perf_counter_ns()
            if mode=='elimination': receipt=k.check(doc,expected); times['baseline'].append(time.perf_counter_ns()-t)
            else:
                out=q.select(doc,expected,reads=4); times['first'].append(time.perf_counter_ns()-t)
                assert kind is None or kind==out['kind']; kind=out['kind']; checker=p.check if kind=='partition' else k.check
                t=time.perf_counter_ns(); assert checker(out['proof'],expected)==out['receipt']; times['replay'].append(time.perf_counter_ns()-t)
    b=st.median(times['baseline']); return dict(features=e.features(doc),visits=doc['result']['assignments_evaluated'],first=st.median(times['first'])/b,replay=st.median(times['replay'])/b,baseline_ns=b,kind=kind)


def train():
    rows=[dict(name=name,**observe(doc,expected)) for name,doc,expected,_ in corpus('train')]
    cal=[dict(name=name,**observe(doc,expected)) for name,doc,expected,_ in corpus('calibrate')]
    model,options=e.calibrate(e.fit(rows),cal)
    return dict(model=model,calibration=cal,options=options)


def timed(mode,model,doc,expected,reads):
    start=time.perf_counter_ns()
    if mode=='predictive': out=e.select(model,doc,expected,reads=reads)
    elif mode=='heuristic': out=q.select(doc,expected,reads=reads)
    else: out=dict(kind='elimination',proof=doc,receipt=k.check(doc,expected))
    first=time.perf_counter_ns()-start; checker=p.check if out['kind']=='partition' else k.check
    for _ in range(reads-1): assert checker(out['proof'],expected)==out['receipt']
    elapsed=time.perf_counter_ns()-start
    return dict(kind=out['kind'],attempted=out.get('attempted',reads>=2 if mode=='heuristic' else False),receipt=out['receipt'],bytes=len(p.canonical(out['proof']))),dict(first_ns=first,total_ns=elapsed)


def controls(model):
    doc,expected,_=old.make({'x':2,'y':2},[(('x',),{(0,):0,(1,):5}),(('x','y'),{(0,0):5,(0,1):5,(1,0):0,(1,1):0})]); names=[]
    assert not e.choose(model,doc,1); names.append('single_read')
    assert not e.choose(dict(model,margin=None),doc,16); names.append('disabled')
    for name,fn in [('bool_reads',lambda:e.select(model,doc,expected,reads=True)),('wrong_anchor',lambda:e.select(model,doc,'0'*64)),('false_optimum',lambda:e.select(model,dict(doc,result=dict(doc['result'],optimum=4)),expected))]:
        try: fn()
        except ValueError: names.append(name)
        else: raise AssertionError(name)
    with patch.object(e,'choose',return_value=True):
        with patch.object(e.q,'generate',side_effect=q.Exhausted('injected')):
            out=e.select(model,doc,expected); assert out['kind']=='elimination' and out['receipt']['optimum']==5; names.append('exhausted_fallback')
        out=e.select(model,doc,expected); assert out['kind']=='partition' and out['receipt']['optimum']==5; names.append('checked_partition')
    return names


def audit(root,training):
    root.mkdir(); model=training['model']; rows=[]; times=[]; modes=('elimination','heuristic','predictive')
    for i,(name,doc,expected,value) in enumerate(corpus('test')):
        for reads in e.DEMAND:
            data={}; ns={m:[] for m in modes}
            for repeat in range(3):
                order=list(modes); random.Random(i*71+reads*7+repeat).shuffle(order)
                for mode in order:
                    result,t=timed(mode,model,doc,expected,reads); assert result['receipt']['optimum']==value and result['receipt']['problem_sha256']==expected
                    if mode in data: assert data[mode]==result
                    data[mode]=result; ns[mode].append(t)
            rows.append(dict(name=name,reads=reads,methods=data)); times.append(dict(name=name,reads=reads,ns=ns))
    out=dict(model_sha256=p.digest(training),rows=rows,timings=times,controls=controls(model),scope='frozen empirical model; three randomized repetitions; includes prediction, attempted generation, fallback and repeated checks; existing elimination certificate available; excludes solving, IO and transaction overhead')
    out['evidence_sha256']=p.digest(out); (root/'evidence.json').write_bytes(p.canonical(out)); return out


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--model',type=Path,required=True); ap.add_argument('--directory',type=Path,required=True); args=ap.parse_args()
    if args.model.exists(): training=json.loads(args.model.read_text())
    else: training=train(); args.model.write_bytes(p.canonical(training))
    out=audit(args.directory,training); print(dict(margin=training['model']['margin'],options=training['options'],states=len(out['rows']),controls=len(out['controls'])))
