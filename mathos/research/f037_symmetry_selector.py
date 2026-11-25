"""Safe direct choices by globally coordinated translation symmetries.

Local truth tables give an exact, polynomially discoverable subgroup
of semantic symmetries. This is not an exact semantic symmetry oracle.
"""
from itertools import combinations, product
from random import Random
from mathos.research.f037_log_backdoor import normalize, restrict, decide, satisfies


def tables(raw):
    f=normalize(raw)
    vs=sorted({abs(l) for c in f for l in c})
    idx={v:i for i,v in enumerate(vs)}
    groups={}
    for c in f:
        s=tuple(sorted({idx[abs(l)] for l in c}))
        groups.setdefault(s,[]).append(c)
    out=[]
    for s,rows in sorted(groups.items()):
        pos={vs[v]:j for j,v in enumerate(s)}
        allowed={a for a in range(1<<len(s))
                 if all(any(bool(a&(1<<pos[abs(l)]))==(l>0)
                            for l in c) for c in rows)}
        out.append((s,allowed))
    return vs,out


def project(mask,s):
    return sum(((mask>>v)&1)<<j for j,v in enumerate(s))


def insert(basis,mask):
    while mask:
        p=(mask&-mask).bit_length()-1
        if p in basis:
            mask^=basis[p]
        else:
            basis[p]=mask
            return True
    return False


def discover(raw):
    vs,groups=tables(raw)
    n=len(vs)
    equations={}
    for s,A in groups:
        T=[b for b in range(1<<len(s))
           if all((a^b) in A for a in A)]
        # T is a vector subspace. Its annihilator gives exactly
        # the local homogeneous constraints on a translation.
        for m in range(1,1<<len(s)):
            if all((m&b).bit_count()%2==0 for b in T):
                insert(equations,sum(1<<v for j,v in enumerate(s) if m&(1<<j)))
    generators={}
    for j in range(n):
        if j in equations:
            continue
        b=1<<j
        for p in sorted(equations,reverse=True):
            if (equations[p]&b).bit_count()%2:
                b|=1<<p
        assert all((b&e).bit_count()%2==0 for e in equations.values())
        insert(generators,b)
    masks=tuple(generators[p] for p in sorted(generators))
    assert check(raw,masks)
    return masks


def check(raw,masks):
    vs,groups=tables(raw)
    last=-1
    for b in masks:
        if type(b) is not int or not 0<b<(1<<len(vs)):
            return False
        p=(b&-b).bit_length()-1
        if p<=last:
            return False
        last=p
        for s,A in groups:
            h=project(b,s)
            if any((a^h) not in A for a in A):
                return False
    return True


def quotient(raw,masks):
    f=normalize(raw)
    assert check(f,masks)
    vs=sorted({abs(l) for c in f for l in c})
    fixed={vs[(b&-b).bit_length()-1]:False for b in masks}
    return restrict(f,fixed),fixed


def move_model(raw,masks,x):
    assert check(raw,masks) and satisfies(raw,x)
    vs=sorted({abs(l) for c in normalize(raw) for l in c})
    y=dict(x)
    for b in masks:
        p=(b&-b).bit_length()-1
        if y.get(vs[p],False):
            for i,v in enumerate(vs):
                if b&(1<<i):
                    y[v]=not y.get(v,False)
    h,fixed=quotient(raw,masks)
    assert all(not y.get(v,False) for v in fixed) and satisfies(raw,y)
    return y


def solve(raw,k):
    masks=discover(raw)
    h,fixed=quotient(raw,masks)
    status,evidence=decide(h,k)
    if status=='SAT':
        x={**evidence,**fixed}
        assert satisfies(raw,x)
        return status,x
    # No standalone UNSAT certificate is emitted by this wrapper.
    return status,None


def xor(a,b,c):
    return [tuple(-v if bit else v for v,bit in zip((a,b,c),(i,j,1-(i^j))))
            for i,j in product((0,1),repeat=2)]


def dense(t,bad):
    f=[]
    outputs=[]
    for i in range(t):
        a,b,c,d=range(4*i+1,4*i+5)
        f.extend(xor(a,b,c)+xor(a,b,d))
        outputs.extend((c,d))
    f.extend((-u,-v) for u,v in combinations(outputs,2) if (u-1)//4!=(v-1)//4)
    f.extend(((3,),(-4,) if bad else (4,)))
    return tuple(f)


def transform(f,rng):
    vs=sorted({abs(l) for c in f for l in c})
    perm=list(vs)
    rng.shuffle(perm)
    mp={v:w*rng.choice((-1,1)) for v,w in zip(vs,perm)}
    g=[tuple(mp[abs(l)]*(1 if l>0 else -1) for l in c) for c in f]
    rng.shuffle(g)
    return tuple(g)


def run():
    rng=Random(3706)
    nontrivial=0
    models=0
    for _ in range(256):
        f=tuple(tuple(v*rng.choice((-1,1)) for v in rng.sample(range(1,6),rng.randrange(1,4)))
                for _ in range(rng.randrange(1,14)))
        masks=discover(f)
        nontrivial+=bool(masks)
        vs,A=tables(f)
        # Independently enumerate ALL simultaneous local translations.
        T={b for b in range(1<<len(vs))
           if all(all((a^project(b,s)) in allowed for a in allowed)
                  for s,allowed in A)}
        span={0}
        for b in masks:
            span|={a^b for a in span}
        assert span==T
        h,fixed=quotient(f,masks)
        originals=[]
        for bits in product((False,True),repeat=len(vs)):
            x=dict(zip(vs,bits))
            if satisfies(f,x):
                originals.append(x)
                move_model(f,masks,x)
                models+=1
        residual=any(satisfies(h,dict(zip(vs,bits)))
                     for bits in product((False,True),repeat=len(vs)))
        assert residual==bool(originals)
    for t in (2,4,8,16,32,64):
        for bad in (False,True):
            f=transform(dense(t,bad),rng)
            masks=discover(f)
            h,fixed=quotient(f,masks)
            assert len(masks)==t and all(len(c)<=2 for c in h)
            assert decide(f,0)[0]=='UNKNOWN'
            status,evidence=solve(f,0)
            assert status==('UNSAT' if bad else 'SAT')
    f=dense(2,False)
    masks=discover(f)
    assert not check(f,(0,))
    assert not check(f,(masks[0],masks[0]))
    assert not check(f,(1<<2,))
    print(f"random_nontrivial={nontrivial} models_transported={models}")
    print("F037_SYMMETRY_SELECTOR_OK random=256 dense=12 max_variables=256 rejection=3")


if __name__=="__main__":
    run()
