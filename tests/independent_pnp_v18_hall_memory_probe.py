"""Development test for conditional Hall proof transfer, not blind evaluation."""
import copy
import json
import random
from collections import Counter
from itertools import combinations
from mathos.research.pnp_signed_hall_subsystem import solve as cold
from mathos.research.pnp_hall_witness_memory import admit, transfer, Limit


def base(h,rng):
    n=h*(h+1)
    v=lambda i,j:i*h+j+1
    f=[[v(i,j) for j in range(h)] for i in range(h+1)]
    f += [[-v(i,j),-v(k,j)] for j in range(h) for i,k in combinations(range(h+1),2)]
    p=list(range(1,n+1));rng.shuffle(p)
    p=[x if rng.randrange(2) else -x for x in p]
    return n, mapped(f,p)


def mapped(f,p):
    return [[p[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]


def independent(n,f,c):
    known={frozenset(q) for q in f}
    gs,bs=c['groups'],c['buckets']
    flat=[x for g in gs for x in g]
    assert c['decision']=='unsat' and gs and all(g and frozenset(g) in known for g in gs)
    assert all(type(x) is int and 0<abs(x)<=n for x in flat)
    assert len({abs(x) for x in flat})==len(flat)
    assert len(bs)<len(gs) and all(bs)
    assert sorted(x for b in bs for x in b)==sorted(flat)
    assert all(frozenset((-x,-y)) in known for b in bs for x,y in combinations(b,2))


def sat(n,f):
    return any(all(any(bool(mask & (1<<(abs(x)-1))) == (x>0) for x in c) for c in f) for mask in range(1<<n))


def probe():
    rng=random.Random(186701);counts=Counter();work=Counter();peak=0
    for h in range(3,9):
        for _ in range(5):
            n,f=base(h,rng);r=cold(n,f);assert r['decision']=='unsat'
            record=admit(n,f,r['certificate']);counts['admitted']+=1
            independent(record['n'],record['guards'],record['certificate'])
            for j in range(10):
                # Explicit known embedding, not inferred from target. Half identity,
                # half signed injection into a larger variable universe.
                m=n if j%2==0 else n+3
                p=list(range(1,m+1));rng.shuffle(p)
                p=p[:n] if j%2 else list(range(1,n+1))
                if j%2:p=[x if rng.randrange(2) else -x for x in p]
                g=mapped(f,p)
                for _ in range(3):
                    g.append([x if rng.randrange(2) else -x for x in rng.sample(range(1,m+1),rng.randint(1,4))])
                rng.shuffle(g)
                embedding=[p[v-1] for v in record['source_embedding']]
                t=transfer(m,g,record,embedding);assert t['decision']=='unsat'
                independent(m,g,t['certificate']);counts['transfers']+=1
                counts['signed_injections' if j%2 else 'strengthenings']+=1
                peak=max(peak,t['work_steps']);work['transfer']+=t['work_steps']
                a=cold(m,g);work['cold']+=a['work_steps'];counts['cold_'+a['decision']]+=1
                if a['certificate']:independent(m,g,a['certificate'])
            # Every witness premise is necessary for exact guard replay. Guard
            # deletion is not itself a claim of satisfiability of the remainder.
            g=record['guards'];k=record['n'];identity=list(range(1,k+1))
            for i in range(len(g)):
                target=g[:i]+g[i+1:]
                t=transfer(k,target,record,identity)
                assert t['status']=='guard_miss' and t['certificate'] is None
                counts['deleted_guard_rejected']+=1
            if h==3:
                for i in range(len(g)):
                    assert sat(k,g[:i]+g[i+1:]);counts['sat_deletion_controls']+=1
            # Stored record itself is untrusted, and embeddings must be injective.
            bad=copy.deepcopy(record);bad['guards'].pop()
            for rec,emb in ((bad,identity),(record,[1]*k),(record,[True]+identity[1:])):
                try:transfer(k,g,rec,emb)
                except (ValueError,Limit):counts['tamper_rejected']+=1
                else:raise AssertionError('invalid transfer accepted')
    n,f=base(3,rng);r=cold(n,f);record=admit(n,f,r['certificate']);e=record['source_embedding']
    t=transfer(n,f,record,e);q=t['work_steps']
    for b in (1,q-1,q):
        x=transfer(n,f,record,e,steps=b)
        assert x['decision']==('unsat' if b==q else 'unknown');counts['boundary_checks']+=1
    # Exact archived greedy-search counterexample, not a newly selected case.
    f=[[9,-7,-11],[-4,1,6,7],[5,-8],[-9,5],[-2,-8],[-2,-9],[10,4,2],
       [12,-1],[11,-4],[-12,8,3],[12,7],[1,9,-4,7],[5,-2],[-4,-3],
       [-8,-9],[7,-10],[-5,-6,1],[7,-8,9,3],[1],[-10,12],[6,-4],
       [10,6,-8,11],[-1,7],[6,11],[11,-3],[-1,-10],[6,-3]]
    a=cold(12,f);g=f+[[11,12]];miss=cold(12,g)
    assert a['decision']=='unsat' and miss['decision']=='unknown' and not sat(12,g)
    record=admit(12,f,a['certificate']); t=transfer(12,g,record,record['source_embedding'])
    assert t['decision']=='unsat';independent(12,g,t['certificate'])
    counterexample={'cold_base_work':a['work_steps'],'cold_strengthened_work':miss['work_steps'],
                    'transfer_work':t['work_steps'],'guard_count':len(record['guards'])}
    return {'counts':dict(counts),'work':dict(work),'max_transfer_work':peak,'boundary':q,
            'counterexample':counterexample,
            'scope':'explicit embedding; pre-admitted witness; synthetic development only'}


if __name__=='__main__':print(json.dumps(probe(),indent=2,sort_keys=True))
