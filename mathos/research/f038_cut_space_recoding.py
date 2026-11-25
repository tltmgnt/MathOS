"""Global NAE difference recoding, exact cycle-syndrome completion."""
import json
from itertools import combinations,product
from mathos.research.f038_bounded_inference import require
from mathos.research import f038_mixed_polymorphisms as M
from mathos.research.f038_mrax_cycle import run_mrax

PLAN='docs/research/tga-universal/f038-mrax-cut-space-recoding.json'


def nae(*bits):
    return any(b!=bits[0] for b in bits)


def source_ok(atoms,w):
    return all(nae(*(w>>v&1 for v in t)) for t in atoms)


def build(n,atoms):
    edges=[]
    index={}
    pairs=[]
    def edge(a,b):
        e=tuple(sorted((a,b)))
        if e not in index:
            index[e]=len(edges)
            edges.append(e)
        return index[e]
    for a,b,c in atoms:
        require(len({a,b,c})==3 and all(0<=v<n for v in (a,b,c)))
        pairs.append((edge(a,b),edge(a,c)))
    parent=list(range(n))
    forest=[[] for _ in range(n)]
    chords=[]
    def root(u):
        while parent[u]!=u:
            u=parent[u]
        return u
    for i,(u,v) in enumerate(edges):
        a,b=root(u),root(v)
        if a==b:
            chords.append(i)
        else:
            parent[a]=b
            forest[u].append((v,i))
            forest[v].append((u,i))
    cols=[0]*len(edges)
    for j,i in enumerate(chords):
        u,v=edges[i]
        stack=[(u,-1,0)]
        while stack:
            x,p,path=stack.pop()
            if x==v:
                break
            stack.extend((y,x,path|(1<<e)) for y,e in forest[x] if y!=p)
        else:
            raise ValueError('missing forest path')
        cols[i]|=1<<j
        for e in range(len(edges)):
            if path>>e&1:
                cols[e]|=1<<j
    return tuple(edges),tuple(pairs),tuple(cols),len(chords)


def difference(edges,w):
    return sum(((w>>u^w>>v)&1)<<i for i,(u,v) in enumerate(edges))


def syndrome(cols,d):
    z=0
    for i,a in enumerate(cols):
        if d>>i&1:
            z^=a
    return z


def edge_ok(pairs,cols,d):
    return syndrome(cols,d)==0 and all(d&((1<<a)|(1<<b)) for a,b in pairs)


def lift(n,edges,d):
    adj=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        adj[u].append((v,d>>i&1))
        adj[v].append((u,d>>i&1))
    value={}
    for u in range(n):
        if u in value:
            continue
        value[u]=0
        stack=[u]
        while stack:
            v=stack.pop()
            for x,b in adj[v]:
                y=value[v]^b
                if x in value:
                    if value[x]!=y:
                        return None
                else:
                    value[x]=y
                    stack.append(x)
    return sum(b<<i for i,b in value.items())


def high_edges(n,edges,cols):
    deg=[0]*n
    for (u,v),a in zip(edges,cols):
        if a:
            deg[u]+=1
            deg[v]+=1
    return tuple(i for i,((u,v),a) in enumerate(zip(edges,cols))
                 if a and (deg[u]>=3 or deg[v]>=3))


def local_dp(order,cycle,units,cols):
    states={}
    for b in (0,1):
        e=order[0]
        if b or e not in units:
            states[b,b,cols[e] if b else 0]=b<<e
    for e in order[1:]:
        new={}
        for (first,last,z),w in states.items():
            for b in (0,1):
                if (last or b) and (b or e not in units):
                    new.setdefault((first,b,z^(cols[e] if b else 0)),w|(b<<e))
        states=new
    out={}
    for (first,last,z),w in states.items():
        if not cycle or first or last:
            out.setdefault(z,w)
    return out


def branch(pairs,cols,fixed,value):
    free=set(range(len(cols)))-fixed
    adj={e:set() for e in free}
    units=set()
    for a,b in pairs:
        if (a in fixed and value>>a&1) or (b in fixed and value>>b&1):
            continue
        if a in fixed and b in fixed:
            return None
        if a in fixed:
            units.add(b)
        elif b in fixed:
            units.add(a)
        else:
            adj[a].add(b)
            adj[b].add(a)
    require(all(len(v)<=2 for v in adj.values()),'non-path residual')
    all_states={syndrome(cols,value):value}
    while free:
        component={min(free)}
        stack=list(component)
        while stack:
            e=stack.pop()
            for q in adj[e]-component:
                component.add(q)
                stack.append(q)
        end=sorted(e for e in component if len(adj[e])<=1)
        cycle=not end
        order=[min(component) if cycle else end[0]]
        seen=set(order)
        while True:
            nxt=adj[order[-1]]-seen
            if not nxt:
                break
            e=min(nxt)
            order.append(e)
            seen.add(e)
        require(seen==component and (not cycle or order[0] in adj[order[-1]]))
        table=local_dp(order,cycle,units,cols)
        merged={}
        for a,w in all_states.items():
            for b,v in table.items():
                merged.setdefault(a^b,w|v)
        all_states=merged
        if not all_states:
            return None
        free-=component
    return all_states.get(0)


