"""Exact semantic translation constraints and bounded-width projection discovery."""
from mathos.research.f038_rule_certification import ROWS, satisfies
from mathos.research.f038_adaptive_rup import solve as adaptive


def brute(f,n):
    return next((w for w in range(1<<n) if satisfies(f,w)),None)


def two_decide(f,n):
    edges=[set() for _ in range(2*n)]
    def idx(l):
        return 2*(abs(l)-1)+int(l<0)
    for c in f:
        if not c:
            return False
        assert len(c)<=2
        a,b=(c[0],c[-1])
        a,b=idx(a),idx(b)
        edges[a^1].add(b)
        edges[b^1].add(a)
    def reach(i):
        seen={i}
        todo=[i]
        while todo:
            u=todo.pop()
            for v in edges[u]-seen:
                seen.add(v)
                todo.append(v)
        return seen
    return all(i+1 not in reach(i) or i not in reach(i+1)
               for i in range(0,2*n,2))


def two_solve(f,n):
    if not two_decide(f,n):
        return None
    g=tuple(f)
    w=0
    for i in range(1,n+1):
        trial=g+((-i,),)
        if two_decide(trial,n):
            g=trial
        else:
            g+=((i,),)
            w|=1<<(i-1)
    assert satisfies(f,w)
    return w


def oracle(f,n):
    if all(len(c)<=2 for c in f):
        return two_solve(f,n)
    return adaptive(f,n)[0]


def scope(c):
    return tuple(sorted(map(abs,c)))


def pin(ids,p):
    return tuple((v if p&(1<<j) else -v,) for j,v in enumerate(ids))


def block(ids,p):
    return tuple(-v if p&(1<<j) else v for j,v in enumerate(ids))


def pattern(w,ids):
    return sum(((w>>(v-1))&1)<<j for j,v in enumerate(ids))


def compile_repair(f,n,i,query=oracle):
    C=f[i]
    H=f[:i]+f[i+1:]
    bad=H+tuple((-l,) for l in C)
    queries=1
    forbidden=0
    if query(bad,n) is None:
        return (),queries,forbidden,True
    clauses=[block(scope(C),0)]
    for D in H:
        ids=scope(D)
        false=sum(1<<j for j,v in enumerate(ids) if -v in D)
        for p in range(1<<len(ids)):
            queries+=1
            if query(bad+pin(ids,p),n) is not None:
                clauses.append(block(ids,p^false))
                forbidden+=1
    return tuple(clauses),queries,forbidden,False


def valid_direction(f,n,i,v,query=oracle):
    # Search exactly for a counterexample to preservation on bad models.
    C=f[i]
    H=f[:i]+f[i+1:]
    bad=H+tuple((-l,) for l in C)
    for D in f:
        translated=tuple(-l if v&(1<<(abs(l)-1)) else l for l in D)
        if query(bad+tuple((-l,) for l in translated),n) is not None:
            return False
    return True


def discover(f,n,i,query=oracle):
    q,_,_,_=compile_repair(f,n,i,query)
    v=query(q,n)
    assert v is None or valid_direction(f,n,i,v,query)
    return v


def audit_fixture(rows,n):
    formulas=candidates=bad_empty=queries=forbidden=semantic=local=strict=0
    checks=sem_dirs=local_dirs=repairs=0
    for mask in range(1<<len(rows)):
        f=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        formulas+=1
        for i,C in enumerate(f):
            H=f[:i]+f[i+1:]
            bad=tuple(w for w in range(1<<n)
                      if satisfies(H,w) and not satisfies((C,),w))
            q,k,z,empty=compile_repair(f,n,i)
            assert empty==not_bad(bad)
            candidates+=1
            bad_empty+=empty
            queries+=k
            forbidden+=z
            se=lo=0
            for v in range(1<<n):
                expected=all(satisfies(f,w^v) for w in bad)
                pairwise=all(satisfies((C,),w) or (
                    satisfies((C,),w^v) and all(not satisfies((D,),w) or
                    satisfies((D,),w^v) for D in H))
                    for w in range(1<<n))
                assert satisfies(q,v)==expected
                assert not pairwise or expected
                if expected:
                    repairs+=len(bad)
                se+=expected
                lo+=pairwise
                checks+=1
            v=oracle(q,n)
            assert (v is not None)==bool(se)
            if v is not None:
                assert valid_direction(f,n,i,v)
            semantic+=bool(se)
            local+=bool(lo)
            strict+=bool(se) and not lo
            sem_dirs+=se
            local_dirs+=lo
    return (formulas,candidates,bad_empty,queries,forbidden,semantic,local,
            strict,checks,sem_dirs,local_dirs,repairs)


