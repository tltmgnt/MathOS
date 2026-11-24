"""F027: compress signed 3-CNF and choose a syntactic affine backdoor.

Cover all pairs of distinct variables in every non-tautological clause.
After fixing the cover, each residual clause is constant or a unit affine
equation. This suffices for exact solving, not a universal small backdoor.
"""
from itertools import combinations, product
from mathos.research.tga_proctor_unrestricted_scope import compile_cnf, evaluate, backdoor


def compress(n, clauses):
    clauses=tuple(tuple(c) for c in clauses)
    compile_cnf(n,clauses)  # existing validation; explicit n convention
    seen=set()
    result=[]
    tautologies=duplicates=repeated=0
    for i,c in enumerate(clauses):
        literals=set(c)
        repeated+=len(c)-len(literals)
        if any(-l in literals for l in literals):
            tautologies+=1
            continue
        key=tuple(sorted(literals))
        if key in seen:
            duplicates+=1
            continue
        seen.add(key)
        result.append((i,key))
    return clauses,tuple(result),dict(tautologies=tautologies,
        duplicate_clauses=duplicates,repeated_literals=repeated)


def edges_for(rows):
    return tuple(sorted({e for _,c in rows
        for e in combinations(sorted({abs(l) for l in c}),2)}))


def valid_cover(edges, cover):
    s=set(cover)
    return all(a in s or b in s for a,b in edges)


def cover_plan(edges):
    """Maximal matching endpoints give a certified 2-approximation.
    Try a degree-greedy alternative and remove redundant vertices.
    """
    used=set()
    matching=[]
    for a,b in edges:
        if a not in used and b not in used:
            matching.append((a,b))
            used.update((a,b))
    chosen=set()
    remaining=list(edges)
    while remaining:
        degree={}
        for a,b in remaining:
            degree[a]=degree.get(a,0)+1
            degree[b]=degree.get(b,0)+1
        v=min(degree,key=lambda x:(-degree[x],x))
        chosen.add(v)
        remaining=[e for e in remaining if v not in e]
    def trim(s):
        s=set(s)
        for v in sorted(s,reverse=True):
            if valid_cover(edges,s-{v}):
                s.remove(v)
        return tuple(sorted(s))
    cover=min((trim(used),trim(chosen)),key=lambda c:(len(c),c))
    assert valid_cover(edges,cover) and len(cover)<=2*len(matching)
    return cover,tuple(matching)


def plan(n,clauses):
    cs,rows,stats=compress(n,clauses)
    edges=edges_for(rows)
    cover,matching=cover_plan(edges)
    return cs,rows,cover,matching,dict(**stats,compressed_clauses=len(rows),
        graph_edges=len(edges),cover_size=len(cover),matching_lower=len(matching),
        prior_gate_backdoor=len(backdoor(compile_cnf(n,cs))))


def residual(c,fixed):
    """None means satisfied; empty tuple means false; otherwise signed units."""
    if any(abs(l) in fixed and fixed[abs(l)]==(l>0) for l in c):
        return None
    return tuple(sorted({l for l in c if abs(l) not in fixed}))


def solve(n, clauses):
    cs,rows,cover,matching,stats=plan(n,clauses)
    failures=[]
    scans=0
    for bits in product((False,True),repeat=len(cover)):
        fixed=dict(zip(cover,bits))
        units={}
        for i,c in rows:
            scans+=1
            r=residual(c,fixed)
            if r is None:
                continue
            if not r:
                failures.append(("false",i))
                break
            if len(r)!=1:
                raise AssertionError("uncovered nonlinear residual")
            l=r[0]
            v,b=abs(l),l>0
            if v in units and units[v][0]!=b:
                failures.append(("units",units[v][1],i))
                break
            units[v]=(b,i)
        else:
            x=[False]*n
            for v,b in fixed.items():
                x[v-1]=b
            for v,(b,_) in units.items():
                x[v-1]=b
            if not evaluate(cs,x):
                raise AssertionError("invalid original witness")
            return dict(sat=True,witness=tuple(x),failures=(),cover=cover,
                matching=matching,branches=len(failures)+1,clause_scans=scans,**stats)
    return dict(sat=False,witness=(),failures=tuple(failures),cover=cover,
        matching=matching,branches=len(failures),clause_scans=scans,**stats)


