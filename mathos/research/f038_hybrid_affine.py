"""Explicit parity extraction, certified hybrid propagation, and projected-rank search."""
from collections import defaultdict
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_resolution_certificate import split_cube, encode


def parity(w):
    return w.bit_count()&1


def mask_of(c):
    return sum(1<<(abs(l)-1) for l in c)


def extract(f):
    groups=defaultdict(list)
    for i,c in enumerate(f):
        assert len(set(map(abs,c)))==len(c) and all(c)
        if 1<=len(c)<=3:
            groups[tuple(sorted(map(abs,c)))].append(i)
    rows=[]
    used=set()
    for scope,ids in groups.items():
        for bad in (0,1):
            selected=tuple(i for i in ids if parity(sum(
                1<<(abs(l)-1) for l in f[i] if l<0))==bad)
            patterns={tuple(sorted(f[i])) for i in selected}
            if len(patterns)==1<<(len(scope)-1):
                rows.append((sum(1<<(v-1) for v in scope),1-bad,selected))
                used.update(selected)
    rest=tuple(i for i in range(len(f)) if i not in used)
    return tuple(rows),rest


def verify_partition(f,rows,rest):
    seen=set()
    for a,b,ids in rows:
        if a<=0 or a.bit_count()>3 or b not in (0,1) or not ids:
            return False
        if any(i<0 or i>=len(f) or i in seen for i in ids):
            return False
        if len(set(ids))!=len(ids):
            return False
        patterns=set()
        for i in ids:
            c=f[i]
            if len(set(map(abs,c)))!=len(c) or not all(c) or mask_of(c)!=a:
                return False
            w=sum(1<<(abs(l)-1) for l in c if l<0)
            if parity(w)==b:
                return False
            patterns.add(w)
        if len(patterns)!=1<<(a.bit_count()-1):
            return False
        seen.update(ids)
    return len(set(rest))==len(rest) and not seen.intersection(rest) and (
        seen|set(rest))==set(range(len(f)))


def reduce(rows,known=0,value=0):
    basis={}
    for j,(a,b,_) in enumerate(rows):
        p=1<<j
        b^=parity(a&value)
        a&=~known
        while a:
            bit=a&-a
            if bit not in basis:
                basis[bit]=(a,b,p)
                break
            c,d,q=basis[bit]
            a^=c
            b^=d
            p^=q
        else:
            if b:
                return None,p
    for bit in sorted(basis,reverse=True):
        a,b,p=basis[bit]
        for v in basis:
            if v<bit and basis[v][0]&bit:
                c,d,q=basis[v]
                basis[v]=(c^a,d^b,q^p)
    return basis,None


def rank(rows):
    basis,bad=reduce(tuple((a,0,()) for a in rows))
    assert bad is None
    return len(basis)


def dimension(rows,db,n):
    basis,bad=reduce(rows)
    if basis is None:
        return -1
    interface=0
    for c in db:
        interface|=mask_of(c)
    private=((1<<n)-1)^interface
    return interface.bit_count()-len(basis)+rank(a&private for a,b,p in rows)


def combination(rows,p):
    a=b=0
    if p<=0 or p>>len(rows):
        return None
    while p:
        bit=p&-p
        p^=bit
        c,d,_=rows[bit.bit_length()-1]
        a^=c
        b^=d
    return a,b


def pins(p,n):
    known=value=0
    for l in p:
        if not 1<=abs(l)<=n:
            return None
        bit=1<<(abs(l)-1)
        if known&bit:
            return None
        known|=bit
        if l>0:
            value|=bit
    return known,value


def true(l,known,value):
    bit=1<<(abs(l)-1)
    return bool(known&bit) and bool(value&bit)==(l>0)


def propagate(rows,db,n,p):
    known,value=pins(p,n)
    trace=[]
    while True:
        basis,bad=reduce(rows,known,value)
        if basis is None:
            trace.append(('x',bad,0))
            return None,tuple(trace)
        forced=next(((bit,b,proof) for bit,(a,b,proof) in sorted(basis.items())
                     if a==bit),None)
        if forced is not None:
            bit,b,proof=forced
            l=bit.bit_length()*(1 if b else -1)
            trace.append(('x',proof,l))
            known|=bit
            if b:
                value|=bit
            continue
        for i,c in enumerate(db):
            if any(true(l,known,value) for l in c):
                continue
            u=[l for l in c if not known&(1<<(abs(l)-1))]
            if not u:
                trace.append(('c',i,0))
                return None,tuple(trace)
            if len(u)==1:
                l=u[0]
                trace.append(('c',i,l))
                bit=1<<(abs(l)-1)
                known|=bit
                if l>0:
                    value|=bit
                break
        else:
            return (known,value,basis),tuple(trace)


def verify_conflict(rows,db,n,p,trace):
    initial=pins(p,n)
    if initial is None or not trace:
        return False
    known,value=initial
    for j,(kind,ref,l) in enumerate(trace):
        if l and (not 1<=abs(l)<=n or known&(1<<(abs(l)-1))):
            return False
        if kind=='x':
            eq=combination(rows,ref)
            if eq is None:
                return False
            a,b=eq
            rem=a&~known
            rhs=b^parity(a&value)
            if l:
                if rem!=1<<(abs(l)-1) or rhs!=int(l>0):
                    return False
            elif rem or not rhs:
                return False
        elif kind=='c':
            if not 0<=ref<len(db):
                return False
            c=db[ref]
            if any(true(v,known,value) for v in c):
                return False
            u=[v for v in c if not known&(1<<(abs(v)-1))]
            if u!=([l] if l else []):
                return False
        else:
            return False
        if not l:
            return j==len(trace)-1
        bit=1<<(abs(l)-1)
        known|=bit
        if l>0:
            value|=bit
    return False


