"""Strict three-color CNF recognition and bounded SAT-only tabu repair."""
from itertools import combinations
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_hall_certificate import verify as verify_model


def eligible(f):
    # Cheap conservative gate. All accepted formulas still undergo
    # exact structural recognition and original-model replay.
    return (sum(len(c)==3 and all(x>0 for x in c) for c in f)>=20
            and all((len(c)==3 and all(x>0 for x in c))
                    or (len(c)==2 and all(x<0 for x in c)) for c in f))


def recognize(n,f,b):
    groups=[]
    owner={}
    neg={}
    for c in f:
        b.tick(1+len(c))
        if len(c)==3 and all(x>0 for x in c) and len(set(c))==3:
            a=tuple(sorted(c))
            i=len(groups)
            if any(v in owner for v in a):
                return None
            groups.append(a)
            owner.update((v,(i,j)) for j,v in enumerate(a))
        elif len(c)==2 and all(x<0 for x in c) and c[0]!=c[1]:
            neg[tuple(sorted(map(abs,c)))]=None
        else:
            return None
    if not groups:
        return None
    edges={}
    for a,c in neg:
        b.tick()
        if a not in owner or c not in owner:
            return None
        (i,j),(k,l)=owner[a],owner[c]
        if i==k:
            continue
        if j!=l:
            return None
        key=tuple(sorted((i,k)))
        edges[key]=edges.get(key,0)|(1<<j)
    for a in groups:
        for pair in combinations(a,2):
            b.tick()
            if pair not in neg:
                return None
    adj=[[] for _ in groups]
    for (i,j),mask in edges.items():
        b.tick()
        if mask!=7:
            return None
        adj[i].append(j)
        adj[j].append(i)
    b.cells(8*len(groups)+2*len(edges))
    return groups,adj


def propose(n,clauses,b):
    f=validate(n,clauses)
    structure=recognize(n,f,b)
    if structure is None:
        return None
    groups,adj=structure
    g=len(groups)
    seed=192405
    def rand(k):
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed%k
    color=[-1]*g
    counts=[[0,0,0] for _ in groups]
    bad={}
    def mark(i):
        if color[i]>=0 and counts[i][color[i]]:
            bad[i]=None
        else:
            bad.pop(i,None)
    def assign(i,c):
        prev=color[i]
        color[i]=c
        b.tick()
        for j in adj[i]:
            b.tick()
            if prev>=0:
                counts[j][prev]-=1
            counts[j][c]+=1
            mark(j)
        mark(i)
    # DSATUR-style initial construction, allowing a conflicting color
    # when the partial coloring cannot be extended greedily.
    for _ in groups:
        best,score=-1,-1
        for i in range(g):
            b.tick()
            if color[i]<0:
                s=sum(x>0 for x in counts[i])*(g+1)+len(adj[i])
                if s>score:
                    best,score=i,s
        a=counts[best]
        m=min(a)
        choices=[c for c in range(3) if a[c]==m]
        assign(best,choices[rand(len(choices))])
    iterations=0
    tabu=[[0,0,0] for _ in groups]
    while bad:
        iterations+=1
        move=None
        score=float("inf")
        ties=0
        for i in bad:
            b.tick()
            for c in range(3):
                if c==color[i]:
                    continue
                b.tick()
                delta=counts[i][c]-counts[i][color[i]]
                if tabu[i][c]>iterations and delta>=0:
                    continue
                if delta<score:
                    score,move,ties=delta,(i,c),1
                elif delta==score:
                    ties+=1
                    if rand(ties)==0:
                        move=(i,c)
        if move is None:
            b.tick(len(bad))
            i=list(bad)[rand(len(bad))]
            move=(i,(color[i]+1+rand(2))%3)
        i,c=move
        tabu[i][color[i]]=iterations+5+rand(8)+len(bad)//2
        assign(i,c)
    model=[False]*n
    for i,a in enumerate(groups):
        b.tick()
        model[a[color[i]]-1]=True
    return {"decision":"sat","certificate":model,"iterations":iterations}


def attempt(n,f,total,seconds):
    b=Budget(seconds=seconds,max_steps=total,max_cells=200_000)
    p,status=None,"unrecognized"
    try:
        p=propose(n,f,b)
        if p is not None:
            verify_model(n,f,p,b)
            status="replayed"
    except Exhausted:
        p,status=None,"resource_exhausted"
    return {"decision":"sat" if p else "unknown","proof":p,
            "status":status,"work_steps":b.steps}


def replay(n,f,r,total):
    w,p=r["work_steps"],r["proof"]
    if type(w) is not int or not 0<=w<=total:
        raise ValueError("invalid work")
    if r["status"]=="replayed":
        if r["decision"]!="sat" or p is None or p["decision"]!="sat":
            raise ValueError("missing SAT proof")
        if type(p["iterations"]) is not int or p["iterations"]<0:
            raise ValueError("invalid observed iterations")
        verify_model(n,f,p,Budget(seconds=15,max_steps=4_000_000,max_cells=200_000))
    elif r["status"] not in ("unrecognized","resource_exhausted") or p is not None or r["decision"]!="unknown":
        raise ValueError("invalid unknown")
    return True
