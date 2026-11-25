"""Exact separator-tree optimization, cycle discovery, and all-tree obstruction audits."""
from itertools import combinations
from mathos.research.f038_affine_separator import span, intersection, cycle
from mathos.research.f038_hybrid_affine import extract, verify_partition
from mathos.research.f038_affine_direct_sum import coordinate_forms


def cuts(scopes):
    m=len(scopes)
    N=1<<m
    spaces=[()]
    for s in range(1,N):
        bit=s&-s
        spaces.append(span(spaces[s^bit]+tuple(scopes[bit.bit_length()-1])))
    ranks=tuple(map(len,spaces))
    return tuple(ranks[s]+ranks[N-1-s]-ranks[-1] for s in range(N))


def splits(s):
    bit=s&-s
    a=(s-1)&s
    while a:
        if a&bit:
            yield a,s^a
        a=(a-1)&s


def optimize(scopes):
    c=cuts(scopes)
    D=[0]*len(c)
    choice={}
    trials=0
    for s in range(1,len(c)):
        if not s&(s-1):
            D[s]=c[s]
            continue
        best=None
        for a,b in splits(s):
            trials+=1
            val=max(D[a],D[b])
            if best is None or val<best:
                best=val
                choice[s]=(a,b)
        D[s]=max(c[s],best)
    def build(s):
        if s not in choice:
            return s
        a,b=choice[s]
        return build(a),build(b)
    return D[-1],build(len(c)-1),tuple(D),trials


def balanced(leaves):
    if len(leaves)<=1:
        return leaves[0] if leaves else 0
    mid=len(leaves)//2
    return balanced(leaves[:mid]),balanced(leaves[mid:])


def tree_width(scopes,tree):
    full=(1<<len(scopes))-1
    def walk(t):
        if type(t) is int:
            if not (t==0 and full==0 or 0<t<=full and not t&(t-1)):
                raise ValueError('invalid leaf')
            s=t
            child=0
        else:
            if len(t)!=2:
                raise ValueError('invalid arity')
            a,x=walk(t[0])
            b,y=walk(t[1])
            if not a or not b or a&b:
                raise ValueError('invalid partition')
            s=a|b
            child=max(x,y)
        w=span(v for i,sc in enumerate(scopes) if s&(1<<i) for v in sc)
        o=span(v for i,sc in enumerate(scopes) if not s&(1<<i) for v in sc)
        cut=len(w)+len(o)-len(span(w+o))
        return s,max(cut,child)
    s,w=walk(tree)
    if s!=full:
        raise ValueError('missing leaves')
    return w


def verify_optimum(scopes,tree,D):
    c=cuts(scopes)
    if len(D)!=len(c) or D[0]!=0:
        return False
    for s in range(1,len(c)):
        expected=c[s]
        if s&(s-1):
            expected=max(expected,min(max(D[a],D[b]) for a,b in splits(s)))
        if D[s]!=expected:
            return False
    try:
        return tree_width(scopes,tree)==D[-1]
    except (ValueError,TypeError):
        return False


def all_trees(s):
    if not s&(s-1):
        yield s
        return
    for a,b in splits(s):
        for x in all_trees(a):
            for y in all_trees(b):
                yield x,y


def width_by_cuts(t,c):
    if type(t) is int:
        return t,c[t]
    a,x=width_by_cuts(t[0],c)
    b,y=width_by_cuts(t[1],c)
    assert not a&b
    return a|b,max(x,y,c[a|b])


def discover_cycle(scopes,n):
    groups={}
    for i,sc in enumerate(scopes):
        key=span(sc)
        groups.setdefault(key,[]).append(1<<i)
    keys=sorted(groups)
    if len(keys)<3 or any(len(k)!=2 or len(groups[k])!=2 for k in keys):
        return None
    neighbors={k:tuple(h for h in keys if h!=k and intersection(k,h,n))
               for k in keys}
    if any(len(v)!=2 for v in neighbors.values()):
        return None
    order=[keys[0]]
    prev=None
    while True:
        nxt=next(k for k in neighbors[order[-1]] if k!=prev)
        if nxt==order[0]:
            break
        if nxt in order:
            return None
        prev=order[-1]
        order.append(nxt)
    if len(order)!=len(keys):
        return None
    tree=balanced([tuple(groups[k]) for k in order])
    return tree if tree_width(scopes,tree)==2 else None


