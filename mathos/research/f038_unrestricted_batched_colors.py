"""Finite color-batched separator reference; not a physical tape simulator."""
import json
from fractions import Fraction
from itertools import combinations, product

G = tuple(range(9))
H = tuple(h for k in (1, 2, 3) for h in combinations(G, k))


def check(ok, msg):
    if not ok:
        raise AssertionError(msg)


def project(groups, z, h):
    return tuple(z[groups.index(g)] for g in h)


def predicate(groups, records):
    by = {}
    for h, z in records:
        by.setdefault(tuple(groups.index(g) for g in h), set()).add(z)
    return lambda z: not any(tuple(z[i] for i in ix) in vals for ix, vals in by.items())


def factor(m, u, v, original):
    contexts = [None] + [(g, c) for g in G if g not in (u, v) for c in range(m)]
    rows = []
    for ctx in contexts:
        h = tuple(sorted((u, v) if ctx is None else (u, v, ctx[0])))
        M = []
        for a in range(m):
            allowed = set()
            for b in range(m):
                vals = {u: a, v: b}
                if ctx is not None:
                    vals[ctx[0]] = ctx[1]
                if (h, tuple(vals[g] for g in h)) not in original:
                    allowed.add(b)
            M.append(allowed)
        rows.append(M)
    labels = []
    for a in range(m):
        used = {labels[j] for j in range(a) if any(M[a] and M[j] and M[a] != M[j] for M in rows)}
        labels.append(next(k for k in range(m) if k not in used))
    K = max(labels) + 1
    common = {(h, z) for h, z in original if not (u in h and v in h)}
    tagged = set()
    def add(k, g, a, ctx):
        vals = {g: a}
        if ctx is not None:
            vals[ctx[0]] = ctx[1]
        h = tuple(sorted(vals))
        tagged.add((k, h, tuple(vals[i] for i in h)))
    for k in range(K):
        A = [a for a in range(m) if labels[a] == k]
        for a in range(m):
            if a not in A:
                add(k, u, a, None)
        for ctx, M in zip(contexts, rows):
            B = next((M[a] for a in A if M[a]), set())
            for a in A:
                check(not M[a] or M[a] == B, 'rectangle')
                if not M[a]:
                    add(k, u, a, ctx)
            for b in range(m):
                if b not in B:
                    add(k, v, b, ctx)
    check(all(len(h) <= 2 for _, h, _ in tagged), 'tag widths')
    return labels, common, tagged


