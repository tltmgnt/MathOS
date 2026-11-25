"""RUP-certified simultaneous constant overwrites.

A proposed overwrite need not be an autarky: clauses whose assigned
literals are all false may survive if implied by the old formula.
This is a sufficient model-repair test, not a complete SAT procedure.
"""
from itertools import combinations, product
from random import Random
from mathos.research.f037_log_backdoor import normalize, restrict, decide, satisfies
from mathos.research.f037_symmetry_selector import discover as symmetries
from mathos.research.f037_linear_autarky import discover as linear_autarky
from mathos.research.f037_checked_folding import find as folding


def rup(f,c):
    # To prove a clause, assume its negation and unit-propagate.
    x={}
    for l in c:
        v,b=abs(l),l<0
        if v in x and x[v]!=b:
            return True
        x[v]=b
    while True:
        g=restrict(f,x)
        if () in g:
            return True
        unit=next((c[0] for c in g if len(c)==1),None)
        if unit is None:
            return False
        v=abs(unit)
        assert v not in x
        x[v]=unit>0


def check(f,x):
    vs={abs(l) for c in f for l in c}
    if not x or not set(x)<=vs or any(type(b) is not bool for b in x.values()):
        return False
    for c in f:
        if not any(abs(l) in x for l in c):
            continue
        if any(abs(l) in x and x[abs(l)]==(l>0) for l in c):
            continue
        remaining=tuple(l for l in c if abs(l) not in x)
        if not rup(f,remaining):
            return False
    return True


def discover(f,r):
    vs=sorted({abs(l) for c in f for l in c})
    for k in range(1,min(r,len(vs))+1):
        for scope in combinations(vs,k):
            for bits in product((False,True),repeat=k):
                x=dict(zip(scope,bits))
                if check(f,x):
                    return x
    return None


def reduce(raw,r):
    f=normalize(raw)
    fixed={}
    trace=[]
    while True:
        if () in f:
            return f,fixed,tuple(trace)
        x=discover(f,r)
        if x is None:
            return f,fixed,tuple(trace)
        assert not set(fixed)&set(x)
        trace.append(x)
        fixed.update(x)
        f=restrict(f,x)


def replay(raw,trace):
    f=normalize(raw)
    fixed={}
    for x in trace:
        if not check(f,x) or set(x)&set(fixed):
            return None
        fixed.update(x)
        f=restrict(f,x)
    return f,fixed


def solve(raw,r,k):
    raw=tuple(tuple(c) for c in raw)
    f,fixed,trace=reduce(raw,r)
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
    from mathos.research.f037_log_backdoor import check_unsat as leaf_check
    trace,proof=cert
    g=replay(raw,trace)
    return g is not None and leaf_check(g[0],proof)


def family(t,bad):
    # One-hot gadgets with exactly one viable color, but no units.
    # A binary implication chain forces the first color by failed literal.
    # Negative cross-color edges make cross-gadget folds invalid.
    f=[]
    for i in range(t):
        a,b,c,u,v=range(5*i+1,5*i+6)
        f.extend(((a,b,c),(-a,-b),(-a,-c),(-b,-c),(a,u),(-u,v),(-v,a)))
    # Every pair is forbidden from sharing the *second* color.
    f.extend((-5*i-2,-5*j-2) for i,j in combinations(range(t),2))
    if bad:
        f.append((-1,-6))
    return tuple(f)


def run():
    rng=Random(3709)
    maps=transports=0
    for _ in range(128):
        f=normalize(tuple(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,5),rng.randrange(1,4)))
                          for _ in range(rng.randrange(1,12))))
        vs=sorted({abs(l) for c in f for l in c})
        xs=[dict(zip(vs,bits)) for bits in product((False,True),repeat=len(vs))]
        models=[x for x in xs if satisfies(f,x)]
        for k in (1,2):
            for s in combinations(vs,k):
                for bits in product((False,True),repeat=k):
                    x=dict(zip(s,bits))
                    if not check(f,x):
                        continue
                    maps+=1
                    h=restrict(f,x)
                    assert bool(models)==any(satisfies(h,m) for m in xs)
                    for m in models:
                        assert satisfies(f,{**m,**x})
                        transports+=1
        h,fixed,trace=reduce(f,2)
        assert replay(f,trace)==(h,fixed)
        assert bool(models)==any(satisfies(h,m) for m in xs)
    for t in (2,4,8,16):
        for bad in (False,True):
            f=family(t,bad)
            assert not symmetries(f)
            assert not linear_autarky(f)
            assert folding(normalize(f)) is None
            # Fixing the first color to true touches two negative
            # one-hot clauses; these are not satisfied by the bit.
            assert check(f,{1:True})
            status,evidence=solve(f,1,0)
            assert status==('UNSAT' if bad else 'SAT')
            if bad:
                assert check_unsat(f,evidence)
    # A two-variable simultaneous repair is strictly stronger than
    # separate overwrites: equality x=y admits either joint setting.
    f=((1,-2),(-1,2))
    assert discover(f,1) is None
    assert check(f,{1:False,2:False})
    assert not check(f,{1:True})
    assert not check(f,{1:True,2:False})
    assert replay(f,({99:True},)) is None
    print(f"accepted_overwrites={maps} model_transports={transports}")
    print("F037_RUP_REPAIR_OK random=128 family=8 max_variables=80 simultaneous=1 rejection=3")


if __name__=='__main__':
    run()