def not_bad(bad):
    return not bad


def reduction(D,n,co=True):
    z,w,r=n+1,n+2,n+3
    top=n+3+len(D)
    g=z if co else -z
    C=(z,w)
    H=[(-w,)]
    for j,(a,b,c) in enumerate(D):
        u=n+4+j
        H.extend(((g,a,u),(-u,b,c)))
    for q in range(1,top+1):
        if q not in (z,w):
            H.append((-g,-q))
    return (C,)+tuple(H),top,z,w,r


def reduction_audit():
    rows=tuple(tuple(-(i+1) if x&(1<<i) else i+1 for i in range(3))
               for x in range(8))
    sources=sat=unsat=projection_checks=fixed_checks=0
    for mask in range(256):
        D=tuple(c for i,c in enumerate(rows) if mask&(1<<i))
        want=brute(D,3) is not None
        sources+=1
        sat+=want
        unsat+=not want
        for co in (True,False):
            f,n,z,w,r=reduction(D,3,co)
            H=f[1:]
            good_z=1 if co else 0
            unique=(1<<(z-1)) if co else 0
            assert satisfies(H,unique)
            forced=H+((z if good_z else -z,),)
            assert oracle(forced,n)==unique
            # Verify uniqueness by excluding the known model in one query.
            exclude=tuple(-i if unique&(1<<(i-1)) else i for i in range(1,n+1))
            assert oracle(forced+(exclude,),n) is None
            for x in range(8):
                for free in (0,1):
                    pins=tuple((i if x&(1<<(i-1)) else -i,)
                               for i in range(1,4))
                    pins+=(((-z if co else z),),(r if free else -r,))
                    got=oracle(H+pins,n) is not None
                    assert got==satisfies(D,x)
                    projection_checks+=1
            if co:
                assert oracle(f,n)==unique
                assert valid_direction(f,n,0,1<<(z-1))==(not want)
                fixed_checks+=1
            else:
                assert (oracle(f,n) is not None)==want
    assert (sources,sat,unsat,projection_checks,fixed_checks)==(256,255,1,8192,256)
    print('F038_SEMANTIC_REPAIR_REDUCTIONS_OK sources=256 sat=255 unsat=1 '
          'projection_checks=8192 fixed_checks=256')


def audit():
    a=audit_fixture(ROWS,3)
    assert a==(4096,24576,18160,163216,32168,20556,9088,11468,196608,
               149184,16936,4716)
    print('F038_SEMANTIC_REPAIR_OK formulas=4096 candidates=24576 bad_empty=18160 '
          'queries=163216 forbidden=32168 semantic_exists=20556 local_exists=9088 '
          'strict=11468 direction_checks=196608 semantic_directions=149184 '
          'local_directions=16936 repairs=4716')
    rows=((-1,),(1,),(-2,),(2,),(-1,-2),(-1,2),(1,-2),(1,2))
    a=audit_fixture(rows,2)
    assert a==(256,1024,672,3936,944,792,304,488,4096,2840,400,160)
    print('F038_SEMANTIC_2CNF_OK formulas=256 candidates=1024 bad_empty=672 '
          'queries=3936 forbidden=944 semantic_exists=792 local_exists=304 '
          'strict=488 direction_checks=4096 semantic_directions=2840 '
          'local_directions=400 repairs=160')
    reduction_audit()


if __name__=='__main__':
    audit()
