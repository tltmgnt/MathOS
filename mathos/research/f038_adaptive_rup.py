"""Adaptive RUP-certified search and bounded trace-verifier compiler."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_prefix_clock import Gates, evaluate_all, bad_family


def propagate(db,n,p):
    a=[0]*(n+1)
    for l in p:
        i,b=abs(l),1 if l>0 else -1
        if a[i]==-b:
            return None
        a[i]=b
    while True:
        changed=False
        for c in db:
            if any(a[abs(l)]==(1 if l>0 else -1) for l in c):
                continue
            u=[l for l in c if not a[abs(l)]]
            if not u:
                return None
            if len(u)==1:
                l=u[0]
                a[abs(l)]=1 if l>0 else -1
                changed=True
        if not changed:
            return a


def solve(f,n):
    db=list(f)
    learned=[]
    nodes=branches=conflicts=0

    def add(p):
        c=tuple(-l for l in p)
        assert propagate(db,n,p) is None
        db.append(c)
        learned.append(c)

    def visit(p):
        nonlocal nodes,branches,conflicts
        nodes+=1
        a=propagate(db,n,p)
        if a is None:
            conflicts+=1
            add(p)
            return None
        pending=[c for c in db if not any(
            a[abs(l)]==(1 if l>0 else -1) for l in c)]
        if not pending:
            return sum(1<<(i-1) for i in range(1,n+1) if a[i]==1)
        counts=[0]*(n+1)
        for c in pending:
            for l in c:
                if not a[abs(l)]:
                    counts[abs(l)]+=1
        v=max((i for i in range(1,n+1) if not a[i]),
              key=lambda i:(counts[i],-i))
        assert counts[v]>0
        branches+=1
        w=visit(p+(-v,))
        if w is not None:
            return w
        w=visit(p+(v,))
        if w is not None:
            return w
        add(p)
        return None

    w=visit(())
    assert (w is None and learned and learned[-1]==()) or (
        w is not None and satisfies(f,w))
    return w,tuple(learned),(nodes,branches,conflicts)


def check_trace(f,n,trace):
    db=list(f)
    for c in trace:
        if any(not 1<=abs(l)<=n for l in c) or len(set(map(abs,c)))!=len(c):
            return False
        if propagate(db,n,tuple(-l for l in c)) is not None:
            return False
        db.append(c)
    return True


def compile_trace(rows,n,T):
    assert T>=1
    g=Gates(len(rows)+2*n*T)
    lits=tuple(l for i in range(1,n+1) for l in (i,-i))
    pres=list(range(2,2+len(rows)))
    db=[(e,tuple(1 if l in c else -1 for l in lits))
        for e,c in zip(pres,rows)]
    checks=[]
    last=None
    for j in range(T):
        start=2+len(rows)+2*n*j
        c=tuple(range(start,start+2*n))
        last=c
        checks.extend(-g.and2(c[2*i],c[2*i+1]) for i in range(n))
        pos=[c[2*i+1] for i in range(n)]
        neg=[c[2*i] for i in range(n)]

        def false(l):
            return neg[l-1] if l>0 else pos[-l-1]

        for _ in range(n):
            pp=[[v] for v in pos]
            nn=[[v] for v in neg]
            for e,members in db:
                fs=[g.disj((-b,false(l))) for l,b in zip(lits,members)]
                for i,l in enumerate(lits):
                    derived=g.conj([e,members[i]]+fs[:i]+fs[i+1:])
                    (pp if l>0 else nn)[abs(l)-1].append(derived)
            pos=[g.disj(v) for v in pp]
            neg=[g.disj(v) for v in nn]
        bad=g.disj([g.and2(p,q) for p,q in zip(pos,neg)]+[
            g.conj([e]+[g.disj((-b,false(l))) for l,b in zip(lits,members)])
            for e,members in db])
        checks.append(bad)
        db.append((1,c))
    valid=g.conj(checks)
    refute=g.and2(valid,g.conj(-b for b in last))
    return g,valid,refute


def exhaustive(rows,n):
    yes=no=nodes=branches=conflicts=adds=sat_adds=unsat_adds=maximum=0
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        w,trace,(a,b,c)=solve(f,n)
        models=tuple(x for x in range(1<<n) if satisfies(f,x))
        assert (w is not None)==bool(models)
        assert check_trace(f,n,trace)
        if w is None:
            assert trace and trace[-1]==()
            no+=1
            unsat_adds+=len(trace)
        else:
            assert w in models
            yes+=1
            sat_adds+=len(trace)
        nodes+=a
        branches+=b
        conflicts+=c
        adds+=len(trace)
        maximum=max(maximum,a)
    return yes,no,nodes,branches,conflicts,adds,sat_adds,unsat_adds,maximum


def audit():
    r=exhaustive(ROWS,3)
    assert r==(1360,2736,4415,303,2752,2752,16,2736,3)
    print('F038_ADAPTIVE_RUP_OK formulas=4096 sat=1360 unsat=2736 '
          'nodes=4415 branches=303 conflicts=2752 learned=2752 '
          'sat_learned=16 unsat_learned=2736 max_nodes=3')
    rows=tuple(tuple(-(i+1) if w&(1<<i) else i+1 for i in range(3))
               for w in range(8))
    r=exhaustive(rows,3)
    assert r[:6]==(255,1,850,510,85,103) and r[-1]==7
    print('F038_ADAPTIVE_FULL_WIDTH_OK formulas=256 sat=255 unsat=1 '
          'nodes=850 branches=510 conflicts=85 learned=103 max_nodes=7')
    counts=[]
    for m in range(1,7):
        f,n=bad_family(m)
        w,trace,(nodes,_,_)=solve(f,n)
        assert w is not None and satisfies(f,w) and w&1
        assert check_trace(f,n,trace) and len(trace)==3
        assert nodes==m+5
        counts.append(nodes)
    print('F038_ADAPTIVE_PREFIX_ESCAPE_OK families=6 nodes='+
          ','.join(map(str,counts))+' learned_each=3')


def compiler_audit():
    rows=((1,2),(1,-2),(-1,2),(-1,-2))
    g,valid,refute=compile_trace(rows,2,2)
    value=evaluate_all(g)
    a,b=value(valid),value(refute)
    ok=proof=nonempty=invalid_norm=0
    for mask in range(16):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        for t in range(256):
            trace=[]
            for j in range(2):
                trace.append(tuple(l for i,l in enumerate((1,-1,2,-2))
                                   if t&(1<<(4*j+i))))
            norm=all(len(set(map(abs,c)))==len(c) for c in trace)
            want=check_trace(f,2,trace)
            ref=want and not trace[-1]
            idx=mask|(t<<4)
            assert bool(a&(1<<idx))==want
            assert bool(b&(1<<idx))==ref
            if ref:
                assert not any(satisfies(f,w) for w in range(4))
            ok+=want
            proof+=ref
            nonempty+=want and bool(trace[-1])
            invalid_norm+=not norm
    assert (ok,proof,nonempty,invalid_norm)==(216,4,212,2800)
    assert all(len(c)<=3 for c in g.cnf+[(refute,)])
    print('F038_RUP_TRACE_COMPILER_OK patterns=4096 valid=216 '
          'refutations=4 valid_nonempty=212 invalid_normalized=2800')


if __name__=='__main__':
    audit()
    compiler_audit()
