"""Matched cold, repeated and churn replay of both checked proof formats."""
import argparse
import copy
import itertools
import json
import random
import statistics as st
import time
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
import mra_x_boundproof as p
import mra_x_kernel as k
import mra_x_proofarbitrate as q
import mra_x_proofarbitrate_audit as base
import mra_x_replay as r


def corpus():
    for j,family in enumerate(('unary','blocks','sparse','chain','cycle','frustrated')):
        for i in range(6):
            rng=random.Random(47100+100*j+i); n=5+i; vs=[f'x{v:02}' for v in range(n)]; d=dict.fromkeys(vs,2); fs=[]
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
            doc,expected,value=base.make(d,fs)
            proof=q.generate(doc,q.Search(nodes=p.MAX_NODES,work=p.MAX_ROWS,entries=100000))
            for kind,obj in [('elimination',doc),('partition',proof)]:
                raw=p.canonical(obj); receipt=r.check(kind,raw,expected); assert receipt['optimum']==value
                yield f'{family}-{i}-{kind}',kind,obj,raw,expected,receipt


def run(mode,items,entries=16,payload=524288):
    start=time.perf_counter_ns(); cache=r.Cache(entries=entries,payload_bytes=payload) if mode=='cache' else None
    for _,kind,obj,raw,expected,receipt in items:
        # Simulate separate immutable wire buffers, not the same object/hash.
        data=memoryview(raw).tobytes()
        if mode=='cache': result=cache.verify(kind,data,expected)
        elif mode=='wire': result=r.check(kind,data,expected)
        else: result=r.CHECKERS[kind](obj,expected)
        assert result==receipt
    elapsed=time.perf_counter_ns()-start
    stats=cache.stats() if cache else dict(checks=len(items),hits=0)
    assert stats['checks']+stats['hits']==len(items)
    return stats,elapsed


def controls(items):
    _,kind,obj,raw,h,receipt=next(x for x in items if x[1]=='elimination' and x[-1]['optimum'] is not None)
    cache=r.Cache(entries=2,payload_bytes=2*len(raw)+100); names=[]
    assert cache.verify(kind,raw,h)==receipt; names.append('cold_full_check')
    with patch.object(r,'check',side_effect=AssertionError('hit repeated full checker')):
        assert cache.verify(kind,memoryview(raw).tobytes(),h)==receipt
    names.append('equal_distinct_bytes_hit')
    copy_receipt=cache.verify(kind,raw,h); copy_receipt['optimum']=999; assert cache.verify(kind,raw,h)==receipt; names.append('detached_receipt')
    def reject(name,fn):
        before=cache.stats()
        try: fn()
        except (ValueError,TypeError,KeyError,RecursionError): names.append(name)
        else: raise AssertionError(name)
        assert cache.stats()==before
    for name,bad in [('missing_anchor',None),('wrong_anchor','0'*64),('nonhex_anchor','g'*64)]: reject(name,lambda:cache.verify(kind,raw,bad))
    reject('wrong_format',lambda:cache.verify('partition',raw,h)); reject('unknown_format',lambda:cache.verify('other',raw,h))
    reject('mutable_bytes',lambda:cache.verify(kind,bytearray(raw),h)); reject('oversize',lambda:cache.verify(kind,b'x'*(r.MAX_BYTES+1),h))
    reject('noncanonical',lambda:cache.verify(kind,raw+b' ',h)); reject('duplicate_key',lambda:cache.verify(kind,b'{"schema":1,'+raw[1:],h))
    bad=copy.deepcopy(obj); bad['result']['optimum']+=1; reject('changed_objective',lambda:cache.verify(kind,p.canonical(bad),h))
    bad=copy.deepcopy(obj); bad['result']['trace'].clear(); reject('changed_trace',lambda:cache.verify(kind,p.canonical(bad),h))
    other=next(x for x in items if x[1]=='partition' and x[4]==h); before=cache.stats(); assert cache.verify(other[1],other[3],h)==other[-1] and cache.stats()['checks']==before['checks']+1; names.append('format_separated')
    # Force capacity eviction and recheck on reread.
    small=r.Cache(entries=1,payload_bytes=r.MAX_BYTES)
    for x in (items[0],items[1],items[0]): assert small.verify(x[1],x[3],x[4])==x[-1]
    assert small.stats()['evictions']==2 and small.stats()['checks']==3; names.append('entry_eviction')
    tiny=r.Cache(entries=8,payload_bytes=len(raw)-1)
    for _ in range(2): assert tiny.verify(kind,raw,h)==receipt
    assert tiny.stats()['bypasses']==2 and tiny.stats()['entries']==0; names.append('oversize_cache_bypass')
    # Byte-based eviction even below entry capacity.
    pair=items[:2]; cap=max(len(x[3]) for x in pair); bounded=r.Cache(entries=8,payload_bytes=cap)
    for x in pair: bounded.verify(x[1],x[3],x[4])
    assert bounded.stats()['entries']==1 and bounded.stats()['evictions']==1 and bounded.stats()['payload_bytes']<=cap; names.append('byte_eviction')
    cache.clear(); before=cache.stats(); assert before['entries']==before['payload_bytes']==0; assert cache.verify(kind,raw,h)==receipt and cache.stats()['checks']==before['checks']+1; names.append('clear_requires_check')
    # Fresh process cannot inherit cached trust.
    code='import sys,mra_x_replay as r; c=r.Cache(); c.verify(sys.argv[1],bytes.fromhex(sys.argv[2]),sys.argv[3]); assert c.stats()["checks"]==1 and c.stats()["hits"]==0'
    subprocess.run([sys.executable,'-c',code,kind,raw.hex(),h],check=True,cwd=Path(__file__).resolve().parent,timeout=20); names.append('fresh_process_cold')
    return names


