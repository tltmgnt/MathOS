"""q-Horn semantic decomposition (established tractable SAT class).
Numerical LP proposes a partition. Exact integer verification is mandatory.
No promise of complete numerical recognition.
"""
from itertools import combinations, product
from random import Random
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from mathos.research.f037_log_backdoor import normalize, decide, restrict, satisfies


def valid(f, w):
    vs={abs(l) for c in f for l in c}
    return (set(w)==vs and all(type(a) is int and 0<=a<=2 for a in w.values())
            and all(sum(w[l] if l>0 else 2-w[-l] for l in c)<=2 for c in f))


def recognize(f):
    vs=sorted({abs(l) for c in f for l in c})
    if not vs:
        return {}
    idx={v:i for i,v in enumerate(vs)}
    ii,jj,aa=[],[],[]
    b=[]
    for i,c in enumerate(f):
        b.append(1-sum(l<0 for l in c))
        for l in c:
            ii.append(i)
            jj.append(idx[abs(l)])
            aa.append(1 if l>0 else -1)
    A=coo_matrix((aa,(ii,jj)),shape=(len(f),len(vs))).tocsc()
    r=linprog([0.0]*len(vs),A_ub=A,b_ub=b,bounds=(0,1),method='highs')
    if not r.success:
        return None
    for eps in (0.0,1e-9,1e-7):
        w={v:0 if a<.5-eps else 2 if a>.5+eps else 1
           for v,a in zip(vs,r.x)}
        if valid(f,w):
            return w
    return None


def decompose(f,w):
    assert valid(f,w)
    # Rename weight-zero positive literals, so every H-positive
    # literal has weight two; Q literals retain weight one.
    flip={v for v,a in w.items() if a==0}
    H={v for v,a in w.items() if a!=1}
    g=tuple(tuple(-l if abs(l) in flip else l for l in c) for c in f)
    horn=tuple(c for c in g if all(abs(l) in H for l in c))
    mixed=tuple(c for c in g if any(abs(l) not in H for l in c))
    assert all(sum(l>0 for l in c)<=1 for c in horn)
    assert all(sum(abs(l) not in H for l in c)<=2 and
               all(l<0 for l in c if abs(l) in H) for c in mixed)
    return H,flip,horn,mixed


def least(H,horn):
    x=set()
    trace=[]
    while True:
        changed=False
        for i,c in enumerate(horn):
            if any(-l not in x for l in c if l<0):
                continue
            pos=[l for l in c if l>0]
            if not pos:
                return x,tuple(trace),i
            if pos[0] not in x:
                x.add(pos[0])
                trace.append(i)
                changed=True
        if not changed:
            return x,tuple(trace),None


def check_unsat(raw,cert):
    f=normalize(raw)
    w,trace,contradiction,proof=cert
    if not valid(f,w):
        return False
    H,flip,horn,mixed=decompose(f,w)
    x=set()
    for i in trace:
        if not 0<=i<len(horn):
            return False
        c=horn[i]
        pos=[l for l in c if l>0]
        if len(pos)!=1 or pos[0] in x or any(-l not in x for l in c if l<0):
            return False
        x.add(pos[0])
    if contradiction is not None:
        if not 0<=contradiction<len(horn):
            return False
        return all(l<0 and -l in x for l in horn[contradiction])
    # Even a partial forced-true H set suffices for UNSAT: every
    # clause with all H antecedents in x is mandatory for all models.
    q=restrict(mixed,{v:v in x for v in H})
    from mathos.research.f037_log_backdoor import check_unsat as check_binary
    return proof is not None and check_binary(q,proof)


def solve(raw, supplied=None):
    raw=tuple(tuple(c) for c in raw)
    f=normalize(raw)
    w=recognize(f) if supplied is None else supplied
    if w is None or not valid(f,w):
        return 'UNKNOWN',None
    H,flip,horn,mixed=decompose(f,w)
    x,trace,bad=least(H,horn)
    if bad is not None:
        cert=(w,trace,bad,None)
        assert check_unsat(raw,cert)
        return 'UNSAT',cert
    h={v:v in x for v in H}
    q=restrict(mixed,h)
    status,evidence=decide(q,0)
    assert status!='UNKNOWN'
    if status=='UNSAT':
        cert=(w,trace,None,evidence)
        assert check_unsat(raw,cert)
        return status,cert
    h.update(evidence)
    model={v:(h.get(v,False)!=(v in flip)) for v in w}
    assert satisfies(raw,model)
    return 'SAT',model


def dense(t,bad):
    # A complete primal graph on 3t Horn variables.
    f=[(-3*i-1,-3*i-2,3*i+3) for i in range(t)]
    f.extend((-u,-v) for u,v in combinations(range(1,3*t+1),2)
             if (u-1)//3!=(v-1)//3)
    p,q=3*t+1,3*t+2
    f.extend([(1,),(2,),(-3,p),(-3,q),(-p,-q) if bad else (p,q)])
    return tuple(f)


def transform(f,rng):
    vs=sorted({abs(l) for c in f for l in c})
    perm=list(vs)
    rng.shuffle(perm)
    mp={v:w*rng.choice((-1,1)) for v,w in zip(vs,perm)}
    out=[tuple(mp[abs(l)]*(1 if l>0 else -1) for l in c) for c in f]
    rng.shuffle(out)
    return tuple(out)


def run():
    rng=Random(3704)
    counts={'SAT':0,'UNSAT':0,'UNKNOWN':0}
    # Small arbitrary formulas, with an exact brute-force class oracle.
    for _ in range(256):
        f=tuple(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,5),rng.randrange(1,4)))
                for _ in range(rng.randrange(1,18)))
        g=normalize(f)
        vs=sorted({abs(l) for c in g for l in c})
        eligible=any(valid(g,dict(zip(vs,w))) for w in product(range(3),repeat=len(vs)))
        sat=any(satisfies(f,dict(zip(range(1,5),bits))) for bits in product((False,True),repeat=4))
        status,evidence=solve(f)
        assert (status!='UNKNOWN')==eligible
        if status=='SAT':
            assert sat and satisfies(f,evidence)
        elif status=='UNSAT':
            assert not sat and check_unsat(f,evidence)
        counts[status]+=1
    for t in (2,4,8,16,32):
        for bad in (False,True):
            f=transform(dense(t,bad),rng)
            status,evidence=solve(f)
            assert status==('UNSAT' if bad else 'SAT')
            if bad:
                assert check_unsat(f,evidence)
            else:
                assert satisfies(f,evidence)
    # Test a fixed mixed partition: a Horn deduction activates a
    # genuinely contradictory binary residual.
    f=((1,),(-1,-2,3),(2,),(-3,4),(-3,5),(-4,-5))
    w={1:2,2:2,3:2,4:1,5:1}
    status,cert=solve(f,w)
    assert status=='UNSAT' and check_unsat(f,cert)
    ww,tr,bad,p=cert
    assert bad is None and p is not None
    assert not check_unsat(f,(ww,tr,bad,None))
    assert not check_unsat(f,(ww,(),bad,p))
    assert not check_unsat(f,({**ww,1:5},tr,bad,p))
    print(counts)
    print('F037_QHORN_OK random=256 dense=10 max_variables=98 mixed=1 rejection=3')


if __name__=='__main__':
    run()
