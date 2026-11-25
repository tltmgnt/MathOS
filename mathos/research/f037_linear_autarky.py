"""Exact checked noninvertible choices via linear autarkies.

LP is a candidate generator; accepted partial assignments are checked
against the original clauses. No exact numerical recognition claim.
"""
from itertools import combinations, product
from random import Random
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from mathos.research.f037_log_backdoor import normalize, restrict, decide, satisfies
from mathos.research.f037_symmetry_selector import discover as symmetries


def check(f, assignment):
    vs={abs(l) for c in f for l in c}
    if not set(assignment)<=vs or any(type(b) is not bool for b in assignment.values()):
        return False
    for c in f:
        touched=[l for l in c if abs(l) in assignment]
        if touched and not any(assignment[abs(l)]==(l>0) for l in touched):
            return False
    return True


def discover(f):
    vs=sorted({abs(l) for c in f for l in c})
    if not vs:
        return {}
    idx={v:i for i,v in enumerate(vs)}
    ii,jj,aa=[],[],[]
    for i,c in enumerate(f):
        for l in c:
            ii.append(i)
            jj.append(idx[abs(l)])
            aa.append(-1 if l>0 else 1)
    A=coo_matrix((aa,(ii,jj)),shape=(len(f),len(vs))).tocsc()
    def candidate(obj):
        r=linprog(obj,A_ub=A,b_ub=[0.0]*len(f),
                  bounds=(-1,1),method='highs')
        if not r.success:
            return {}
        for eps in (1e-8,1e-10,0):
            x={v:bool(a>0) for v,a in zip(vs,r.x) if abs(a)>eps}
            if x and check(f,x):
                return x
        return {}
    # Fast aggregate objective first; coordinate objectives give the
    # complete mathematical search when using an exact LP oracle.
    x=candidate([-1.0]*len(vs))
    if x:
        return x
    for i in range(len(vs)):
        for sign in (-1,1):
            obj=[0.0]*len(vs)
            obj[i]=sign
            x=candidate(obj)
            if x:
                return x
    return {}


def reduce(raw):
    f=normalize(raw)
    fixed={}
    trace=[]
    while True:
        x=discover(f)
        if not x:
            return f,fixed,tuple(trace)
        assert check(f,x) and not set(x)&set(fixed)
        trace.append(x)
        fixed.update(x)
        f=restrict(f,x)


def replay(raw,trace):
    f=normalize(raw)
    fixed={}
    for x in trace:
        if not x or not check(f,x) or set(x)&set(fixed):
            return None
        fixed.update(x)
        f=restrict(f,x)
    return f,fixed


def solve(raw,k=0):
    raw=tuple(tuple(c) for c in raw)
    f,fixed,trace=reduce(raw)
    assert replay(raw,trace)==(f,fixed)
    status,evidence=decide(f,k)
    if status=='SAT':
        x={**fixed,**evidence}
        assert satisfies(raw,x)
        return status,x
    if status=='UNSAT':
        return status,(trace,evidence)
    return status,None


def check_unsat(raw,cert):
    from mathos.research.f037_log_backdoor import check_unsat as check_leaf
    trace,proof=cert
    result=replay(raw,trace)
    return result is not None and check_leaf(result[0],proof)


def dense(t,bad):
    f=[]
    for i in range(t):
        a,b,c,d,e,g=range(6*i+1,6*i+7)
        f.extend(((a,b,c),(d,-a,-b),(e,-b,-c),(g,-a,-c)))
    f.extend((u,v) for u,v in combinations(range(1,6*t+1),2)
             if (u-1)//6!=(v-1)//6)
    # Both mixed clauses are satisfied by a=true, leaving the
    # binary core untouched even when it is inconsistent.
    p,q,r=range(6*t+1,6*t+4)
    f.extend(((1,p),(1,-p),(p,),(-p,q),(-q,r),(-r,-p) if bad else (r,p)))
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
    rng=Random(3707)
    changed=steps=0
    for _ in range(128):
        f=tuple(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,5),rng.randrange(1,4)))
                for _ in range(rng.randrange(1,14)))
        h,fixed,trace=reduce(f)
        assert replay(f,trace)==(h,fixed)
        changed+=bool(trace)
        steps+=len(trace)
        vs=range(1,5)
        xs=[dict(zip(vs,bits)) for bits in product((False,True),repeat=4)]
        original=any(satisfies(f,x) for x in xs)
        residual=any(satisfies(h,x) for x in xs)
        assert original==residual
        for x in xs:
            if satisfies(f,x):
                assert satisfies(f,{**x,**fixed})
    for t in (2,4,8,16):
        for bad in (False,True):
            f=transform(dense(t,bad),rng)
            assert not symmetries(f)
            h,x,trace=reduce(f)
            assert len(x)>=6*t and all(len(c)<=2 for c in h)
            status,evidence=solve(f)
            assert status==('UNSAT' if bad else 'SAT')
            if bad:
                assert check_unsat(f,evidence)
            else:
                assert satisfies(f,evidence)
    f=((1,2),(-1,3))
    assert not check(f,{1:True})
    assert replay(f,({2:True},{2:False})) is None
    assert replay(f,({99:True},)) is None
    print(f"random_changed={changed} autarky_steps={steps}")
    print("F037_LINEAR_AUTARKY_OK random=128 dense=8 max_variables=99 rejection=3")


if __name__=="__main__":
    run()
