"""Certified affine/bijunctive interfaces and exact finite regression."""
from itertools import combinations, product
from collections import deque
from mathos.research.f038_witness_composition import seed
from mathos.research.f038_rule_certification import ROWS, satisfies

AFFINE=((1,0),(2,1),(3,0),(5,1),(6,0),(7,1),(9,0),(10,1),(12,0))
BINARY=((1,2),(-1,3),(-2,-3),(1,-3),(2,),(-1,))


def parity(a):
    return a.bit_count()&1


def eliminate(rows,private=0):
    basis={}
    for j,(a,b) in enumerate(rows):
        p=1<<j
        while a:
            q=a&private or a
            bit=q&-q
            if bit not in basis:
                basis[bit]=(a,b,p)
                break
            c,d,r=basis[bit]
            a^=c
            b^=d
            p^=r
        else:
            if b:
                return None,p
    return basis,None


def combination(rows,p):
    a=b=0
    while p:
        bit=p&-p
        p^=bit
        c,d=rows[bit.bit_length()-1]
        a^=c
        b^=d
    return a,b


def implied(basis,a):
    b=p=0
    while a:
        bit=a&-a
        if bit not in basis:
            return None
        c,d,r=basis[bit]
        a^=c
        b^=d
        p^=r
    return b,p


def project(rows,shared,private):
    basis,bad=eliminate(rows,private)
    if basis is None:
        return None,bad,None
    projected={bit:row for bit,row in basis.items() if not row[0]&private}
    low=[]
    vs=[]
    x=shared
    while x:
        bit=x&-x
        x^=bit
        vs.append(bit)
    for a in vs+[a|b for a,b in combinations(vs,2)]:
        got=implied(projected,a)
        if got is not None:
            b,p=got
            assert combination(rows,p)==(a,b)
            low.append((a,b,p))
    small,bad=eliminate(tuple((a,b) for a,b,p in low))
    assert bad is None
    return projected,tuple(low),len(small)==len(projected)


def binary_rows(low):
    f=[]
    for a,b,_ in low:
        vs=[i+1 for i in range(a.bit_length()) if a&(1<<i)]
        assert 1<=len(vs)<=2
        for vals in product((0,1),repeat=len(vs)):
            if sum(vals)%2!=b:
                f.append(tuple(-i if v else i for i,v in zip(vs,vals)))
    return tuple(f)


def affine_model(rows):
    basis,bad=eliminate(rows)
    if basis is None:
        return None
    w=0
    for bit,(a,b,p) in sorted(basis.items(),reverse=True):
        if parity(a&w)!=b:
            w|=bit
    assert all(parity(a&w)==b for a,b in rows)
    return w


def paths(f,n):
    adj={i:set() for v in range(1,n+1) for i in (v,-v)}
    for c in f:
        assert 1<=len(c)<=2
        a,b=c[0],c[-1]
        adj[-a].add(b)
        adj[-b].add(a)

    def path(a,b):
        parent={a:None}
        todo=deque([a])
        while todo and b not in parent:
            next_node=todo.popleft()
            for v in adj[next_node]:
                if v not in parent:
                    parent[v]=next_node
                    todo.append(v)
        if b not in parent:
            return None
        out=[]
        while b is not None:
            out.append(b)
            b=parent[b]
        return tuple(reversed(out))

    for v in range(1,n+1):
        a,b=path(v,-v),path(-v,v)
        if a is not None and b is not None:
            return a,b
    return None


def verify_paths(f,cert):
    a,b=cert
    assert len(a)>=2 and len(b)>=2
    assert a[0]==-a[-1] and b[0]==a[-1] and b[-1]==a[0]
    edges=set()
    for c in f:
        u,v=c[0],c[-1]
        edges.update(((-u,v),(-v,u)))
    assert all((u,v) in edges for path in cert for u,v in zip(path,path[1:]))


