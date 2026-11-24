"""F026: exact dynamic programming on a supplied primal tree decomposition.

Table entries are assignments to a bag that extend to its entire subtree.
The checker validates coverage and running intersection before computing.
No universal width guarantee or formal Python refinement is claimed.
"""
from itertools import product
from mathos.research.tga_proctor_factor_decomposition import normalize
from mathos.research.tga_proctor_unrestricted_scope import evaluate


def prepare(n, clauses, bags, edges):
    clauses,_=normalize(n,clauses)
    bags=tuple(tuple(b) for b in bags)
    if not bags:
        raise ValueError("at least one bag required")
    if any(any(type(v) is not int or not 1<=v<=n for v in b)
           or len(b)!=len(set(b)) for b in bags):
        raise ValueError("invalid bag")
    bags=tuple(tuple(sorted(b)) for b in bags)
    sets=tuple(map(set,bags))
    adj=[[] for _ in bags]
    seen_edges=set()
    for a,b in edges:
        if (type(a) is not int or type(b) is not int or
            not 0<=a<len(bags) or not 0<=b<len(bags) or a==b):
            raise ValueError("invalid tree edge")
        e=tuple(sorted((a,b)))
        if e in seen_edges:
            raise ValueError("duplicate edge")
        seen_edges.add(e)
        adj[a].append(b)
        adj[b].append(a)
    parent={0:-1}
    order=[0]
    for a in order:
        for b in sorted(adj[a]):
            if b==parent[a]:
                continue
            if b in parent:
                raise ValueError("cycle")
            parent[b]=a
            order.append(b)
    if len(order)!=len(bags):
        raise ValueError("disconnected decomposition")
    locations={}
    for i,bag in enumerate(bags):
        for v in bag:
            locations.setdefault(v,set()).add(i)
    # Isolated original variables may be absent; they are set false.
    for v,indices in locations.items():
        root=min(indices)
        reached={root}
        stack=[root]
        while stack:
            a=stack.pop()
            for b in adj[a]:
                if b in indices and b not in reached:
                    reached.add(b)
                    stack.append(b)
        if reached!=indices:
            raise ValueError("running intersection violated")
    assigned=[[] for _ in bags]
    for c in clauses:
        variables={abs(l) for l in c}
        j=next((i for i,b in enumerate(sets) if variables<=b),None)
        if j is None:
            raise ValueError("uncovered clause")
        assigned[j].append(c)
    children=[[] for _ in bags]
    for j in order[1:]:
        children[parent[j]].append(j)
    return clauses,bags,order,parent,children,assigned


def local_ok(cs,values):
    return all(any(values[abs(l)]==(l>0) for l in c) for c in cs)


def tables_for(bags,order,parent,children,assigned):
    tables=[None]*len(bags)
    projections={}
    visited=lookups=projection_entries=0
    for i in reversed(order):
        table=[]
        for bits in product((False,True),repeat=len(bags[i])):
            visited+=1
            values=dict(zip(bags[i],bits))
            if not local_ok(assigned[i],values):
                continue
            feasible=True
            for j in children[i]:
                shared,index=projections[j]
                lookups+=1
                if tuple(values[v] for v in shared) not in index:
                    feasible=False
                    break
            if feasible:
                table.append(bits)
        tables[i]=tuple(table)
        if parent[i]!=-1:
            shared=tuple(v for v in bags[i] if v in bags[parent[i]])
            pos=tuple(bags[i].index(v) for v in shared)
            index={}
            for bits in table:
                projection_entries+=1
                index.setdefault(tuple(bits[k] for k in pos),bits)
            projections[i]=(shared,index)
    return tuple(tables),projections,dict(table_candidates=visited,
        child_lookups=lookups,projection_entries=projection_entries)


