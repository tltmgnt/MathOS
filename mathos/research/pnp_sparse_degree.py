"""Compressed fixed-degree Boolean quotient calculus and dual verification.

Monomials use dense coordinate indices, not bit positions equal to
variable-subset masks. All products with degree > D have a unique
preimage among degree <= D monomials for a fixed multiplier variable.
"""
from itertools import combinations
from math import comb
from .pnp_structural_kernel import normalize,Exhausted
from .pnp_boolean_lift import polynomial
from .pnp_unified_portfolio import fingerprint

MAX_VARIABLES=64
MAX_DEGREE=4
MAX_COORDINATES=4096
MAX_RECORDS=50000


def coordinates(n,d,b):
    if type(n) is not int or not 0<=n<=MAX_VARIABLES or type(d) is not int or not 0<=d<=MAX_DEGREE:
        raise ValueError("invalid coordinate dimensions")
    size=sum(comb(n,k) for k in range(min(n,d)+1))
    if size>MAX_COORDINATES:
        raise Exhausted("compressed dimension cap")
    b.cells(size)
    out=[]
    for k in range(min(n,d)+1):
        for vs in combinations(range(n),k):
            b.tick()
            out.append(sum(1<<v for v in vs))
    return tuple(sorted(out))


def _input(n,f,d,b):
    nn,g,m=normalize(n,f)
    if nn>MAX_VARIABLES or any(len(c)>d for c in g):
        raise Exhausted("variable or axiom degree cap")
    terms=coordinates(nn,d,b)
    return nn,g,m,terms,{t:i for i,t in enumerate(terms)}


def _encode(p,index):
    return sum(1<<index[t] for t in p)


def _bits(p):
    while p:
        t=p&-p
        yield t.bit_length()-1
        p^=t


def _map(terms,index,v,b):
    mapping=[]
    blocked=0
    for i,t in enumerate(terms):
        b.tick()
        j=index.get(t|(1<<v),-1)
        mapping.append(j)
        if j<0:
            blocked|=1<<i
    return mapping,blocked


def _mul(p,mapping,b):
    q=0
    for i in _bits(p):
        b.tick()
        j=mapping[i]
        if j<0:
            raise ValueError("ineligible multiplication")
        q^=1<<j
    return q


def _insert(p,B,b):
    while p:
        b.tick()
        k=p.bit_length()-1
        if k not in B:
            B[k]=p
            return
        p^=B[k]


def _reduce(p,B,b):
    while p:
        b.tick()
        k=p.bit_length()-1
        if k not in B:
            return p
        p^=B[k]
    return 0


