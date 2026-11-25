"""A direct monotone-circuit obstruction for existential branch choice.

The graph reduction is polynomial. Exhaustive finite DPLL controls
are validation oracles only; no unrestricted SAT algorithm is claimed.
"""
from itertools import combinations, product
from mathos.research.f037_log_backdoor import restrict, satisfies
from mathos.research.f037_probe_selector_barrier import propagate


def template(n,k):
    assert 2<=k<=n
    top=1
    fixed=[]
    edge_rows={}
    nonedge_rows={}
    pairs=tuple(combinations(range(n),2))

    def new():
        nonlocal top
        top+=1
        return top

    def add(g,c):
        # Guard an arbitrary-width clause and split it with
        # private auxiliary variables into width-three clauses.
        row=(g,*c)
        while len(row)>3:
            u=new()
            fixed.append((row[0],row[1],u))
            row=(-u,*row[2:])
        fixed.append(row)

    def onehot(g,vs):
        add(g,tuple(vs))
        for a,b in combinations(vs,2):
            add(g,(-a,-b))

    # False selector activates the coloring branch.
    color=[[new() for _ in range(k-1)] for _ in range(n)]
    for row in color:
        onehot(1,row)
    for u,v in pairs:
        edge_rows[u,v]=tuple((1,-a,-b)
                             for a,b in zip(color[u],color[v]))

    # True selector activates the clique branch.
    pick=[[new() for _ in range(n)] for _ in range(k)]
    for row in pick:
        onehot(-1,row)
    for i,j in combinations(range(k),2):
        for v in range(n):
            add(-1,(-pick[i][v],-pick[j][v]))
    for u,v in pairs:
        nonedge_rows[u,v]=tuple(
            row for i,j in combinations(range(k),2)
            for row in ((-1,-pick[i][u],-pick[j][v]),
                        (-1,-pick[i][v],-pick[j][u])))
    return top,tuple(fixed),pairs,edge_rows,nonedge_rows


def instantiate(t,mask):
    n,f,pairs,a,b=t
    f=list(f)
    oriented=[]
    for i,e in enumerate(pairs):
        on=bool(mask&(1<<i))
        f.extend(a[e] if on else b[e])
        # Increasing inputs mean adding constraints on false
        # branch and removing constraints on true branch.
        oriented.extend([on]*(len(a[e])+len(b[e])))
    assert all(1<=len(c)<=3 for c in f)
    return tuple(f),tuple(oriented)


def graph_properties(n,k,pairs,mask):
    edges={e for i,e in enumerate(pairs) if mask&(1<<i)}
    clique=any(all(e in edges for e in combinations(s,2))
               for s in combinations(range(n),k))
    colorable=any(all(c[u]!=c[v] for u,v in edges)
                  for c in product(range(k-1),repeat=n))
    assert not (clique and colorable)
    return colorable,clique


def sat(f):
    state,g=propagate(f)
    if state!='OPEN':
        return state=='MODEL'
    v=abs(min(g,key=len)[0])
    return sat(restrict(g,{v:False})) or sat(restrict(g,{v:True}))


def audit():
    counts=[0,0,0]
    checks=monotone_edges=0
    max_variables=max_clauses=0
    for n in (3,4,5):
        for k in range(3,min(4,n)+1):
            t=template(n,k)
            N,_,pairs,_,_=t
            max_variables=max(max_variables,N)
            outcomes=[]
            for mask in range(1<<len(pairs)):
                f,flags=instantiate(t,mask)
                a,b=graph_properties(n,k,pairs,mask)
                assert sat(restrict(f,{1:False}))==a
                assert sat(restrict(f,{1:True}))==b
                assert sat(f)==(a or b)
                outcomes.append((a,b,flags))
                counts[0 if a else 1 if b else 2]+=1
                checks+=1
                max_clauses=max(max_clauses,len(f))
            for mask,(a,b,flags) in enumerate(outcomes):
                for i in range(len(pairs)):
                    if mask&(1<<i):
                        continue
                    c,d,newflags=outcomes[mask|(1<<i)]
                    assert all(not x or y for x,y in zip(flags,newflags))
                    assert not c or a
                    assert not b or d
                    monotone_edges+=1
    # Odd cycle: neither a triangle nor bipartite. Safe choice
    # is unconstrained, so this is not exact CLIQUE recognition.
    t=template(5,3)
    edges={(0,1),(1,2),(2,3),(3,4),(0,4)}
    mask=sum(1<<i for i,e in enumerate(t[2]) if e in edges)
    assert graph_properties(5,3,t[2],mask)==(False,False)
    assert not sat(instantiate(t,mask)[0])
    assert checks==2184
    print(f"color_only={counts[0]} clique_only={counts[1]} neither={counts[2]} monotone_edges={monotone_edges} max_variables={max_variables} max_clauses={max_clauses}")
    print("F038_MONOTONE_CHOICE_OK graphs=2184 branch_checks=4368 no_promise=1")


if __name__=="__main__":
    audit()
