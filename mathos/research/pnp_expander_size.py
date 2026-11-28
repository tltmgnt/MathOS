"""Expander Tseitin separation with exact finite spectral certificates.

Asymptotic claims import the Margulis–Gabber–Galil spectral theorem
and Ben-Sasson–Wigderson width–size theorem; neither is a Python test.
"""
from collections import Counter
from itertools import product
from .pnp_structural_kernel import validate
from .pnp_unified_portfolio import fingerprint

MAX_SIDE=10


def _side(s):
    if type(s) is not int or not 2<=s<=MAX_SIDE:
        raise ValueError("unsupported expander side")


def edges(s):
    """Four permutations and their inverses define the 8-regular multigraph.

    Keep every nonloop undirected edge occurrence, including parallel
    edges. Loops have zero cut contribution and cancel in parity rows.
    """
    _side(s)
    out=[]
    for x in range(s):
        for y in range(s):
            u=x*s+y
            for a,b in ((x+2*y,y),(x+2*y+1,y),(x,y+2*x),(x,y+2*x+1)):
                v=(a%s)*s+b%s
                if u!=v:
                    out.append((min(u,v),max(u,v)))
    return tuple(sorted(out))


def family(s,*,odd=True):
    if type(odd) is not bool:
        raise ValueError("invalid parity selector")
    e=edges(s)
    incident=[[] for _ in range(s*s)]
    for i,(u,v) in enumerate(e,1):
        incident[u].append(i)
        incident[v].append(i)
    # Even twin has two charged vertices, rather than a trivial zero model.
    rows=tuple((tuple(vs),int(j==0 or (not odd and j==1))) for j,vs in enumerate(incident))
    f=tuple(tuple(-v if bit else v for v,bit in zip(vs,bits))
            for vs,rhs in rows for bits in product((False,True),repeat=len(vs))
            if sum(bits)%2!=rhs)
    return len(e),f,rows


def _matrix(s,e):
    """Principal minor of 10 V L - 9 V I + 9 J (constant kernel)."""
    V=s*s
    L=[[0]*V for _ in range(V)]
    for u,v in e:
        L[u][u]+=1
        L[v][v]+=1
        L[u][v]-=1
        L[v][u]-=1
    return [[10*V*L[i][j]+9-(9*V if i==j else 0)
             for j in range(V-1)] for i in range(V-1)]


def spectral_pivots(s,e,b):
    """Bareiss leading principal determinants: exact positive minor test.

    Sylvester's criterion on the principal minor, plus the constant
    kernel, proves L >= (9/10) I on the orthogonal complement of ones.
    """
    a=_matrix(s,e)
    n=len(a)
    b.cells(n*n)
    previous=1
    result=[]
    for k in range(n):
        p=a[k][k]
        if p<=0:
            raise ValueError("nonpositive spectral certificate pivot")
        result.append(p)
        for i in range(k+1,n):
            for j in range(k+1,n):
                b.tick()
                q,r=divmod(a[i][j]*p-a[i][k]*a[k][j],previous)
                if r:
                    raise ValueError("nonexact Bareiss division")
                a[i][j]=q
        previous=p
    return result


def _tree_model(s,e,rows,b):
    """Solve the even-charge instance by a spanning-tree parity assignment."""
    V=s*s
    g=[[] for _ in range(V)]
    for i,(u,v) in enumerate(e,1):
        g[u].append((v,i))
        g[v].append((u,i))
    parent={0:(-1,0)}
    order=[0]
    for u in order:
        for v,i in g[u]:
            b.tick()
            if v not in parent:
                parent[v]=(u,i)
                order.append(v)
    if len(order)!=V:
        raise ValueError("disconnected graph")
    residual=[rhs for _,rhs in rows]
    bits=[False]*len(e)
    for v in reversed(order[1:]):
        b.tick()
        u,i=parent[v]
        bits[i-1]=bool(residual[v])
        residual[u]^=residual[v]
    if residual[0]:
        raise ValueError("odd parity in SAT branch")
    return bits


def parameters(s,n,rows,odd):
    V=s*s
    w0=max(map(lambda r:len(r[0]),rows))
    # Balanced support U: |U|(1-|U|/V) >= 2V/9.
    # Spectral gap >= 9/10 gives width >= V/5.
    w=(V+4)//5 if odd else None
    gap=max(0,w-w0) if odd else None
    return {"vertices":V,"edge_variables":n,"initial_width":w0,
            "width_lower":w,"size_exponent_ratio":None if gap is None else [gap*gap,n]}