def _annihilator(B,size,b):
    pivots=sorted(B)
    b.cells(size*max(1,(size+63)//64))
    H=[]
    for j in range(size):
        if j in B:
            continue
        h=1<<j
        for k in pivots:
            b.tick()
            if (B[k]&h).bit_count()&1:
                h|=1<<k
        H.append(h)
    return H


def _header(n,f,d,m,terms):
    return {"schema":"mathos-pnp-sparse-degree/1","input_sha256":fingerprint(n,f),
            "degree":d,"new_to_old":m,"dimension":len(terms)}


def derive(n,f,b,*,degree):
    nn,g,m,terms,index=_input(n,f,degree,b)
    known=[_encode(polynomial(c),index) for c in g]
    words=(len(terms)+63)//64
    if len(known)>MAX_RECORDS:
        raise Exhausted("axiom record cap")
    b.cells(len(known)*words)
    B={}
    steps=[]
    def record(op,i,j,mapping=None):
        b.tick()
        if len(known)>=MAX_RECORDS:
            raise Exhausted("compressed record cap")
        p=known[i]^known[j] if op=="xor" else _mul(known[i],mapping,b)
        known.append(p)
        steps.append([op,i,j])
        b.cells(len(known)*words)
        return len(known)-1
    def add(i):
        while known[i]:
            b.tick()
            k=known[i].bit_length()-1
            if k not in B:
                B[k]=i
                return
            i=record("xor",i,B[k])
    for i in range(len(g)):
        add(i)
        if 0 in B:
            break
    sweeps=0
    while 0 not in B:
        before=len(B)
        sweeps+=1
        for v in range(nn):
            mapping,blocked=_map(terms,index,v,b)
            H={}
            for i in list(B.values()):
                p=known[i]&blocked
                while p:
                    b.tick()
                    k=p.bit_length()-1
                    if k not in H:
                        H[k]=(p,i)
                        break
                    q,j=H[k]
                    p^=q
                    i=record("xor",i,j)
                if not p:
                    add(record("mul",i,v,mapping))
                if 0 in B:
                    break
            if 0 in B:
                break
        if len(B)==before:
            break
    r=_header(n,f,degree,m,terms)
    if 0 in B:
        # Only a refutation needs its derivation history.
        r.update(status="refuted",steps=steps,root=B[0],functionals=None)
    else:
        H=_annihilator({k:known[i] for k,i in B.items()},len(terms),b)
        r.update(status="closed_no_refutation",steps=None,root=None,functionals=H)
    r["observed_sweeps"]=sweeps
    return r


def evaluation(n,f,b,*,degree,assignment):
    """Direct dual from a verified model (dense normalized variable order)."""
    nn,g,m,terms,_=_input(n,f,degree,b)
    if type(assignment) is not int or not 0<=assignment<1<<nn:
        raise ValueError("invalid evaluation assignment")
    for c in g:
        b.tick(1+len(c))
        if not any(bool(assignment>>(abs(x)-1)&1)==(x>0) for x in c):
            raise ValueError("evaluation is not a model")
    h=sum(1<<i for i,t in enumerate(terms) if assignment&t==t)
    return {**_header(n,f,degree,m,terms),"status":"closed_no_refutation",
            "steps":None,"root":None,"functionals":[h],"observed_sweeps":0}


def _axiom(c,index,b):
    # Independent construction from local assignment values and
    # subset Möbius transform, without v29's twelve-variable limit.
    vs=sorted(abs(x)-1 for x in c)
    values=[]
    for a in range(1<<len(vs)):
        b.tick()
        bits=sum((a>>j&1)<<v for j,v in enumerate(vs))
        values.append(int(not any(bool(bits>>(abs(x)-1)&1)==(x>0) for x in c)))
    for j in range(len(vs)):
        for a in range(1<<len(vs)):
            if a>>j&1:
                b.tick()
                values[a]^=values[a^(1<<j)]
    return _encode((sum((a>>j&1)<<v for j,v in enumerate(vs))
                    for a,value in enumerate(values) if value),index)


def verify(n,f,r,b):
    d=r["degree"]
    nn,g,m,terms,index=_input(n,f,d,b)
    size=len(terms)
    words=(size+63)//64
    if (r["schema"]!="mathos-pnp-sparse-degree/1" or r["input_sha256"]!=fingerprint(n,f)
            or tuple(r["new_to_old"])!=m or r["dimension"]!=size
            or type(r["observed_sweeps"]) is not int or not 0<=r["observed_sweeps"]<=size+1):
        raise ValueError("invalid compressed binding")
    axioms=[_axiom(c,index,b) for c in g]
    if r["status"]=="refuted":
        steps=r["steps"]
        if r["functionals"] is not None or len(axioms)+len(steps)>MAX_RECORDS:
            raise ValueError("invalid proof size")
        known=axioms
        b.cells(len(known)*words)
        for op,i,j in steps:
            b.tick()
            if type(i) is not int or not 0<=i<len(known) or type(j) is not int:
                raise ValueError("invalid source record")
            if op=="xor" and 0<=j<len(known):
                p=known[i]^known[j]
            elif op=="mul" and 0<=j<nn:
                p=0
                for k in _bits(known[i]):
                    b.tick()
                    t=terms[k]|(1<<j)
                    if t not in index:
                        raise ValueError("degree exceeded")
                    p^=1<<index[t]
            else:
                raise ValueError("invalid algebraic operation")
            known.append(p)
            b.cells(len(known)*words)
        root=r["root"]
        if type(root) is not int or not 0<=root<len(known) or known[root]!=1:
            raise ValueError("missing constant refutation")
    elif r["status"]=="closed_no_refutation":
        H=r["functionals"]
        if (r["steps"] is not None or r["root"] is not None or
                not isinstance(H,list) or not 1<=len(H)<=size or
                any(type(h) is not int or not 0<h<1<<size for h in H) or
                not any(h&1 for h in H)):
            raise ValueError("invalid dual separation")
        b.cells(len(H)*words)
        B={}
        for h in H:
            _insert(h,B,b)
        if len(B)!=len(H):
            raise ValueError("dependent dual rows")
        for p in axioms:
            for h in H:
                b.tick()
                if (p&h).bit_count()&1:
                    raise ValueError("axiom outside dual kernel")
        for v in range(nn):
            mapping,blocked=_map(terms,index,v,b)
            # Restrict every dual row to eligible coordinates. The
            # high-part constraints are exactly the blocked singleton
            # coordinates, so span membership modulo them is sufficient.
            C={}
            for h in H:
                _insert(h&~blocked,C,b)
            for h in H:
                pull=0
                for i,j in enumerate(mapping):
                    b.tick()
                    if j>=0 and h>>j&1:
                        pull|=1<<i
                if _reduce(pull,C,b):
                    raise ValueError("dual kernel is not closed")
    else:
        raise ValueError("unknown proof status")
    return True