def hybrid_audit():
    systems=inconsistent=consistent=bij=non=projections=closure=cases=yes=no=0
    for m in range(1<<len(AFFINE)):
        rows=tuple(r for i,r in enumerate(AFFINE) if m&(1<<i))
        models=tuple(w for w in range(16) if all(parity(w&a)==b for a,b in rows))
        systems+=1
        proj,low,ok=project(rows,7,8)
        if not models:
            assert proj is None and combination(rows,low)==(0,1)
            inconsistent+=1
            continue
        consistent+=1
        assert proj is not None
        visible={w&7 for w in models}
        relaxed={w for w in range(8) if all(parity(w&a)==b for a,b,p in low)}
        for w in range(8):
            assert (w in visible)==all(parity(w&a)==b for a,b,p in proj.values())
            projections+=1
        closed=True
        for a,b,c in product(visible,repeat=3):
            closed &= ((a&b)|(a&c)|(b&c)) in visible
            closure+=1
        assert ok==(visible==relaxed)==closed
        bij+=ok
        non+=not ok
        if not ok:
            continue
        derived=binary_rows(low)
        for b in range(1<<len(BINARY)):
            f=tuple(c for i,c in enumerate(BINARY) if b&(1<<i))
            g=f+derived
            w=seed(g,3,())
            want=any(satisfies(f,v) for v in models)
            assert (w is not None)==want
            if want:
                full=affine_model(rows+tuple((1<<i,(w>>i)&1) for i in range(3)))
                assert full is not None and full&7==w and satisfies(f,full)
                assert all(parity(full&a)==rhs for a,rhs in rows)
            else:
                cert=paths(g,3)
                assert cert is not None
                verify_paths(g,cert)
            cases+=1
            yes+=want
            no+=not want
    assert (systems,inconsistent,consistent,bij,non,projections,closure,cases,yes,no)==(
        512,271,241,237,4,1928,4560,15168,6972,8196)
    print(f'F038_AFFINE_INTERFACE_OK systems={systems} inconsistent={inconsistent} '
          f'consistent={consistent} bijunctive={bij} non_bijunctive={non} '
          f'projection_checks={projections} closure_checks={closure} '
          f'hybrid_cases={cases} sat={yes} unsat={no}')


def reduce_cnf(f,n):
    top=n
    rows=[]
    clauses=[]
    blocks=[]
    for c in f:
        ids=tuple(range(top+1,top+len(c)+1))
        top+=len(c)
        row=(sum(1<<(i-1) for i in ids),1)
        local=tuple((-i,-j) for i,j in combinations(ids,2))+tuple(
            (-i,l) for i,l in zip(ids,c))
        rows.append(row)
        clauses.extend(local)
        blocks.append((ids,row,local))
    return top,tuple(rows),tuple(clauses),tuple(blocks)


def reduction_audit():
    cases=params=checks=source_sat=feasible=max_v=max_r=max_c=0
    for mask in range(1<<len(ROWS)):
        f=tuple(c for i,c in enumerate(ROWS) if mask&(1<<i))
        top,rows,clauses,blocks=reduce_cnf(f,3)
        assert all(a.bit_count()<=3 for a,b in rows)
        assert all(len(c)<=2 for c in clauses)
        ok=False
        for x in range(8):
            all_good=True
            w=x
            for c,(ids,(a,b),local) in zip(f,blocks):
                valid=False
                for t in range(1<<len(ids)):
                    z=x|sum(1<<(i-1) for j,i in enumerate(ids) if t&(1<<j))
                    got=parity(z&a)==b and satisfies(local,z)
                    assert got==(t.bit_count()==1 and satisfies(local,z))
                    if got and not valid:
                        w|=z
                    valid|=got
                    checks+=1
                assert valid==satisfies((c,),x)
                all_good &= valid
            assert all_good==satisfies(f,x)
            if all_good:
                assert satisfies(clauses,w) and all(parity(w&a)==b for a,b in rows)
            ok|=all_good
            params+=1
            feasible+=all_good
        cases+=1
        source_sat+=ok
        max_v=max(max_v,top)
        max_r=max(max_r,len(rows))
        max_c=max(max_c,len(clauses))
    assert (cases,params,checks,source_sat,feasible,max_v,max_r,max_c)==(
        4096,32768,851968,1360,2304,25,12,36)
    print(f'F038_AFFINE_MIXED_BARRIER_OK cases={cases} parameters={params} '
          f'local_checks={checks} source_sat={source_sat} feasible={feasible} '
          f'max_variables={max_v} max_rows={max_r} max_clauses={max_c}')


if __name__=='__main__':
    hybrid_audit()
    reduction_audit()
