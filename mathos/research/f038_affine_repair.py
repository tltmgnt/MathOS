"""Certified affine translation deletion and exact bounded-rank discovery."""
from itertools import combinations
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_hybrid_affine import extract, verify_partition, reduce, parity
from mathos.research.f038_affine_direct_sum import coordinate_forms
from mathos.research.f038_affine_separator import clause, lift, equations
from mathos.research.f038_branchwidth_adapter import run, verify_negative


def flat(c,forms):
    eq=tuple((forms[abs(l)-1][0],
              forms[abs(l)-1][1]^int(l<0),()) for l in c)
    basis,bad=reduce(eq)
    if basis is None:
        return None
    return tuple((a,b,()) for _,(a,b,p) in sorted(basis.items()))


def shifted(D,v):
    return tuple((a,b^parity(a&v),()) for a,b,_ in D)


def safe(flats,active,i,v,n):
    if type(v) is not int or not 0<=v<1<<n or i not in active:
        return False
    C=flats[i]
    if C is None:
        return v==0
    if not any(parity(a&v) for a,b,p in C):
        return False
    for j in active:
        D=flats[j]
        if j==i or D is None:
            continue
        if any(parity(a&v) for a,b,p in D):
            if lift(C+shifted(D,v)) is not None:
                return False
    return True


def find_flip(flats,active,i,n):
    C=flats[i]
    if C is None:
        return 0
    basis=tuple(a for a,b,p in C)
    for p in range(1,1<<len(basis)):
        pins=equations(basis,p)
        v0=lift(pins)
        assert v0 is not None
        constraints=list(pins)
        for j in active:
            D=flats[j]
            if j==i or D is None:
                continue
            if lift(C+shifted(D,v0)) is not None:
                constraints.extend((a,0,()) for a,b,q in D)
        v=lift(tuple(constraints))
        if v is not None:
            assert safe(flats,active,i,v,n)
            return v
    return None


def verify_trace(f,n,rows,rest,retained,trace):
    if not verify_partition(f,rows,rest):
        return False
    forms,bad=coordinate_forms(rows,n)
    if forms is None:
        return False
    flats=tuple(flat(f[i],forms) for i in rest)
    active=list(range(len(rest)))
    for i,v in trace:
        if not safe(flats,active,i,v,n):
            return False
        active.remove(i)
    return tuple(active)==retained


def simplify(f,n,audit=False):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    forms,bad=coordinate_forms(rows,n)
    if forms is None:
        return None
    db=tuple(f[i] for i in rest)
    flats=tuple(flat(c,forms) for c in db)
    active=list(range(len(db)))
    trace=[]
    taut=flips=candidates=exhausted=0
    while True:
        for i in active:
            candidates+=1
            v=find_flip(flats,active,i,n)
            if audit:
                # Exhaust the ambient parameter space only in tiny fixtures.
                allowed=[]
                for d in range(1<<n):
                    good=True
                    for t in range(1<<n):
                        if clause(db[i],forms,t):
                            continue
                        if not clause(db[i],forms,t^d) or any(
                            j!=i and clause(db[j],forms,t) and
                            not clause(db[j],forms,t^d) for j in active):
                            good=False
                            break
                    # Identity is our canonical certificate for tautologies.
                    if good and (flats[i] is not None or d==0):
                        allowed.append(d)
                    assert safe(flats,active,i,d,n)==(
                        good and (flats[i] is not None or d==0))
                assert (v is not None)==bool(allowed)
                assert v is None or v in allowed
            if v is None:
                exhausted+=1
                continue
            taut+=flats[i] is None
            flips+=flats[i] is not None
            trace.append((i,v))
            active.remove(i)
            break
        else:
            break
    retained=tuple(active)
    trace=tuple(trace)
    assert verify_trace(f,n,rows,rest,retained,trace)
    removed={rest[i] for i,v in trace}
    reduced=tuple(c for i,c in enumerate(f) if i not in removed)
    return rows,rest,forms,db,retained,trace,reduced,(taut,flips,candidates,exhausted)


def repair(forms,db,trace,w):
    # Free original coordinates are literally their own parameter bits;
    # pivot bits in w are ignored by every direction row.
    t=w
    for i,v in reversed(trace):
        if not clause(db[i],forms,t):
            t^=v
    return sum(1<<i for i,(a,b) in enumerate(forms) if parity(a&t)^b)