def verify(n,clauses,result):
    """Original-clause proof checker, independent of compressed row search.
    A false residual or opposite pair of unit residuals refutes its branch.
    """
    cs=tuple(tuple(c) for c in clauses)
    compile_cnf(n,cs)
    try:
        if result["sat"] is True:
            x=result["witness"]
            return len(x)==n and all(b in (0,1) for b in x) and evaluate(cs,x)
        if result["sat"] is not False:
            return False
        cover=tuple(result["cover"])
        if (any(type(v) is not int or not 1<=v<=n for v in cover)
            or tuple(sorted(set(cover)))!=cover):
            return False
        failures=result["failures"]
        if len(failures)!=2**len(cover):
            return False
        for bits,proof in zip(product((False,True),repeat=len(cover)),failures):
            fixed=dict(zip(cover,bits))
            tag,*ix=proof
            if any(type(i) is not int or not 0<=i<len(cs) for i in ix):
                return False
            # Compute directly from original literals. Set removes duplicates.
            rs=[]
            for i in ix:
                c=cs[i]
                if any(abs(l) in fixed and fixed[abs(l)]==(l>0) for l in c):
                    rs.append(None)
                else:
                    rs.append({l for l in c if abs(l) not in fixed})
            if tag=="false" and len(rs)==1 and rs[0]==set():
                continue
            if (tag=="units" and len(rs)==2 and all(r is not None and len(r)==1 for r in rs)
                and rs[0]=={-l for l in rs[1]}):
                continue
            return False
        return True
    except (TypeError,KeyError,ValueError,IndexError):
        return False


def controls():
    base=tuple(product((-2,-1,1,2),repeat=3))
    fixtures=[(0,()),(2,())]+[(2,(c,)) for c in base]
    small=((1,1,1),(-1,-1,-1),(1,-2,1),(-1,2,-1),(1,-1,2),(2,2,2))
    fixtures += [(2,(a,b)) for a,b in product(small,repeat=2)]
    fixtures += [(3,tuple(tuple(s*(i+1) for i,s in enumerate(signs))
                          for signs in product((-1,1),repeat=3)))]
    counts=dict(cases=0,sat=0,unsat=0,branches=0,clause_scans=0,
                original_gate_backdoor_sum=0,cover_size_sum=0)
    for n,cs in fixtures:
        r=solve(n,cs)
        brute=any(evaluate(cs,x) for x in product((False,True),repeat=n))
        assert r["sat"]==brute and verify(n,cs,r)
        _,rows,cover,matching,_=plan(n,cs)
        edges=edges_for(rows)
        optimum=min(len(c) for k in range(n+1)
                    for c in combinations(range(1,n+1),k) if valid_cover(edges,c))
        assert len(matching)<=optimum<=len(cover)<=2*optimum
        if not brute:
            assert not verify(n,cs,{**r,"failures":r["failures"][:-1]})
            assert not verify(n,cs,{**r,"failures":(("false",-1),)+r["failures"][1:]})
        counts["cases"]+=1
        counts["sat" if brute else "unsat"]+=1
        counts["branches"]+=r["branches"]
        counts["clause_scans"]+=r["clause_scans"]
        counts["original_gate_backdoor_sum"]+=r["prior_gate_backdoor"]
        counts["cover_size_sum"]+=r["cover_size"]
    n=64
    cs=tuple((1,i,i) for i in range(2,n+1))
    r=solve(n,cs+cs+((1,-1,2),))
    assert r["sat"] and verify(n,cs+cs+((1,-1,2),),r)
    assert r["cover_size"]==1 and r["duplicate_clauses"]==63
    counts["star"]={k:r[k] for k in ("cover_size","prior_gate_backdoor",
        "branches","clause_scans","duplicate_clauses","tautologies","repeated_literals")}
    # Dense positive triple family: trivial SAT, but any syntactic cover
    # of the complete primal graph has at least n-1 vertices.
    dense=tuple(combinations(range(1,13),3))
    _,rows,c,matching,_=plan(12,dense)
    assert len(edges_for(rows))==66 and len(c)==11
    counts["dense_cover"]=len(c)
    return counts
