"""Exact bounded-degree closure in the square-free Boolean polynomial ring.

Addition and multiplication by a single variable are the only inference
rules. Degree is measured after reduction x_i^2=x_i. The closed-space
certificate checks ALL eligible linear combinations, not only basis
vectors whose individual products fit the degree cap.
"""
from .pnp_boolean_lift import polynomial,_expected_polynomial
from .pnp_structural_kernel import normalize,Exhausted
from .pnp_unified_portfolio import fingerprint

MAX_VARIABLES=8
MAX_RECORDS=20000


def _input(n,f,d):
    if type(d) is not int or not 0<=d<=MAX_VARIABLES:
        raise ValueError("invalid degree")
    nn,g,m=normalize(n,f)
    if nn>MAX_VARIABLES or any(len(c)>d for c in g):
        raise Exhausted("variable or input degree cap")
    return nn,g,m


def _mask(terms):
    return sum(1<<t for t in terms)


def _high(n,d):
    return _mask(t for t in range(1<<n) if t.bit_count()>d)


def _mul(p,v,b):
    q=0
    while p:
        b.tick()
        t=p&-p
        p^=t
        q^=1<<((t.bit_length()-1)|(1<<v))
    return q


def _reduce(p,basis,b):
    while p:
        b.tick()
        k=p.bit_length()-1
        if k not in basis:
            break
        p^=basis[k]
    return p


def derive(n,f,b,*,degree):
    nn,g,m=_input(n,f,degree)
    high=_high(nn,degree)
    known=[_mask(polynomial(c)) for c in g]
    steps=[]
    basis={}
    def record(op,i,j):
        b.tick()
        if len(known)>=MAX_RECORDS:
            raise Exhausted("polynomial record cap")
        p=known[i]^known[j] if op=="xor" else _mul(known[i],j,b)
        if p&high:
            raise AssertionError("inference exceeds degree")
        steps.append([op,i,j])
        known.append(p)
        b.cells(len(known))
        return len(known)-1
    def add(i):
        while known[i]:
            b.tick()
            k=known[i].bit_length()-1
            if k not in basis:
                basis[k]=i
                return
            i=record("xor",i,basis[k])
    for i in range(len(g)):
        add(i)
        if 0 in basis:
            break
    rounds=0
    while 0 not in basis:
        before=len(basis)
        rounds+=1
        for v in range(nn):
            # Eliminate high-degree product terms while tracking valid
            # combinations of the original (low-degree) basis records.
            H={}
            for i in list(basis.values()):
                p=_mul(known[i],v,b)&high
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
                    add(record("mul",i,v))
                if 0 in basis:
                    break
            if 0 in basis:
                break
        if len(basis)==before:
            break
    return {"schema":"mathos-pnp-degree-closure/1","input_sha256":fingerprint(n,f),
            "normalized_n":nn,"new_to_old":m,"degree":degree,"steps":steps,
            "basis":list(basis.values()),"root":basis.get(0),
            "status":"refuted" if 0 in basis else "closed_no_refutation",
            "rounds":rounds}


def verify(n,f,r,b):
    nn,g,m=_input(n,f,r["degree"])
    high=_high(nn,r["degree"])
    if (r["schema"]!="mathos-pnp-degree-closure/1" or r["input_sha256"]!=fingerprint(n,f)
            or r["normalized_n"]!=nn or tuple(r["new_to_old"])!=m
            or len(g)+len(r["steps"])>MAX_RECORDS):
        raise ValueError("invalid degree certificate metadata")
    # Independent initial polynomial reconstruction.
    known=[_mask(_expected_polynomial(c,0,b)) for c in g]
    for op,i,j in r["steps"]:
        if type(i) is not int or not 0<=i<len(known) or type(j) is not int:
            raise ValueError("invalid operand")
        if op=="xor" and 0<=j<len(known):
            p=known[i]^known[j]
        elif op=="mul" and 0<=j<nn:
            # Independent multiplication using membership of each
            # square-free monomial rather than the sparse producer loop.
            p=0
            for t in range(1<<nn):
                b.tick()
                if known[i]>>t&1:
                    p^=1<<(t|(1<<j))
        else:
            raise ValueError("invalid inference")
        if p&high:
            raise ValueError("degree limit violated")
        known.append(p)
        b.cells(len(known))
    refs=r["basis"]
    if (len(refs)>1<<nn or len(set(refs))!=len(refs) or
            any(type(i) is not int or not 0<=i<len(known) for i in refs)):
        raise ValueError("invalid basis references")
    B={}
    for i in refs:
        p=_reduce(known[i],B,b)
        if not p:
            raise ValueError("dependent basis")
        B[p.bit_length()-1]=p
    root=r["root"]
    if r["status"]=="refuted":
        if type(root) is not int or root not in refs or known[root]!=1:
            raise ValueError("missing constant contradiction")
    elif r["status"]=="closed_no_refutation":
        if root is not None or not _reduce(1,B,b):
            raise ValueError("closed space contains contradiction")
        for p in known[:len(g)]:
            if _reduce(p,B,b):
                raise ValueError("axiom outside closed space")
        # For each variable, high-part elimination on the FULL
        # products produces a spanning set of the kernel. Every
        # resulting low-degree product must lie in B.
        for v in range(nn):
            H={}
            for p in B.values():
                q=_mul(p,v,b)
                while q&high:
                    b.tick()
                    k=(q&high).bit_length()-1
                    if k not in H:
                        H[k]=q
                        break
                    q^=H[k]
                if not q&high and _reduce(q,B,b):
                    raise ValueError("space not closed under eligible multiplication")
    else:
        raise ValueError("invalid status")
    if type(r["rounds"]) is not int or not 0<=r["rounds"]<=(1<<nn)+1:
        raise ValueError("invalid observed round count")
    return True


def adaptive(n,f,budget_factory):
    nn,g,_=normalize(n,f)
    if nn>MAX_VARIABLES:
        raise Exhausted("variable cap")
    start=max(map(len,g),default=0)
    attempts=[]
    for d in range(start,nn+1):
        try:
            r=derive(n,f,budget_factory(),degree=d)
            verify(n,f,r,budget_factory())
        except Exhausted:
            attempts.append({"degree":d,"status":"resource_exhausted","proof":None})
            break
        attempts.append({"degree":d,"status":r["status"],"proof":r})
        if r["status"]=="refuted":
            break
    return attempts


def verify_adaptive(n,f,attempts,budget_factory):
    nn,g,_=normalize(n,f)
    if nn>MAX_VARIABLES or not attempts:
        raise ValueError("invalid adaptive input")
    start=max(map(len,g),default=0)
    if len(attempts)>nn-start+1:
        raise ValueError("too many attempts")
    for i,a in enumerate(attempts):
        if a["degree"]!=start+i:
            raise ValueError("nonconsecutive degree")
        if a["status"]=="resource_exhausted":
            if a["proof"] is not None or i!=len(attempts)-1:
                raise ValueError("invalid exhaustion")
        else:
            p=a["proof"]
            if p["degree"]!=a["degree"] or p["status"]!=a["status"]:
                raise ValueError("attempt mismatch")
            verify(n,f,p,budget_factory())
            if a["status"]=="refuted" and i!=len(attempts)-1:
                raise ValueError("search continued after refutation")
    a=attempts[-1]
    if a["status"]=="closed_no_refutation" and a["degree"]!=nn:
        raise ValueError("premature search termination")
    return True
