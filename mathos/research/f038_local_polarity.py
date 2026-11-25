"""Local unate seeds and opposing-unate union barrier; finite regression."""
from mathos.research.f038_factored_interface import vals, reconstruct
from mathos.research.f038_horn_cover import satisfies
from mathos.research.f038_monotone_choice import sat, restrict
from mathos.research.f038_symbolic_interface import address_reduction, check_decomposition

ROWS=((1,2,-4),(-1,4),(2,4),(-2,-4),(1,-2,5),(-1,-5),
      (3,5),(-3,-5),(2,3,-6),(-2,6),(-3,6),(1,-3))
MATRIX=((-1,),(1,),(-2,),(2,),(3,),(-1,-2),(2,3),(-1,2,3),(1,-2,3))


def occurrences(f):
    pos=neg=0
    for c in f:
        for l in c:
            bit=1<<(abs(l)-1)
            if l>0:
                pos|=bit
            else:
                neg|=bit
    return pos,neg


def partition(f,u,e):
    """Declared universal/existential masks; retain isolated existential bits."""
    parent={v:v for v in vals(e) if v and not v&(v-1)}

    def root(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]]
            v=parent[v]
        return v

    def scope(c):
        v=0
        for l in c:
            v|=1<<(abs(l)-1)
        assert not v&~(u|e)
        return v

    for c in f:
        bits=[v for v in parent if scope(c)&v]
        if bits:
            for v in bits[1:]:
                parent[root(v)]=root(bits[0])
    groups={}
    for v in parent:
        key=root(v)
        if key not in groups:
            groups[key]=[0,[]]
        groups[key][0]|=v
    parameter_only=[]
    for c in f:
        bits=scope(c)&e
        if bits:
            groups[root(bits&-bits)][1].append(c)
        else:
            parameter_only.append((0,(c,)))
    return tuple((v,tuple(cs)) for v,cs in groups.values())+tuple(parameter_only)


def local_seeds(f,u,bags,children,fs):
    pos,neg=occurrences(f)
    h=u&pos&neg
    worst=u&neg&~pos
    return h,{a:reconstruct(bags,children,fs,u,a|worst) for a in vals(h)}


def positive():
    families=total=non=blocks=probes=missing=checks=outputs=max_local=max_global=0
    u,e=7,56
    for mask in range(4096):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        ps=partition(f,u,e)
        pos,neg=occurrences(f)
        max_global=max(max_global,1<<(u&pos&neg).bit_count())
        tables=[]
        valid=True
        for ev,g in ps:
            p,n=occurrences(g)
            uv=(p|n)&u
            scope=uv|ev
            h,table=local_seeds(g,uv,(scope,),((),),(g,))
            # Independently check the exact local slice invariant.
            for a,w in table.items():
                success=w is not None
                assert success==all(any(satisfies(g,x|y) for y in vals(ev))
                                    for x in vals(uv) if x&h==a)
                if success:
                    assert all(satisfies(g,x|(w&ev))
                               for x in vals(uv) if x&h==a)
                probes+=1
                missing+=not success
                valid &= success
            tables.append((ev,h,table))
            blocks+=1
            max_local=max(max_local,len(table))
        actual=True
        for x in range(8):
            want=any(satisfies(f,x|y) for y in vals(e))
            actual &= want
            checks+=1
            w=x
            for ev,h,table in tables:
                v=table[x&h]
                if v is None:
                    break
                w|=v&ev
            else:
                assert satisfies(f,w) and w&u==x
                outputs+=1
        assert actual==valid
        families+=1
        total+=valid
        non+=not valid
    assert (families,total,non,blocks,probes,missing,checks,outputs,max_local,max_global)==(
        4096,648,3448,14336,22272,6144,32768,8648,4,8)
    print(f'F038_LOCAL_POLARITY_OK families={families} total={total} non_total={non} '
          f'blocks={blocks} seed_probes={probes} missing={missing} global_checks={checks} '
          f'outputs={outputs} max_local={max_local} max_global={max_global}')


def split(d,n):
    p=tuple(tuple(l if l>0 else n-l for l in c) for c in d)
    p+=tuple((i,n+i) for i in range(1,n+1))
    q=tuple((-i,-n-i) for i in range(1,n+1))
    return p,q


def negative():
    matrices=source_sat=source_unsat=params=checks=total=pc=nc=uc=max_v=max_c=0
    n=3
    u=(1<<(2*n))-1
    for mask in range(1<<len(MATRIX)):
        d=tuple(c for i,c in enumerate(MATRIX) if mask&(1<<i))
        p,q=split(d,n)
        enc=[]
        for j,mat in enumerate((p,q)):
            top,address,bags,children,fs=address_reduction(mat,2*n)
            check_decomposition(top,bags,children,fs)
            assert max(b.bit_count() for b in bags)<=len(address)+3
            f=tuple(c for local in fs for c in local)
            pos,neg=occurrences(f)
            assert not (pos if j==0 else neg)&u
            enc.append(f)
            max_v=max(max_v,top)
            max_c=max(max_c,len(f))
        valid=True
        split_sat=False
        for x in range(1<<(2*n)):
            pins={i+1:bool(x&(1<<i)) for i in range(2*n)}
            a,b=(sat(restrict(f,pins)) for f in enc)
            assert (a,b)==(not satisfies(p,x),not satisfies(q,x))
            split_sat|=satisfies(p,x) and satisfies(q,x)
            valid &= a or b
            params+=1
            checks+=2
            pc+=a
            nc+=b
            uc+=a or b
        want=any(satisfies(d,x) for x in range(1<<n))
        assert split_sat==want and valid==(not want)
        matrices+=1
        source_sat+=want
        source_unsat+=not want
        total+=valid
    assert (matrices,source_sat,source_unsat,params,checks,total,pc,nc,uc,max_v,max_c)==(
        512,272,240,32768,65536,240,27984,18944,32208,56,71)
    print(f'F038_OPPOSITE_UNATE_UNION_OK matrices={matrices} sat={source_sat} '
          f'unsat={source_unsat} parameters={params} projection_checks={checks} '
          f'total={total} positive_violations={pc} negative_violations={nc} '
          f'union_covered={uc} max_variables={max_v} max_clauses={max_c}')


if __name__=='__main__':
    positive()
    negative()