def solve(n,atoms):
    edges,pairs,cols,r=build(n,atoms)
    bridges={i for i,a in enumerate(cols) if not a}
    B=high_edges(n,edges,cols)
    require(len(B)<=6*r)
    fixed=bridges|set(B)
    initial=sum(1<<i for i in bridges)
    trials=0
    for z in range(1<<len(B)):
        trials+=1
        value=initial|sum(1<<e for i,e in enumerate(B) if z>>i&1)
        d=branch(pairs,cols,fixed,value)
        if d is not None:
            w=lift(n,edges,d)
            require(w is not None and edge_ok(pairs,cols,d)
                    and difference(edges,w)==d and source_ok(atoms,w))
            return 'SAT',w,(r,len(B),trials,d)
    return 'UNSAT',None,(r,len(B),trials,None)


def verify(n,atoms,result):
    try:
        return result==solve(n,atoms)
    except (ValueError,TypeError,IndexError):
        return False


def fixture(n,all_pivots):
    triples=tuple(combinations(range(n),3))
    stats=[0]*12
    for choices in product(range(4 if all_pivots else 2),repeat=len(triples)):
        atoms=[]
        for t,k in zip(triples,choices):
            if k:
                p=k-1 if all_pivots else 0
                atoms.append((t[p],)+tuple(v for i,v in enumerate(t) if i!=p))
        atoms=tuple(atoms)
        edges,pairs,cols,r=build(n,atoms)
        images=set()
        models=[]
        for w in range(1<<n):
            d=difference(edges,w)
            images.add(d)
            ok=source_ok(atoms,w)
            require(ok==edge_ok(pairs,cols,d))
            if ok:
                models.append(w)
            stats[4]+=1
        em=0
        for d in range(1<<len(edges)):
            require((syndrome(cols,d)==0)==(d in images))
            stats[5]+=1
            if edge_ok(pairs,cols,d):
                w=lift(n,edges,d)
                require(w is not None and source_ok(atoms,w) and difference(edges,w)==d)
                em+=1
                stats[7]+=1
        require(len(models)==em*(1<<n)//len(images))
        result=solve(n,atoms)
        require((result[0]=='SAT')==bool(models) and verify(n,atoms,result))
        if models:
            require(result[1] in models)
        stats[0]+=1
        stats[1]+=bool(models)
        stats[2]+=not models
        stats[3]+=len(models)
        stats[6]+=em
        stats[8]+=all(not cols[a] or not cols[b] for a,b in pairs)
        stats[9]+=r
        stats[10]=max(stats[10],r)
        stats[11]+=len(high_edges(n,edges,cols))
    return stats


def controls():
    split=ineq=types=good=families=corrupt=0
    for a,b,c,d in product((0,1),repeat=4):
        require(nae(a,b,c,d)==any(nae(a,b,u) and nae(1-u,c,d) for u in (0,1)))
        split+=1
    for a,b in product((0,1),repeat=2):
        ok=False
        for i,j,k in product((0,1),repeat=3):
            ok|=nae(a,b,i) and nae(a,b,j) and nae(a,b,k) and nae(i,j,k)
            ineq+=1
        require(ok==(a!=b))
    for T in product(range(4),repeat=3):
        valid=M.closed((0,3,5,6),T)
        require(valid==(T==(3,3,3)))
        good+=valid
        types+=1
    for n,atoms,r in (
        (96,tuple((3*i,3*i+1,3*i+2) for i in range(32)),0),
        (33,tuple((i,(i-1)%33,(i+1)%33) for i in range(33)),1),
        (64,tuple((i,(i-1)%64,(i+1)%64) for i in range(64)),1)):
        result=solve(n,atoms)
        require(result[0]=='SAT' and result[2][:3]==(r,0,1) and verify(n,atoms,result))
        families+=1
    require(not verify(n,atoms,('SAT',0,result[2])))
    corrupt+=1
    return [split,ineq,types,good,families,corrupt]


def audit():
    result={'four':fixture(4,True),'five':fixture(5,False),'controls':controls()}
    print('F038_MRAX_CUT_SPACE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
