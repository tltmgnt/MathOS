"""Finite audit of branch safety and total-certificate trace semantics.

Exhaustive SAT is used ONLY as an independent fixture oracle, never
claimed to be polynomial. The checker below tests a supplied exhaustive
certificate for tiny inputs; general short certificate existence is open.
"""
from itertools import product
from mathos.research.f037_log_backdoor import normalize, restrict, satisfies


def variables(f):
    return sorted({abs(l) for c in f for l in c})


def models(f):
    vs=variables(f)
    return (dict(zip(vs,b)) for b in product((False,True),repeat=len(vs))
            if satisfies(f,dict(zip(vs,b))))


def sat(f):
    return next(models(f),None) is not None


def guard(f,g):
    out=[]
    fresh=1+max([abs(g)]+variables(f))
    for c in normalize(f):
        if len(c)<=2:
            out.append((g,*c))
        elif len(c)==3:
            a,b,d=c
            out.extend(((g,a,fresh),(-fresh,b,d)))
            fresh+=1
        else:
            raise ValueError("fixture uses width three")
    return tuple(out)


def pair(a,b):
    # Reserve selector 1 and give the independent gadgets disjoint
    # variables, including their auxiliaries.
    x=guard(a,1)
    off=max([1]+variables(x))
    y=guard(b,-1)
    y=tuple(tuple(l if abs(l)==1 else
                  (1 if l>0 else -1)*(abs(l)+off) for l in c)
            for c in y)
    return x+y


def safe(f,v,b):
    return not sat(f) or sat(restrict(f,{v:b}))


def check_trace(f,vs,steps):
    # Tiny fixture verifier uses exact truth semantics as an oracle.
    if len(vs)!=len(steps):
        return False
    for v,b in zip(vs,steps):
        if type(b) is not bool or not safe(f,v,b):
            return False
        f=restrict(f,{v:b})
    return () in f


def run():
    # All 64 subsets of a signed two-variable clause vocabulary.
    rows=((2,),(-2,),(3,),(-3,),(2,3),(-2,-3))
    fs=[tuple(c for i,c in enumerate(rows) if a&(1<<i)) for a in range(64)]
    status=[sat(f) for f in fs]
    table={(a,b):0 for a,b in product((False,True),repeat=2)}
    for i,a in enumerate(fs):
        for j,b in enumerate(fs):
            f=pair(a,b)
            sa,sb=status[i],status[j]
            assert sat(restrict(f,{1:False}))==sa
            assert sat(restrict(f,{1:True}))==sb
            assert safe(f,1,True)==(not sa or sb)
            assert safe(f,1,False)==(not sb or sa)
            table[sa,sb]+=1
    # A genuine width-three guarded clause tests the split gadget.
    f=guard(((2,3,4),),1)
    for bits in product((False,True),repeat=4):
        x=dict(zip((1,2,3,4),bits))
        actual=sat(restrict(f,x))
        assert actual==(x[1] or x[2] or x[3] or x[4])
    chains=0
    rows=((),(1,),(-1,),(2,3),(1,-1),(1,1,1),
          (-1,-2,-3),(-1,-2,3),(1,2,-3),(1,2,3),(2,1),(1,2))
    for mask in range(1<<len(rows)):
        f=normalize(tuple(c for j,c in enumerate(rows) if mask&(1<<j)))
        vs=variables(f)
        found=False
        for bits in product((False,True),repeat=len(vs)):
            if check_trace(f,vs,bits):
                assert not sat(f)
                chains+=1
                found=True
        assert found==not_sat(f)
    assert not check_trace(((1,),),[1],[False])
    assert not check_trace(((1,),),[1],[])
    assert not check_trace(((1,),),[1],[True])
    print(f"pair_table={table} accepted_unsat_traces={chains}")
    print("F037_CERTIFICATE_COMPLEXITY_OK pairs=4096 guards=16 formulas=4096 rejection=3")


def not_sat(f):
    return not sat(f)


if __name__=="__main__":
    run()
