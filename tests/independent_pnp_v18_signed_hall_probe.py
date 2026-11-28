"""Independent synthetic controls for signed Hall subsystem certificate search."""
import random
import json
from itertools import combinations, product
from collections import Counter
from mathos.research.pnp_signed_hall_subsystem import solve, replay
from mathos.research.pnp_bounded_matching import solve as strict


def exhaustive(n, f):
    m=1<<n
    mask=(1<<m)-1
    positives=[]
    for v in range(n):
        block=(1<<(1<<v))-1
        bits=0
        for i in range(1<<v,m,1<<(v+1)):
            bits|=block<<i
        positives.append(bits)
    surviving=mask
    for c in f:
        sat=0
        for x in c:
            b=positives[abs(x)-1]
            sat|=b if x>0 else mask^b
        surviving &= sat
        if not surviving:
            return False
    return bool(surviving)


def independent_check(n,f,c):
    # No use of matching search or production certificate checking.
    known={frozenset(q) for q in f}
    assert c["decision"]=="unsat"
    gs,bs=c["groups"],c["buckets"]
    flat=[x for g in gs for x in g]
    assert gs and all(g and frozenset(g) in known for g in gs)
    assert all(type(x) is int and 0<abs(x)<=n for x in flat)
    assert len({abs(x) for x in flat})==len(flat)
    assert len(bs)<len(gs) and all(bs)
    assert sorted(x for b in bs for x in b)==sorted(flat)
    assert all(frozenset((-x,-y)) in known for b in bs for x,y in combinations(b,2))


def make(h,sat,rng):
    n=h*(h+1)
    v=lambda i,j:i*h+j+1
    f=[[v(i,j) for j in range(h)] for i in range(h+1)]
    f += [[-v(i,j),-v(k,j)] for j in range(h) for i,k in combinations(range(h+1),2)
          if not (sat and j==0 and i==0 and k==h)]
    witness={v(i,i%h) for i in range(h+1)}
    f.append([1])
    for _ in range(4):
        c=rng.sample(range(1,n+1),h+1)
        c=[x if x in witness else -x for x in c]
        f.append(c)
    p=list(range(1,n+1));rng.shuffle(p)
    p=[x if rng.randrange(2) else -x for x in p]
    g=[[p[abs(x)-1]*(1 if x>0 else -1) for x in c] for c in f]
    for c in g:rng.shuffle(c)
    rng.shuffle(g)
    model=[False]*n
    for i,x in enumerate(p,1):model[abs(x)-1]=(i in witness)==(x>0)
    if sat: assert all(any(model[abs(x)-1]==(x>0) for x in c) for c in g)
    return n,g


def probe():
    rng=random.Random(185619); counts=Counter(); costs=[]
    for h in range(3,9):
        for sat in (False,True):
            for _ in range(10):
                n,f=make(h,sat,rng)
                r=solve(n,f);replay(n,f,r)
                old=strict(n,f,steps=25_000,seconds=1.25)
                assert old['decision']=='unknown'
                assert r['decision']==('unknown' if sat else 'unsat')
                if r['certificate']: independent_check(n,f,r['certificate'])
                if n<=12: assert exhaustive(n,f)==sat
                counts['mixed_sat_controls' if sat else 'mixed_unsat_certified']+=1
                costs.append(r['work_steps'])
    for i in range(500):
        n,f=make(3,bool(i%2),rng)
        for _ in range(rng.randrange(1,5)):
            j=rng.randrange(len(f));c=f[j]
            if rng.randrange(2):f.pop(j)
            else:
                k=rng.randrange(len(c));c[k]=-c[k]
        ref=exhaustive(n,f);r=solve(n,f);replay(n,f,r)
        assert r['decision']=='unknown' or not ref
        if r['certificate']: independent_check(n,f,r['certificate'])
        counts['perturbed_'+r['decision']]+=1
    n,f=make(3,False,rng);r=solve(n,f);w=r['work_steps']
    for q in (1,w-1,w):
        s=solve(n,f,steps=q);assert s['decision']==('unsat' if q==w else 'unknown');replay(n,f,s,steps=q)
        counts['boundary_checks']+=1
    assert solve(n,f,steps=1)['certificate'] is None
    # A SAT claim is never admitted even if it includes a real model.
    for bad in (dict(r,decision='sat'),dict(r,certificate=None),dict(r,work_steps=0)):
        try: replay(n,f,bad)
        except (ValueError,RuntimeError): counts['forgeries_rejected']+=1
        else: raise AssertionError('forged certificate accepted')
    # Preserve a discovered search-monotonicity counterexample, not a soundness failure.
    n,f=make(3,False,random.Random(185620))
    old=solve(n,f)
    stronger=f+[[11,12]]
    assert old['decision']=='unsat' and solve(n,stronger)['decision']=='unknown'
    assert not exhaustive(n,stronger)
    independent_check(n,stronger,old['certificate'])
    replay(n,stronger,old)
    counts['search_monotonicity_counterexample']+=1
    return {'counts':dict(counts),'max_mixed_work':max(costs),'example_boundary':w,
            'scope':'synthetic development only; independent mathematical witness replay'}


if __name__=='__main__':print(json.dumps(probe(),indent=2,sort_keys=True))