def tile(groups, S, m, b, d, K, off, common, tagged, stats):
    # One extraction of all colors; tag -1 denotes shared data.
    records = []
    for k, h, z in [( -1, h, z) for h, z in common] + list(tagged):
        delta = project(groups, off, h)
        q = tuple(x-y for x, y in zip(z, delta))
        if all(0 <= x < b for x in q):
            records.append((k, h, q))
    for g, o in zip(groups, off):
        records.extend((-1, (g,), (a,)) for a in range(b) if o+a >= m)
    stats[0] += 1
    stats[1] += len(records)
    slots = [tuple(d*j+x for j,x in zip(J,X))
             for J in product(range((b+d-1)//d), repeat=7)
             for X in product(range(d), repeat=7)]
    index = {key: i for i, key in enumerate(slots)}
    out = [None] * (K * len(slots))
    for k in range(K):
        passes = predicate(groups, [(h,z) for c,h,z in records if c in (-1,k)])
        for z in product(range(b), repeat=8):
            stats[2] += 1
            if passes(z):
                i = k*len(slots)+index[project(groups,z,S)]
                if out[i] is None:
                    out[i] = tuple(a+o for a,o in zip(z,off))
        stats[3] += 1
    return slots, out


def fixture(m, mode, u, v, b, d):
    S = tuple(g for g in G if g not in (u,v))
    bags = (tuple(g for g in G if g != v), tuple(g for g in G if g != u))
    original = set()
    for h in H:
        for z in product(range(m), repeat=len(h)):
            x = dict(zip(h,z))
            pair = u in h and v in h
            if mode == 0: bad = False
            elif mode == 1: bad = len(h)==1 and h==(v,)
            elif mode == 2: bad = len(h)==2 and z==(1,1)
            elif mode == 3: bad = len(h)==3 and (sum(h)+sum((i+2)*a for i,a in enumerate(z)))%5==0
            elif mode == 4: bad = pair and len(h)==3 and x[u]!=x[next(g for g in h if g not in (u,v))]
            elif mode == 5: bad = pair and len(h)==2 and x[u]==x[v]
            elif mode == 6: bad = len(h)==3 and any(z)
            else: bad = (pair and len(h)==2 and x[u]%2==x[v]%2) or (len(h)==3 and not pair and sum(z)%5==4)
            if bad: original.add((h,z))
    labels, common, tagged = factor(m,u,v,original)
    K = max(labels)+1
    if mode in (0,1,4,6): check(K==1, 'single color control')
    if mode in (2,7): check(K==2, 'two color control')
    if mode==5: check(K==m, 'all conflict control')
    shared = [set(),set()]; extras = [set(),set()]
    for h,z in common:
        shared[next(i for i,B in enumerate(bags) if set(h)<=set(B))].add((h,z))
    for k,h,z in tagged:
        extras[next(i for i,B in enumerate(bags) if set(h)<=set(B))].add((k,h,z))
    # Direct global enumeration, independently of all transformed lists.
    passes = predicate(G,original)
    models = [z for z in product(range(m),repeat=9) if passes(z)]
    expected = {(labels[z[u]],project(G,z,S)) for z in models}
    actual = set(); stats = [0]*7; blocks=0
    # Direct untiled reference for each side and color.
    refs=[]
    for B,C,T in zip(bags,shared,extras):
        refs.append([{project(B,z,S) for z in product(range(m),repeat=8)
                      if p(z)} for k in range(K)
                     for p in [predicate(B,C|{(h,z) for c,h,z in T if c==k})]])
    for J in product(range((m+b-1)//b),repeat=7):
        blocks+=1; accs=[]
        for side,(B,C,T) in enumerate(zip(bags,shared,extras)):
            p = u if side==0 else v
            acc=None
            for j in range((m+b-1)//b):
                off=tuple(b*(j if g==p else J[S.index(g)]) for g in B)
                slots,out=tile(B,S,m,b,d,K,off,C,T,stats)
                if acc is None: acc=[None]*len(out)
                for i,z in enumerate(out):
                    if z is not None:
                        if acc[i] is not None: stats[4]+=1
                        else: acc[i]=z
                    stats[5]+=1
            for k in range(K):
                got={project(B,z,S) for z in acc[k*len(slots):(k+1)*len(slots)] if z is not None}
                exp={z for z in refs[side][k] if tuple(a//b for a in z)==J}
                check(got==exp,'exact side/color block')
                stats[6]+=len(got)
            accs.append(acc)
        for i,(x,y) in enumerate(zip(*accs)):
            if x is None or y is None: continue
            k=i//len(slots)
            key=tuple(b*j+a for j,a in zip(J,slots[i%len(slots)]))
            check(project(bags[0],x,S)==project(bags[1],y,S)==key,'aligned key')
            z=dict(zip(bags[0],x)); z.update(zip(bags[1],y)); z=tuple(z[g] for g in G)
            check(passes(z) and labels[z[u]]==k and (k,key) not in actual,'joined witness')
            actual.add((k,key))
    check(actual==expected,'complete projected model set')
    return [m,mode,K,len(original),len(common),len(tagged),len(models),len(actual),blocks,*stats]


def audit():
    rows=[fixture(m,mode,0 if mode%2==0 else 8,8 if mode%2==0 else 0,2,2)
          for m in (2,3) for mode in range(8)]
    # Nonconsecutive classes and a padded inner layout at scale 3, reduced outer size.
    rows.append(fixture(3,7,0,8,3,2))
    for a in (Fraction(0),Fraction(1,7),Fraction(1,5),Fraction(1,6)):
        beta=(3-a)/7
        e=Fraction(62,7)+5*a/7
        check(11-5*beta==8+a+2*beta==e and a+7*beta==3 and beta>=a,'balanced exponent')
    check(Fraction(62,7)+Fraction(5,7)*Fraction(1,5)==9,'threshold')
    result={'fixtures':len(rows),'sums':[sum(row[i] for row in rows) for i in range(2,len(rows[0]))]}
    print('F038_UNRESTRICTED_BATCHED_COLORS_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__=='__main__':
    audit()
