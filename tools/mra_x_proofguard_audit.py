"""Phase XLIV: disjoint seeded demand audit with deterministic risk accounting."""
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
import mra_x_proofeconomics_audit as old
import mra_x_proofguard as g


def corpus():
    for j,family in enumerate(('unary','blocks','sparse','chain','cycle','frustrated')):
        for i in range(6):
            rng=random.Random(46100+100*j+i); n=8+i; vs=[f'x{v:02}' for v in range(n)]; d=dict.fromkeys(vs,2); fs=[]
            def add(scope,sparse=False):
                tab={row:rng.randint(-8,9) for row in itertools.product(*(range(d[v]) for v in scope)) if not sparse or rng.random()<.45}
                fs.append((tuple(scope),tab))
            if family in ('unary','blocks','sparse'):
                b={'unary':1,'blocks':4,'sparse':5}[family]
                for offset in range(0,n,b):
                    group=vs[offset:offset+b]; add(group,family=='sparse'); add(group[:1],family=='sparse')
            else:
                for offset in range(n-1): add(vs[offset:offset+2])
                if family!='chain': add([vs[-1],vs[0]])
                if family=='frustrated':
                    for offset in range(n-2): add(vs[offset:offset+3])
                for v in vs: add([v])
            if i==0: fs.append(((),{}))
            yield f'{family}-{i}',*old.old.make(d,fs)


def conflicting():
    d={}; fs=[]
    for i in range(16):
        x,y=f'x{i:02}',f'y{i:02}'; d[x]=d[y]=2
        fs.extend([((x,),{(0,):0,(1,):5}),((x,y),{(0,0):5,(0,1):5,(1,0):0,(1,1):0})])
    return old.old.make(d,fs)


def measured(mode,model,doc,expected,reads):
    if mode!='guard': return old.timed(mode,model,doc,expected,reads)
    start=time.perf_counter_ns(); out=g.select(doc,expected,reads=reads); first=time.perf_counter_ns()-start
    checker=p.check if out['kind']=='partition' else k.check
    for _ in range(reads-out['checks_used']): assert checker(out['proof'],expected)==out['receipt']
    elapsed=time.perf_counter_ns()-start
    row={key:value for key,value in out.items() if key!='proof'}; row['bytes']=len(p.canonical(out['proof']))
    assert out['extra_units']<=reads*out['baseline_units']//8
    if out['kind']=='partition': assert 10*out['projected_units']<=9*reads*out['baseline_units']
    else: assert out['projected_units']<=reads*out['baseline_units']*9//8
    return row,dict(first_ns=first,total_ns=elapsed)


def controls():
    doc,expected,_=conflicting(); names=[]
    def reject(name,fn):
        try: fn()
        except (ValueError,TypeError,KeyError): names.append(name)
        else: raise AssertionError(name)
    for name,bad in [('missing_anchor',None),('empty_anchor',''),('nonhex_anchor','g'*64),('wrong_anchor','0'*64),('bool_anchor',True)]:
        reject(name,lambda:g.select(doc,bad,reads=1))
    reject('bool_demand',lambda:g.select(doc,expected,reads=True)); reject('zero_demand',lambda:g.select(doc,expected,reads=0))
    bad=copy.deepcopy(doc); bad['result']['trace'].clear(); reject('corrupt_elimination_trace',lambda:g.select(bad,expected,reads=128))
    bad=copy.deepcopy(doc); bad['result']['assignments_evaluated']+=1000; reject('forged_work_telemetry',lambda:g.select(bad,expected,reads=128))
    with patch.object(g,'root_proof',side_effect=AssertionError('unexpected speculative work')):
        assert g.select(doc,expected,reads=1)['reason']=='direct'; names.append('single_read_bypass')
    r=g.select(doc,expected,reads=128); assert r['kind']=='partition' and r['search_nodes']>0 and r['receipt']['optimum']==80; names.append('nonroot_checked_conversion')
    with patch.object(g.q,'generate',side_effect=q.Exhausted('injected')):
        r=g.select(doc,expected,reads=128); assert r['kind']=='elimination' and r['reason']=='search_refused' and r['receipt']['optimum']==80; names.append('exhausted_checked_fallback')
    r=g.select(doc,expected,reads=8); assert r['kind']=='elimination' and r['reason'] in ('structure_guard','direct'); names.append('conservative_structure_screen')
    # Root infeasibility avoids branch search; partition check remains authoritative.
    d={f'x{i}':2 for i in range(64)}; fs=[((v,),{(0,):0,(1,):1}) for v in d]+[((),{})]; doc,h,_=old.old.make(d,fs)
    r=g.select(doc,h,reads=128); assert r['kind']=='partition' and r['search_nodes']==0 and r['receipt']['optimum'] is None; names.append('root_infeasibility')
    with patch.object(g.p,'check',side_effect=ValueError('injected checker refusal')):
        reject('checker_fail_closed',lambda:g.select(doc,h,reads=128))
    return names


def audit(root,training):
    root.mkdir(); model=training['model']; rows=[]; times=[]; modes=('elimination','heuristic','predictive','guard')
    for i,(name,doc,expected,value) in enumerate(corpus()):
        for reads in (1,2,4,8,16):
            data={}; ns={m:[] for m in modes}
            for repeat in range(3):
                labels=list(modes); random.Random(44000+i*71+reads*7+repeat).shuffle(labels)
                for mode in labels:
                    result,t=measured(mode,model,doc,expected,reads); assert result['receipt']['optimum']==value and result['receipt']['problem_sha256']==expected
                    if mode in data: assert data[mode]==result
                    data[mode]=result; ns[mode].append(t)
            rows.append(dict(name=name,reads=reads,methods=data)); times.append(dict(name=name,reads=reads,ns=ns))
    out=dict(model_sha256=p.digest(training),rows=rows,timings=times,controls=controls(),scope='fresh seeds; same frozen Phase XLIII comparator; four methods, three randomized repeats; existing elimination certificate available; guard verifies elimination first and counts conversion replay as second check; proxy bounds count selected structural operations only, not elapsed time, CPU or memory; no solver, IO, training or transaction cost')
    out['evidence_sha256']=p.digest(out); (root/'evidence.json').write_bytes(p.canonical(out)); return out


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--model',type=Path,required=True); ap.add_argument('--directory',type=Path,required=True); args=ap.parse_args(); out=audit(args.directory,json.loads(args.model.read_text())); print(dict(states=len(out['rows']),controls=out['controls']))