def audit():
    fixture=((1,),(2,),(3,),(4,),(5,6),(1,2),(2,4),(1,4))
    cases=states=trials=trees=rank_checks=worse=corrupt=0
    hist=[0]*4
    for s in range(1<<len(fixture)):
        sc=tuple(v for i,v in enumerate(fixture) if s&(1<<i))
        if len(sc)>5:
            continue
        w,t,D,k=optimize(sc)
        c=cuts(sc)
        assert verify_optimum(sc,t,D)
        bad=D[:-1]+(D[-1]+1,)
        assert not verify_optimum(sc,t,bad)
        corrupt+=1
        optimum=None
        for tree in all_trees(len(c)-1):
            mask,width=width_by_cuts(tree,c)
            assert mask==len(c)-1
            optimum=width if optimum is None else min(optimum,width)
            trees+=1
        assert optimum==w
        for mask in range(len(c)):
            a=span(v for i,x in enumerate(sc) if mask&(1<<i) for v in x)
            b=span(v for i,x in enumerate(sc) if not mask&(1<<i) for v in x)
            assert len(intersection(a,b,3))==c[mask]
            rank_checks+=1
        bw=tree_width(sc,balanced([1<<i for i in range(len(sc))]))
        worse+=bw>w
        hist[w]+=1
        cases+=1
        states+=len(c)
        trials+=k
    assert (cases,states,trials,trees,rank_checks,worse,hist,corrupt)==(
        219,3489,7154,7135,3489,51,[26,42,146,5],219)
    print('F038_SEPARATOR_OPTIMUM_OK cases=219 states=3489 split_trials=7154 '
          'trees=7135 rank_checks=3489 balanced_worse=51 '
          'width_hist=26,42,146,5 corrupt_rejected=219')


def graph_audit():
    widths=[]
    bounds=[]
    states=[]
    trials=[]
    for n in range(3,6):
        f=tuple((i+1,j+1) for i,j in combinations(range(n),2))
        rows,rest=extract(f)
        assert not rows and verify_partition(f,rows,rest)
        sc=tuple(tuple(1<<(v-1) for v in c) for c in f)
        w,t,D,k=optimize(sc)
        assert verify_optimum(sc,t,D)
        m=len(f)
        bound=0
        while bound*(bound-1)//2<(m+2)//3:
            bound+=1
        assert w>=bound
        # Independent exhaustive balanced-cut check.
        for s,c in enumerate(cuts(sc)):
            if m<=3*s.bit_count()<=2*m:
                assert c>=bound
        widths.append(w)
        bounds.append(bound)
        states.append(len(D))
        trials.append(k)
    assert (widths,bounds,states,trials)==(
        [2,3,4],[2,3,4],[8,64,1024],[6,301,28501])
    print('F038_SEPARATOR_ALL_TREE_BARRIER_OK sizes=3,4,5 widths=2,3,4 '
          'bounds=2,3,4 states=8,64,1024 split_trials=6,301,28501')


def cycle_audit():
    sizes=(3,4,7,8,15,16,31,32)
    for m in sizes:
        f,n=cycle(m)
        # Put positive residual triples before negative residual triples.
        f=tuple(c for c in f if len(c)==2)+tuple(
            c for c in f if len(c)==3 and c[0]>0)+tuple(
            c for c in f if len(c)==3 and c[0]<0)
        rows,rest=extract(f)
        assert verify_partition(f,rows,rest) and len(rest)==2*m
        forms,bad=coordinate_forms(rows,n)
        assert forms is not None and bad is None
        sc=tuple(span(forms[abs(l)-1][0] for l in f[i]) for i in rest)
        assert len(span(v for s in sc for v in s))==m
        bad_tree=balanced([1<<i for i in range(2*m)])
        assert tree_width(sc,bad_tree)==m
        tree=discover_cycle(sc,n)
        assert tree is not None and tree_width(sc,tree)==2
        # Every singleton cut is rank two, proving optimality.
        for i,s in enumerate(sc):
            outside=span(v for j,t in enumerate(sc) if j!=i for v in t)
            assert len(intersection(s,outside,n))==2
    print('F038_SEPARATOR_CYCLE_DISCOVERY_OK sizes=3,4,7,8,15,16,31,32 '
          'bad_widths=3,4,7,8,15,16,31,32 optimal_width_each=2 '
          'max_rank=32')


if __name__=='__main__':
    audit()
    graph_audit()
    cycle_audit()
