"""Reference regression for semantic rectangle barrier; not original-U compilation."""
import json
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_unrestricted_crossing_adversary import onehot, norm, true
from mathos.research.f038_unrestricted_universal_search import encoded, valid
from mathos.research.f038_universal_witness_layout import pool


def rectangle_checks():
    rows = []
    for M in range(9):
        K = 1 << M
        full = K - 1
        dis = crossed = 0
        for a in range(K):
            for b in range(K):
                first = next((j for j in range(M) if (a & b) >> j & 1), None)
                require((first is not None) == bool(a & b), 'intersection')
                if first is None:
                    # R_a covers (a,b); both subset conditions hold.
                    require(not (b & a), 'cover')
                    dis += 1
            for b in range(a + 1, K):
                require(bool((a & (full ^ b)) or (b & (full ^ a))), 'fooling set')
                crossed += 1
        require(dis == 3**M and crossed == K*(K-1)//2, 'counts')
        rows.append([M,K*K,dis,K,crossed])
    return rows


def extract(raw, m, n, C):
    # High-level semantic reference only. C is the canonical pool.
    require(raw[:n+1] == '1'*n+'0' and len(raw) == n+1+len(C), 'header')
    streams = [[], [], []]
    for c, bit in zip(C, raw[n+1:]):
        if len(c) != 3:
            continue
        for off, target in ((0,0),(6*m,1)):
            if all(c[k] < 0 and off+(k+1)*m < -c[k] <= off+(k+2)*m
                   for k in range(3)):
                streams[target].append(int(bit))
        if 10*m < c[0] <= n-2 and c[1:] == (1-n,-n):
            streams[2].append(int(bit))
    A,B,P = streams
    require(len(A)==len(B)==m**3 and len(P)==n-10*m-2, 'stream lengths')
    hit = next((j for j,(a,b) in enumerate(zip(A,B)) if not (a or b)), None)
    if hit is None:
        return streams, None
    digits = (hit//(m*m),hit//m%m,hit%m)
    ones = [10*m+1+i for i,b in enumerate(P) if b]
    for k,j in enumerate(digits):
        ones.extend(((k+1)*m+1+j,(k+7)*m+1+j))
        ones.extend(4*m+k*(m-1)+1+i for i in range(m-1) if j<=i+1)
    return streams, sum(1<<(i-1) for i in ones)


def layout_checks():
    rows = []
    # Reduced geometry with one pin; not the asymptotic n=101u subsequence.
    for m in (2,3):
        n = 10*m+3
        M = m**3
        X = [tuple(range((k+1)*m+1,(k+2)*m+1)) for k in range(3)]
        Z = [tuple(x+6*m for x in g) for g in X]
        Y = [tuple(range(4*m+k*(m-1)+1,4*m+(k+1)*(m-1)+1)) for k in range(3)]
        indices = tuple(product(range(m),repeat=3))
        A = [tuple(-X[k][j[k]] for k in range(3)) for j in indices]
        B = [tuple(-Z[k][j[k]] for k in range(3)) for j in indices]
        C = pool(n)
        loc = {c:i for i,c in enumerate(C)}
        checks = cases = 0
        for pin in (0,1):
            F = []
            used = set()
            for x,y,z in zip(X,Y,Z):
                F.extend(onehot(x,y))
                for a,b in zip(x,z):
                    F.extend(((-a,b),(a,-b)))
                used.update(x+y+z)
            p = 10*m+1
            used.add(p)
            F.extend((p if pin else -p,a,b) for a,b in product((1-n,n-1),(-n,n)))
            F.extend((-i,) for i in range(1,n+1) if i not in used)
            F = tuple(map(norm,F))
            require(len(set(F+tuple(A)+tuple(B)))==len(F)+2*M,'clause overlap')
            for mode in range(8):
                a = [int(1 if mode==0 else 0 if mode==1 else j%2==0 if mode==2
                         else j==M-1 if mode==3 else (j*17+mode*11)%13<6)
                     for j in range(M)]
                b = [int(0 if mode==0 else 1 if mode==1 else j%2==1 if mode==2
                         else j==M-1 if mode==3 else (j*19+mode*7)%11<5)
                     for j in range(M)]
                selected = F+tuple(c for c,v in zip(A,a) if v)+tuple(c for c,v in zip(B,b) if v)
                selector = sum(1<<loc[c] for c in selected)
                raw = encoded(n,selector,C)
                streams,w = extract(raw,m,n,C)
                require(streams==[a,b,[pin]],'stream content')
                j = next((j for j in range(M) if not (a[j] or b[j])),None)
                require((w is not None)==(j is not None),'witness existence')
                if w is not None:
                    require(valid(C,n,selector,w),'original verifier predicate')
                    for i in range(M):
                        require(true(A[i],w)==(i!=j) and true(B[i],w)==(i!=j),'index predicate')
                        checks += 2
                cases += 1
        rows.append([m,n,n+1+len(C),cases,checks])
    return rows


def audit():
    result = {'rectangles':rectangle_checks(),'layout':layout_checks()}
    require(result['layout']==[[2,23,15250,16,160],[3,33,45860,16,540]],'layout totals')
    print('F038_UNRESTRICTED_SEMANTIC_RECTANGLE_BARRIER_OK '+json.dumps(result,separators=(',',':'),sort_keys=True))
    return result


if __name__ == '__main__':
    audit()
