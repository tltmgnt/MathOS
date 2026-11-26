"""Finite separator-message reference, not an original tape implementation."""
import json
from itertools import combinations, product
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_distributed_hyperclique import fixed, witness

R=9
H=tuple(h for k in (1,2,3) for h in combinations(range(R),k))
A=tuple(range(4))
B=tuple(range(4,9))
FIVE={tuple(sorted(4+(i+j)%5 for j in range(3))) for i in range(5)}
PATH=((0,1,2,3,4),(2,3,4,5,6),(4,5,6,7,8))
BRIDGE=(A,(3,4),B)
PARENTS=(-1,0,1)


def require(ok,msg):
    if not ok:
        raise AssertionError(msg)


def clause(h,z,m):
    return tuple(-(g*m+a+1) for g,a in zip(h,z))


def forbidden(mode,h,z,m):
    if mode==0:
        return False
    if mode==1:
        return h==(0,)
    if mode==2:
        return len(h)==1 and z[0]!=h[0]%m
    if mode==3:
        return len(h)==2 and h[1]==h[0]+1 and z[0]!=z[1]
    if mode==4:
        return len(h)==3 and (sum((i+2)*a for i,a in enumerate(z))+sum(h))%5==0
    if mode==5:
        return len(h)==3 and any(a!=(g+1)%m for g,a in zip(h,z))
    if h==(3,4):
        return z==(1,1)
    if len(h)==3 and (set(h)<=set(A) or h in FIVE):
        nz=[a for a in z if a]
        return len(nz)%2==1 or len(nz)==2 and nz[0]==nz[1]
    return False


def projection(groups,z,h):
    return tuple(z[groups.index(g)] for g in h)