def solve(n,clauses,bags,edges):
    cs,bags,order,parent,children,assigned=prepare(n,clauses,bags,edges)
    tables,projections,counts=tables_for(bags,order,parent,children,assigned)
    result={"sat":bool(tables[0]),"witness":(),"tables":tables,
            "max_bag_size":max(map(len,bags)),**counts}
    if not tables[0]:
        return result
    chosen={0:tables[0][0]}
    witness={}
    for i in order:
        values=dict(zip(bags[i],chosen[i]))
        for v,b in values.items():
            if v in witness and witness[v]!=b:
                raise AssertionError("inconsistent bag witnesses")
            witness[v]=b
        for j in children[i]:
            shared,index=projections[j]
            chosen[j]=index[tuple(values[v] for v in shared)]
    x=tuple(witness.get(v,False) for v in range(1,n+1))
    if not evaluate(cs,x):
        raise AssertionError("invalid global witness")
    return {**result,"witness":x}


def verify(n,clauses,bags,edges,result):
    """Independent recurrence check, using full child-table scans, not indices."""
    cs,bags,order,parent,children,assigned=prepare(n,clauses,bags,edges)
    try:
        if result["sat"] is True:
            x=result["witness"]
            return len(x)==n and all(v in (0,1) for v in x) and evaluate(cs,x)
        if result["sat"] is not False:
            return False
        ts=result["tables"]
        if len(ts)!=len(bags):
            return False
        for i in reversed(order):
            expected=[]
            for bits in product((False,True),repeat=len(bags[i])):
                values=dict(zip(bags[i],bits))
                if local_ok(assigned[i],values) and all(
                    any(all(values[v]==b for v,b in zip(bags[j],t) if v in values)
                        for t in ts[j]) for j in children[i]):
                    expected.append(bits)
            if tuple(map(tuple,ts[i]))!=tuple(expected):
                return False
        return not ts[0]
    except (KeyError,TypeError,ValueError,IndexError):
        return False


def controls():
    base=((1,1,1),(-1,-1,-1),(1,-2,1),(-1,2,-1))
    fixtures=[(0,(),((),),()),(3,(),((1,),(),(3,)),((0,1),(1,2)))]
    fixtures += [(2,(a,b),((1,2),),()) for a,b in product(base,repeat=2)]
    # All sign patterns on a two-bag chain, including repeated literals.
    for a,b,c,d in product((-1,1),repeat=4):
        fixtures.append((4,((a,2*b,2*b),(2*c,3*d,4),(1,1,1),(-4,-4,-4)),
                         ((1,2),(2,3,4)),((0,1),)))
    # Contradiction crossing a bag interface.
    fixtures.append((3,((1,1,1),(-1,2,2),(-2,-2,-2)),
                     ((1,),(1,2),(2,3)),((0,1),(1,2))))
    counts=dict(cases=0,sat=0,unsat=0,table_candidates=0,child_lookups=0,
                projection_entries=0)
    for n,cs,bags,edges in fixtures:
        r=solve(n,cs,bags,edges)
        brute=any(evaluate(cs,x) for x in product((False,True),repeat=n))
        assert r["sat"]==brute and verify(n,cs,bags,edges,r)
        assert r["table_candidates"]==sum(2**len(b) for b in bags)
        if not brute:
            bad=list(r["tables"])
            bad[0]=((False,)*len(bags[0]),)
            assert not verify(n,cs,bags,edges,{**r,"tables":bad})
        counts["cases"]+=1
        counts["sat" if brute else "unsat"]+=1
        for k in ("table_candidates","child_lookups","projection_entries"):
            counts[k]+=r[k]
    # Large low-width connected chain, not brute-force enumerated.
    n=64
    cs=tuple((-i,i+1,i+1) for i in range(1,n))+((1,1,1),)
    bags=tuple((i,i+1) for i in range(1,n))
    edges=tuple((i,i+1) for i in range(n-2))
    r=solve(n,cs,bags,edges)
    assert r["sat"] and all(r["witness"]) and verify(n,cs,bags,edges,r)
    counts["chain_variables"]=n
    counts["chain_candidates"]=r["table_candidates"]
    return counts