def certify(s,*,odd,b):
    n,f,rows=family(s,odd=odd)
    e=edges(s)
    r={"schema":"mathos-pnp-expander-size/1","side":s,"odd":odd,
       "input_sha256":fingerprint(n,f),"edges":e,"rows":rows,
       "spectral_gap_lower":[9,10],"spectral_pivots":spectral_pivots(s,e,b),
       "parameters":parameters(s,n,rows,odd),
       "decision_proof":{"kind":"xor_conflict","rows":list(range(s*s))} if odd else
                       {"kind":"sat_witness","assignment":_tree_model(s,e,rows,b)}}
    return r


def verify(s,n,clauses,r,b):
    """Verify graph multiplicity, exact encoding, finite spectrum and verdict."""
    _side(s)
    V=s*s
    f=validate(n,clauses)
    odd=r["odd"]
    if (type(odd) is not bool or r["schema"]!="mathos-pnp-expander-size/1" or r["side"]!=s or
            r["input_sha256"]!=fingerprint(n,f) or r["spectral_gap_lower"]!=[9,10]):
        raise ValueError("invalid certificate binding")
    e=tuple(tuple(a) for a in r["edges"])
    if n!=len(e) or n==0 or tuple(sorted(e))!=e:
        raise ValueError("invalid edge list")
    # Independent eight-neighbor directed multiplicity check, ignoring loops.
    directed=Counter()
    for x in range(s):
        for y in range(s):
            u=x*s+y
            for a,c in ((x+2*y,y),(x-2*y,y),(x+2*y+1,y),(x-2*y-1,y),
                        (x,y+2*x),(x,y-2*x),(x,y+2*x+1),(x,y-2*x-1)):
                v=(a%s)*s+c%s
                if v!=u:
                    directed[u,v]+=1
    actual=Counter()
    incident=[[] for _ in range(V)]
    for i,(u,v) in enumerate(e,1):
        b.tick()
        if any(type(x) is not int for x in (u,v)) or not 0<=u<v<V:
            raise ValueError("invalid nonloop edge")
        actual[u,v]+=1
        actual[v,u]+=1
        incident[u].append(i)
        incident[v].append(i)
    if actual!=directed or any(not 1<=len(vs)<=8 for vs in incident):
        raise ValueError("incorrect expander multiplicity")
    rows=r["rows"]
    if len(rows)!=V:
        raise ValueError("incomplete vertex rows")
    groups={}
    for c in f:
        b.tick(1+len(c))
        vs=tuple(sorted(abs(x) for x in c))
        if len(set(vs))!=len(c):
            raise ValueError("invalid clause support")
        mask=tuple(x<0 for x in sorted(c,key=abs))
        groups.setdefault(vs,[]).append(mask)
    scopes=set()
    for j,(raw,rhs) in enumerate(rows):
        vs=tuple(raw)
        if (any(type(v) is not int for v in vs) or vs!=tuple(incident[j]) or
                type(rhs) is not int or rhs!=int(j==0 or (not odd and j==1)) or vs in scopes):
            raise ValueError("incorrect vertex parity row")
        scopes.add(vs)
        expected=set()
        for bits in product((False,True),repeat=len(vs)):
            b.tick(1+len(vs))
            if sum(bits)%2!=rhs:
                expected.add(bits)
        block=groups.get(vs,[])
        if len(block)!=len(expected) or set(block)!=expected:
            raise ValueError("incorrect local parity encoding")
    if set(groups)!=scopes or r["parameters"]!=parameters(s,n,rows,odd):
        raise ValueError("incomplete encoding or bound metadata")
    pivots=r["spectral_pivots"]
    if any(type(p) is not int for p in pivots) or pivots!=spectral_pivots(s,e,b):
        raise ValueError("invalid exact spectral certificate")
    p=r["decision_proof"]
    if odd:
        if p["kind"]!="xor_conflict" or p["rows"]!=list(range(V)):
            raise ValueError("missing all-row XOR certificate")
        active=set()
        rhs=0
        for vs,q in rows:
            b.tick(1+len(vs))
            active.symmetric_difference_update(vs)
            rhs^=q
        if active or rhs!=1:
            raise ValueError("XOR conflict not established")
    else:
        bits=p["assignment"]
        if p["kind"]!="sat_witness" or len(bits)!=n or any(type(x) is not bool for x in bits):
            raise ValueError("invalid SAT witness")
        for c in f:
            b.tick(1+len(c))
            if not any(bits[abs(x)-1]==(x>0) for x in c):
                raise ValueError("SAT witness violates input")
    return True
