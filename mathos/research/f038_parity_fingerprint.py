"""Affine model-parity fingerprints: isolation and explicit limits.

All exhaustive enumeration is a finite audit, not a polynomial parity
oracle. The mathematical polynomial advice bound is nonuniform.
"""
from collections import Counter
from itertools import product
from random import Random
from mathos.research.f037_log_backdoor import satisfies


def probe_mask(n, equations):
    return sum(1<<x for x in range(1<<n)
               if all((x&a).bit_count()%2==b for a,b in equations))


def distributions(n):
    full=(1<<(1<<n))-1
    rows=Counter(probe_mask(n,((a,b),))
                 for a in range(1<<n) for b in (0,1))
    dist=Counter({full:1})
    for k in range(1,n+2):
        nxt=Counter()
        for p,u in dist.items():
            for q,v in rows.items():
                nxt[p&q]+=u*v
        dist=nxt
        assert sum(dist.values())==2**((n+1)*k)
        yield k,dist


def greedy(n, masks):
    # Deliberately exhaustive finite advice synthesis. No asymptotic
    # runtime claim. Each selected test covers odd intersections.
    uncovered=set(range(1,1<<(1<<n)))
    chosen=[]
    while uncovered:
        p=max(masks,key=lambda p:(sum((p&s).bit_count()%2
                                      for s in uncovered),p))
        rest={s for s in uncovered if (p&s).bit_count()%2==0}
        assert len(rest)<len(uncovered)
        chosen.append(p)
        uncovered=rest
    return tuple(chosen)


def detects(s, probes):
    return any((s&p).bit_count()%2 for p in probes)


def xor_row(a,b,c):
    return [tuple(-v if bit else v for v,bit in zip((a,b,c),bits))
            for bits in product((False,True),repeat=3)
            if bits[0]^bits[1]!=bits[2]]


def encode_hash(n, equations):
    # Explicit original variables, including absent/free ones, count
    # toward the assignment domain. Auxiliaries have unique extensions.
    f=[]
    top=n
    for a,b in equations:
        vs=[i+1 for i in range(n) if a&(1<<i)]
        if not vs:
            if b:
                f.append(())
            continue
        acc=vs[0]
        for v in vs[1:]:
            top+=1
            f.extend(xor_row(acc,v,top))
            acc=top
        f.append((acc if b else -acc,))
    return tuple(f),top


def blind_points(n, probes):
    # At most q+1 points suffice for a nontrivial dependence of
    # their q-bit measurement columns.
    q=len(probes)
    assert q<1<<n
    basis={}
    for x in range(q+1):
        v=sum(((p>>x)&1)<<i for i,p in enumerate(probes))
        support=1<<x
        while v:
            pivot=v.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(v,support)
                break
            w,t=basis[pivot]
            v^=w
            support^=t
        else:
            return tuple(j for j in range(q+1) if support&(1<<j))
    raise AssertionError("q+1 columns must be dependent")


def membership(n, points):
    rows=[]
    gates=[]
    top=n
    def AND(a,b):
        nonlocal top
        top+=1
        rows.extend(((-top,a),(-top,b),(top,-a,-b)))
        gates.append((top,a,b))
        return top
    flags=[]
    for x in points:
        ls=[i+1 if x&(1<<i) else -(i+1) for i in range(n)]
        acc=ls[0]
        for l in ls[1:]:
            acc=AND(acc,l)
        flags.append(acc)
    assert flags
    acc=flags[0]
    for l in flags[1:]:
        acc=-AND(-acc,-l)
    rows.append((acc,))
    return tuple(rows),gates,top


def evaluate_gates(x,n,gates):
    y={i+1:bool(x&(1<<i)) for i in range(n)}
    for v,a,b in gates:
        y[v]=(y[abs(a)]==(a>0)) and (y[abs(b)]==(b>0))
    return y


def audit():
    subsets=choices=0
    for n in (1,2,3):
        all_masks=set()
        full=(1<<(1<<n))-1
        ds=dict(distributions(n))
        for k,dist in ds.items():
            total=2**((n+1)*k)
            all_masks.update(dist)
            for x in range(1<<n):
                assert sum(v for p,v in dist.items() if p&(1<<x))*2**k==total
                for y in range(x):
                    assert sum(v for p,v in dist.items()
                               if p&(1<<x) and p&(1<<y))*2**(2*k)==total
        probes=greedy(n,all_masks)
        assert len(probes)==1<<n
        assert not detects(0,probes)
        for s in range(1,full+1):
            k=(s.bit_count()-1).bit_length()+1
            dist=ds[k]
            unique=sum(v for p,v in dist.items() if (p&s).bit_count()==1)
            assert 16*unique>=3*sum(dist.values())
            assert detects(s,probes)
            subsets+=1
            for v in range(n):
                z=probe_mask(n,((1<<v,0),))
                left=s&z
                right=s&(full^z)
                b=not detects(left,probes)
                assert right if b else left
                choices+=1
        print(f"n={n} affine_masks={len(all_masks)} exhaustive_advice={len(probes)}")
    n=3
    equations=tuple(product(range(1<<n),(0,1)))
    controls=0
    for a,b in product(equations,repeat=2):
        f,top=encode_hash(n,(a,b))
        p=probe_mask(n,(a,b))
        for x in range(1<<n):
            count=0
            base={i+1:bool(x&(1<<i)) for i in range(n)}
            for ext in product((False,True),repeat=top-n):
                y={**base,**dict(zip(range(n+1,top+1),ext))}
                count+=satisfies(f,y)
            assert count==((p>>x)&1)
            controls+=1
    # A fixed projected probe list is blind to a succinct nonempty
    # set, even though it includes the unrestricted parity query.
    n=6
    rng=Random(3802)
    probes=[probe_mask(n,())]
    for _ in range(16):
        rows=tuple((rng.randrange(1<<n),rng.randrange(2))
                   for _ in range(rng.randrange(1,n+1)))
        probes.append(probe_mask(n,rows))
    points=blind_points(n,probes)
    s=sum(1<<x for x in points)
    assert len(points)>=2 and not detects(s,probes)
    f,gates,top=membership(n,points)
    assert all(len(c)<=3 for c in f)
    for x in range(1<<n):
        y=evaluate_gates(x,n,gates)
        assert satisfies(f,y)==(x in points)
    assert subsets==273 and choices==798 and controls==2048
    print(f"blind_points={points} projected_probes={len(probes)} encoded_variables={top} encoded_clauses={len(f)}")
    print("F038_PARITY_FINGERPRINT_OK subsets=273 choices=798 hash_extensions=2048 blind_probes=17 projected_points=64")


if __name__=="__main__":
    audit()
