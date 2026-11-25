"""Audit a direct single-path SAT candidate without an UNSAT oracle.

A failed run on a satisfiable input is efficiently checkable using
the input model. A failed run alone is NOT evidence of UNSAT.
"""
from itertools import product
from mathos.research.f037_log_backdoor import normalize, restrict, satisfies


def follow(raw,pick,order=None):
    raw=tuple(tuple(c) for c in raw)
    f=normalize(raw)
    vs={abs(l) for c in f for l in c}
    order=tuple(sorted(vs)) if order is None else tuple(order)
    assert len(set(order))==len(order) and vs<=set(order)
    x={}
    for v in order:
        b=pick(f,v)
        assert type(b) is bool
        x[v]=b
        f=restrict(f,{v:b})
    return x


def majority(f,v):
    pos=sum(v in c for c in f)
    neg=sum(-v in c for c in f)
    return pos>=neg


def unit_first(f,v):
    if (v,) in f:
        return True
    if (-v,) in f:
        return False
    return majority(f,v)


def check_failure(f,witness,pick):
    return satisfies(f,witness) and not satisfies(f,follow(f,pick))


def shrink_failure(f,witness,pick):
    assert check_failure(f,witness,pick)
    f=tuple(f)
    while True:
        for i in range(len(f)):
            g=f[:i]+f[i+1:]
            if check_failure(g,witness,pick):
                f=g
                break
        else:
            return f


def run():
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    sat=unsat=0
    counts={p.__name__:[0,0] for p in (majority,unit_first)}
    counterexamples={}
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        witness=next((dict(zip((1,2,3),bits))
                      for bits in product((False,True),repeat=3)
                      if satisfies(f,dict(zip((1,2,3),bits)))),None)
        if witness is None:
            unsat+=1
        else:
            sat+=1
        for pick in (majority,unit_first):
            x=follow(f,pick)
            if satisfies(f,x):
                assert witness is not None
                counts[pick.__name__][0]+=1
            elif witness is not None:
                assert check_failure(f,witness,pick)
                counts[pick.__name__][1]+=1
                counterexamples.setdefault(pick.__name__,(f,witness,pick))
    assert (sat,unsat)==(1280,2816)
    # Also exhibit a majority/unit-first failure without initial units.
    f=((-1,2),(-1,-2),(1,3),(1,4),(1,5))
    w={1:False,2:False,3:True,4:True,5:True}
    assert check_failure(f,w,majority)
    assert check_failure(f,w,unit_first)
    for f,w,pick in counterexamples.values():
        small=shrink_failure(f,w,pick)
        assert check_failure(small,w,pick)
        assert all(not check_failure(small[:i]+small[i+1:],w,pick)
                   for i in range(len(small)))
    # A reference exponential selector illustrates the sufficient
    # condition only; it is not a proposed polynomial algorithm.
    def reference(f,v):
        h=restrict(f,{v:False})
        vs=sorted({abs(l) for c in h for l in c})
        return not any(satisfies(h,dict(zip(vs,bits)))
                       for bits in product((False,True),repeat=len(vs)))
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        witness=any(satisfies(f,dict(zip((1,2,3),bits)))
                    for bits in product((False,True),repeat=3))
        assert satisfies(f,follow(f,reference))==witness
    print(counts)
    print("F037_SINGLE_PATH_GATE_OK formulas=4096 selectors=3 sat=1280 unsat=2816 explicit_failure=1")


if __name__=="__main__":
    run()