def verify_proof(f,n,rows,rest,proof):
    if not verify_partition(f,rows,rest):
        return False
    db=[f[i] for i in rest]
    for c,trace in proof:
        if not verify_conflict(rows,db,n,tuple(-l for l in c),trace):
            return False
        db.append(c)
    return True


def solve(f,n):
    rows,rest=extract(f)
    assert verify_partition(f,rows,rest)
    db=[f[i] for i in rest]
    r=dimension(rows,db,n)
    learned=[]
    nodes=conflicts=0

    def add(p,trace=None):
        if trace is None:
            state,trace=propagate(rows,db,n,p)
            assert state is None
        assert verify_conflict(rows,db,n,p,trace)
        c=tuple(-l for l in p)
        learned.append((c,trace))
        db.append(c)

    def visit(p):
        nonlocal nodes,conflicts
        nodes+=1
        state,trace=propagate(rows,db,n,p)
        if state is None:
            conflicts+=1
            add(p,trace)
            return None
        known,value,basis=state
        pending=[c for c in db if not any(true(l,known,value) for l in c)]
        if not pending:
            w=value
            for bit,(a,b,_) in basis.items():
                if b:
                    w|=bit
            assert satisfies(f,w)
            return w
        counts=[0]*(n+1)
        for c in pending:
            for l in c:
                if not known&(1<<(abs(l)-1)):
                    counts[abs(l)]+=1
        v=max(range(1,n+1),key=lambda i:(counts[i],-i))
        assert counts[v]>0
        w=visit(p+(-v,))
        if w is not None:
            return w
        w=visit(p+(v,))
        if w is not None:
            return w
        add(p)
        return None

    w=visit(())
    assert nodes<=(1 if r<0 else (1<<(r+1))-1)
    assert w is not None or (learned and learned[-1][0]==())
    assert verify_proof(f,n,rows,rest,learned)
    return w,rows,rest,tuple(learned),(nodes,conflicts,r)


def exhaustive(fixture):
    yes=no=nodes=adds=conflicts=rowsum=residual=max_nodes=checks=0
    for mask in range(1<<len(fixture)):
        f=tuple(c for i,c in enumerate(fixture) if mask&(1<<i))
        w,rows,rest,proof,(nn,cc,r)=solve(f,3)
        models=[]
        affine=[]
        interface=0
        db=tuple(f[i] for i in rest)
        for c in db:
            interface|=mask_of(c)
        for x in range(8):
            a=all(parity(x&m)==b for m,b,p in rows)
            if a:
                affine.append(x&interface)
            got=satisfies(f,x)
            assert got==(a and satisfies(db,x))
            if got:
                models.append(x)
            checks+=1
        assert (w is not None)==bool(models)
        if w is not None:
            assert w in models
        else:
            assert proof and proof[-1][0]==()
        assert r==(len(set(affine)).bit_length()-1 if affine else -1)
        yes+=bool(models)
        no+=not models
        nodes+=nn
        adds+=len(proof)
        conflicts+=cc
        rowsum+=len(rows)
        residual+=len(rest)
        max_nodes=max(max_nodes,nn)
    return yes,no,nodes,adds,conflicts,rowsum,residual,max_nodes,checks


def audit():
    a=exhaustive(ROWS)
    assert a==(1360,2736,4402,2752,2752,12544,11264,3,32768)
    print('F038_HYBRID_AFFINE_OK formulas=4096 sat=1360 unsat=2736 '
          'nodes=4402 learned=2752 conflicts=2752 rows=12544 residual=11264 '
          'max_nodes=3 extraction_checks=32768')
    fixture=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
                  for w in range(8))
    a=exhaustive(fixture)
    assert a==(255,1,832,97,82,32,896,7,2048)
    print('F038_HYBRID_FULL_WIDTH_OK formulas=256 sat=255 unsat=1 '
          'nodes=832 learned=97 conflicts=82 rows=32 residual=896 '
          'max_nodes=7 extraction_checks=2048')
    for n in (3,8,16,32):
        f=tuple(c for i in range(1,n) for c in ((-i,i+1),(i,-i-1)))+tuple(
            (i,i+1,i+2) for i in range(1,n-1))
        w,rows,rest,proof,(nodes,conflicts,r)=solve(f,n)
        assert w==(1<<n)-1 and r==1 and nodes==3 and len(proof)==1
    print('F038_HYBRID_RANK_ONE_OK sizes=3,8,16,32 nodes_each=3 learned_each=1')
    for d in range(2,6):
        n,edges=split_cube(d)
        z=len(edges)+1
        base=encode(n,edges,1)
        for b in (0,1):
            f=base+((z if b else -z,),)
            w,rows,rest,proof,(nodes,conflicts,r)=solve(f,z)
            assert not rest and nodes==1
            assert (w is not None)==bool(b)
            if b:
                assert r==0 and not proof and satisfies(f,w)
            else:
                assert r==-1 and len(proof)==1 and proof[0][0]==()
                assert proof[0][1][-1][0]=='x'
                # Corrupt the algebraic provenance reference.
                trace=list(proof[0][1])
                kind,ref,l=trace[-1]
                trace[-1]=(kind,0,l)
                assert not verify_proof(f,z,rows,rest,(((),tuple(trace)),))
    print('F038_HYBRID_TSEITIN_ESCAPE_OK dimensions=2,3,4,5 '
          'branch_checks=8 nodes_each=1 wrong_learned_each=1 corrupt_rejected=4')


if __name__=='__main__':
    audit()
