"""Satisfiable guarded 3-CNFs with locally surviving wrong branches."""
from itertools import combinations, permutations
from mathos.research.f037_log_backdoor import restrict, satisfies


def guarded(k,good):
    # Selector is 1. The guard literal is true at the unique good bit.
    # Every other variable has an owner pigeon and a value function
    # on that pigeon's chosen hole.
    g=1 if good else -1
    tags={}
    f=[]
    next_id=2

    def new(p,values):
        nonlocal next_id
        v=next_id
        next_id+=1
        tags[v]=(p,tuple(values))
        return v

    def add(p,c):
        if len(c)<=2:
            f.append((g,*c))
        else:
            a,b,c=c
            # (g OR a OR b OR c) via (g OR a OR u), (-u OR b OR c).
            # In the wrong branch u = not a, determined by one pigeon.
            u=new(p,[not (tags[abs(a)][1][j]==(a>0)) for j in range(k)])
            f.extend(((g,a,u),(-u,b,c)))

    placements=[]
    for p in range(k+1):
        x=[new(p,[j==h for j in range(k)]) for h in range(k)]
        s=[new(p,[j<=h for j in range(k)]) for h in range(k)]
        placements.append(x)
        add(p,(-x[0],s[0]))
        add(p,(x[0],-s[0]))
        for h in range(1,k):
            add(p,(-s[h-1],s[h]))
            add(p,(-x[h],s[h]))
            add(p,(s[h-1],x[h],-s[h]))
        add(p,(s[-1],))
    for p,q in combinations(range(k+1),2):
        for h in range(k):
            f.append((g,-placements[p][h],-placements[q][h]))
    # Every nonselector bit false satisfies the inactive guarded
    # clauses, including the second clause of each split.
    model={1:good}
    model.update({v:False for v in tags})
    assert satisfies(f,model)
    return tuple(f),tags,model


def local_family(k,tags,scope):
    pigeons=sorted({tags[v][0] for v in scope})
    return {tuple(tags[v][1][d[tags[v][0]]] for v in scope)
            for holes in permutations(range(k),len(pigeons))
            for d in [dict(zip(pigeons,holes))]}


def audit(k,good):
    f,tags,model=guarded(k,good)
    wrong=restrict(f,{1:not good})
    clauses=[(c,{abs(l) for l in c}) for c in wrong]
    vs=sorted(tags)
    H={}
    count=local=extensions=0
    for size in range(k+1):
        for s in combinations(vs,size):
            vals=local_family(k,tags,s)
            assert vals
            H[s]=vals
            count+=len(vals)
            local_rows=[c for c,scope in clauses if scope<=set(s)]
            for a in vals:
                assert satisfies(local_rows,dict(zip(s,a)))
                local+=len(local_rows)
    for s,vals in H.items():
        if len(s)==k:
            continue
        for v in vs:
            if v in s:
                continue
            t=tuple(sorted((*s,v)))
            indices=[t.index(w) for w in s]
            projected={tuple(a[j] for j in indices) for a in H[t]}
            assert projected==vals
            extensions+=len(vals)
    return len(vs)+1,len(f),len(H),count,local,extensions


def run():
    for k in (2,3):
        a=audit(k,False)
        b=audit(k,True)
        assert a==b
        print(f"k={k} variables={a[0]} clauses={a[1]} scopes={a[2]} states={a[3]} local={a[4]} extensions={a[5]}")
    print("F037_GUARDED_CHOICE_OK capacities=2,3 polarities=2")


if __name__=="__main__":
    run()