def reference(m,mode,C,loc):
    bags=BRIDGE if mode==6 else PATH
    sep=[()]+[tuple(g for g in bags[i] if g in bags[PARENTS[i]])
              for i in range(1,len(bags))]
    require(set().union(*map(set,bags))==set(range(R)),'bag coverage')
    require(all(len(b)<=5 for b in bags) and all(len(s)<=3 for s in sep),'bounds')
    for g in range(R):
        occurrences=[i for i,b in enumerate(bags) if g in b]
        require(occurrences==list(range(min(occurrences),max(occurrences)+1)),
                'path running intersection')
    selected={}
    owned=[{} for _ in bags]
    for h in H:
        i=next((i for i,b in enumerate(bags) if set(h)<=set(b)),None)
        if i is None:
            continue
        values={z for z in product(range(m),repeat=len(h)) if forbidden(mode,h,z,m)}
        if values:
            selected[h]=values
            owned[i][h]=values
    n=19*m-7
    pins=tuple((g+mode)%2 for g in range(m))
    F=tuple(fixed(R,m,n,pins))
    clauses=tuple(clause(h,z,m) for h,vals in selected.items() for z in sorted(vals))
    require(len(set(F+clauses))==len(F)+len(clauses),'fixed/cross separation')
    p=sum(1<<loc[c] for c in F+clauses)
    raw=encoded(n,p,C)
    require(raw[:n+1]=='1'*n+'0' and len(raw)==n+1+len(C),'normalized header')
    recovered={}
    for h in H:
        vals={z for z in product(range(m),repeat=len(h))
              if raw[n+1+loc[clause(h,z,m)]]=='1'}
        if vals:
            recovered[h]=vals
    require(recovered==selected,'exact selector bits')

    def passes(groups,z,relations):
        return not any(projection(groups,z,h) in vals for h,vals in relations.items())

    messages=[{} for _ in bags]
    local=passing=keys=exact=0
    for i in reversed(range(len(bags))):
        b=bags[i]
        children=[j for j,q in enumerate(PARENTS) if q==i]
        for z in product(range(m),repeat=len(b)):
            if not passes(b,z,owned[i]):
                continue
            local+=1
            if any(projection(b,z,sep[j]) not in messages[j] for j in children):
                continue
            passing+=1
            messages[i].setdefault(projection(b,z,sep[i]),z)
        require(len(messages[i])<=m**len(sep[i]),'message capacity')
        keys+=len(messages[i])

    # Independently enumerate each entire subtree and compare its separator projection.
    for i in range(len(bags)):
        desc=[i]
        for j in range(i+1,len(bags)):
            if PARENTS[j] in desc:
                desc.append(j)
        groups=tuple(sorted(set().union(*(set(bags[j]) for j in desc))))
        relations={h:v for j in desc for h,v in owned[j].items()}
        ref={projection(groups,z,sep[i]) for z in product(range(m),repeat=len(groups))
             if passes(groups,z,relations)}
        require(ref==set(messages[i]),'exact subtree separator message')
        exact+=len(ref)

    models=0
    for z in product(range(m),repeat=R):
        models+=passes(tuple(range(R)),z,selected)
    require(bool(models)==bool(messages[0]),'root SAT equivalence')
    if models:
        z=[-1]*R
        for i,b in enumerate(bags):
            record=messages[i][tuple(z[g] for g in sep[i])]
            for g,a in zip(b,record):
                require(z[g] in (-1,a),'consistent witness')
                z[g]=a
        require(passes(tuple(range(R)),tuple(z),selected),'reconstructed tuple')
        require(valid(C,n,p,witness(R,m,n,pins,tuple(z))),'actual original verifier')
    anti=0
    minimum=m
    if mode==6:
        require(models==1 and z==[0]*R,'unique control')
        tables={}
        for h in H:
            rel={k:v for k,v in selected.items() if set(k)<=set(h)}
            tables[h]={t for t in product(range(m),repeat=len(h)) if passes(h,t,rel)}
        for g in range(R):
            for h,T in tables.items():
                if g not in h:
                    continue
                i=h.index(g)
                require({t[i] for t in T}==set(range(m)),'full local support')
                counts={}
                for t in T:
                    k=t[:i]+t[i+1:]
                    counts[k]=counts.get(k,0)+1
                minimum=min(minimum,max(counts.values()))
            for a,b in product(range(m),repeat=2):
                if a==b:
                    continue
                require(any(t[h.index(g)]==b and
                            t[:h.index(g)]+(a,)+t[h.index(g)+1:] not in T
                            for h,T in tables.items() if g in h for t in T),
                        'contextual incomparability')
                anti+=1
        require(minimum>=m-2,'fanout lower bound')
    return [m,mode,len(clauses),models,local,passing,keys,exact,anti,minimum]


EXPECTED=[[2,0,0,512,96,96,17,17,0,2],[2,1,2,0,64,64,16,16,0,2],
[2,2,9,1,17,17,17,17,0,2],[2,3,16,2,18,18,17,17,0,2],
[2,4,45,0,7,2,2,2,0,2],[2,5,196,1,3,3,3,3,0,2],
[3,0,0,19683,729,729,55,55,0,3],[3,1,3,0,486,486,54,54,0,3],
[3,2,18,1,55,55,55,55,0,3],[3,3,48,3,57,57,55,55,0,3],
[3,4,151,16,86,54,33,33,0,3],[3,5,728,1,3,3,3,3,0,3],
[3,6,181,1,10,5,5,5,54,1],[4,6,406,1,17,6,6,6,108,2]]


def audit():
    rows=[]
    for m,modes in ((2,range(6)),(3,range(7)),(4,(6,))):
        C=pool(19*m-7)
        loc={c:i for i,c in enumerate(C)}
        rows.extend(reference(m,mode,C,loc) for mode in modes)
    require(rows==EXPECTED,'independent JS reference')
    result={'fixtures':len(rows),'sums':[sum(r[i] for r in rows) for i in range(2,9)]}
    require(result=={'fixtures':14,'sums':[1803,20222,1648,1595,338,338,162]},
            'aggregate')
    print('F038_UNRESTRICTED_SEPARATOR_MESSAGES_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