def solve(f,n):
    p=simplify(f,n)
    if p is None:
        w,cert,_,_=run(f,n)
        assert w is None
        rows,rest=extract(f)
        assert verify_negative(f,n,rows,rest,None,cert)
        return None,None,cert
    rows,rest,forms,db,retained,trace,reduced,stats=p
    w,cert,_,_=run(reduced,n)
    if w is None:
        rr,rs=extract(reduced)
        assert verify_negative(reduced,n,rr,rs,None,cert)
        return None,p,cert
    assert satisfies(reduced,w)
    x=repair(forms,db,trace,w)
    assert satisfies(f,x)
    return x,p,cert


def audit_fixture(fixture):
    yes=no=inconsistent=original=remaining=deleted=taut=flips=0
    candidates=exhausted=fully=models_checked=steps=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        models=tuple(w for w in range(8) if satisfies(f,w))
        yes+=bool(models)
        no+=not models
        p=simplify(f,3,audit=True)
        if p is None:
            assert not models
            inconsistent+=1
            continue
        rows,rest,forms,db,retained,trace,reduced,stats=p
        original+=len(rest)
        remaining+=len(retained)
        deleted+=len(trace)
        a,b,c,d=stats
        taut+=a
        flips+=b
        candidates+=c
        exhausted+=d
        fully+=not retained
        reduced_models=tuple(w for w in range(8) if satisfies(reduced,w))
        assert bool(reduced_models)==bool(models)
        for w in reduced_models:
            x=repair(forms,db,trace,w)
            assert x in models
            models_checked+=1
            steps+=len(trace)
        x,q,cert=solve(f,3)
        assert (x is not None)==bool(models)
        if x is not None:
            assert x in models
    return (yes,no,inconsistent,original,remaining,deleted,taut,flips,
            candidates,exhausted,fully,models_checked,steps)


def audit():
    a=audit_fixture(ROWS)
    assert a==(1360,2736,2384,4736,466,4270,3088,1182,5451,1181,1360,3470,9438)
    print('F038_AFFINE_REPAIR_OK formulas=4096 sat=1360 unsat=2736 '
          'inconsistent=2384 original=4736 remaining=466 deleted=4270 '
          'tautologies=3088 flips=1182 candidates=5451 exhausted=1181 '
          'fully_reduced=1360 model_checks=3470 restoration_steps=9438')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=audit_fixture(fixture)
    assert a==(255,1,1,896,0,896,0,896,896,0,255,1920,6944)
    print('F038_AFFINE_REPAIR_FULL_OK formulas=256 sat=255 unsat=1 '
          'inconsistent=1 original=896 remaining=0 deleted=896 '
          'tautologies=0 flips=896 candidates=896 exhausted=0 '
          'fully_reduced=255 model_checks=1920 restoration_steps=6944')
    deletions=0
    for n in (3,8,16,32):
        f=tuple((a,b) for a,b in combinations(range(1,n+1),2))
        w,p,cert=solve(f,n)
        rows,rest,forms,db,retained,trace,reduced,stats=p
        assert w is not None and satisfies(f,w)
        assert not rows and not retained and not reduced
        assert len(trace)==len(f)
        assert verify_trace(f,n,rows,rest,retained,trace)
        i,v=trace[0]
        assert v
        assert not verify_trace(f,n,rows,rest,retained,((i,0),)+trace[1:])
        assert not verify_trace(f,n,rows,rest,retained,trace[:-1])
        deletions+=len(trace)
    assert deletions==647
    print('F038_AFFINE_REPAIR_DENSE_OK sizes=3,8,16,32 deleted=647 '
          'retained=0 max_reduced_width=0 corrupt_rejected=8')
    f=tuple(tuple(-v if x&(1<<j) else v for j,v in enumerate((1,4,5)))
            for x in (1,2,4,7))+((-2,4),(2,-4),(-1,3),(1,-3),(2,4),(1,3))
    rows,rest=extract(f)
    forms,bad=coordinate_forms(rows,5)
    assert forms is not None and len(rest)==2
    assert f[rest[0]]==(2,4)
    flats=tuple(flat(f[i],forms) for i in rest)
    v=find_flip(flats,(0,1),0,5)
    assert v==24 and safe(flats,(0,1),0,v,5)
    assert not any(safe(flats,(0,1),0,1<<i,5) for i in range(5))
    w,p,cert=solve(f,5)
    assert w is not None and satisfies(f,w)
    print('F038_AFFINE_REPAIR_NONCOORDINATE_OK direction=24 '
          'weight=2 single_bit_failures=5')


if __name__=='__main__':
    audit()