def audit():
    items=list(corpus()); modes=('parsed','wire','cache'); rows=[]; timing=[]
    for i,item in enumerate(items):
        for reads in (1,4,16):
            ns={m:[] for m in modes}; results={}
            for rep in range(3):
                labels=list(modes); random.Random(45000+i*19+reads+rep).shuffle(labels)
                for m in labels:
                    stats,t=run(m,[item]*reads); ns[m].append(t)
                    if m in results: assert results[m]==stats
                    results[m]=stats
            assert results['cache']['checks']==1 and results['cache']['hits']==reads-1
            rows.append(dict(name=item[0],kind=item[1],reads=reads,receipt=item[-1],bytes=len(item[3]),methods=results)); timing.append(dict(name=item[0],reads=reads,ns=ns))
    # Churn: four hot pairs, 72 unique cold proofs, then the hot pairs again.
    hot=items[:8]; sequence=hot*4+items+hot*4; churn=[]; churn_times=[]
    for capacity in (4,16,128):
        ns={m:[] for m in modes}; results={}
        for rep in range(5):
            labels=list(modes); random.Random(45099+capacity+rep).shuffle(labels)
            for m in labels:
                stats,t=run(m,sequence,entries=capacity); ns[m].append(t)
                if m in results: assert results[m]==stats
                results[m]=stats
        churn.append(dict(capacity=capacity,requests=len(sequence),methods=results)); churn_times.append(dict(capacity=capacity,ns=ns))
    out=dict(rows=rows,churn=churn,controls=controls(items),timing=timing,churn_timing=churn_times,scope='trusted process-local exact-byte receipt memoization; fresh byte buffers per request, preexisting proofs; parsed baseline already decoded; timing includes checks and cache lifecycle, excludes proof generation, wire encoding, IO, transactions and process startup except fresh-process control; payload caps not RSS')
    out['evidence_sha256']=p.digest(out); return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args(); out=audit(); args.output.write_bytes(p.canonical(out)); print(dict(scenarios=len(out['rows']),controls=len(out['controls']),churn=out['churn']))
