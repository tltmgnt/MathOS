"""Constructive resolution-to-Boolean-quotient simulation."""
from .pnp_boolean_lift import polynomial
from .pnp_degree_closure import _input,_mask,MAX_RECORDS,verify as verify_degree
from .pnp_resolution_refutation import verify as verify_resolution
from .pnp_unified_portfolio import fingerprint
from .pnp_structural_kernel import normalize,Exhausted


def lift(n,f,proof,b):
    verify_resolution(n,f,proof,b)
    nn,g,m=normalize(n,f)
    if nn>8:
        raise Exhausted("simulation variable cap")
    width=max([len(c) for c in g]+[len(s["clause"]) for s in proof["steps"]],default=0)
    d=min(nn,width+1)
    _input(n,f,d)
    clauses=list(g)
    known=[_mask(polynomial(c)) for c in g]
    refs=list(range(len(g)))
    steps=[]
    def record(op,i,j):
        b.tick()
        if len(known)>=MAX_RECORDS:
            raise Exhausted("simulation record cap")
        if op=="xor":
            p=known[i]^known[j]
        else:
            p=0
            q=known[i]
            while q:
                b.tick()
                t=q&-q
                q^=t
                p^=1<<((t.bit_length()-1)|(1<<j))
        if any((k.bit_count()>d) and (p>>k&1) for k in range(1<<nn)):
            raise AssertionError("simulation degree bound failed")
        steps.append([op,i,j])
        known.append(p)
        return len(known)-1
    def multiply_literals(i,ls):
        for x in ls:
            j=record("mul",i,abs(x)-1)
            i=record("xor",i,j) if x>0 else j
        return i
    for s in proof["steps"]:
        p,q,v=s["positive"],s["negative"],s["pivot"]
        a=[x for x in clauses[p] if x!=v]
        c=[x for x in clauses[q] if x!=-v]
        i=multiply_literals(refs[p],c)
        j=multiply_literals(refs[q],a)
        k=record("xor",i,j)
        if known[k]!=_mask(polynomial(s["clause"])):
            raise AssertionError("translated clause mismatch")
        refs.append(k)
        clauses.append(tuple(s["clause"]))
    root=refs[proof["root"]]
    if known[root]!=1:
        raise AssertionError("translation did not refute")
    return {"schema":"mathos-pnp-resolution-algebra/1","source":proof,"width":width,
            "translation":{"schema":"mathos-pnp-degree-closure/1",
                "input_sha256":fingerprint(n,f),"normalized_n":nn,"new_to_old":m,
                "degree":d,"steps":steps,"basis":[root],"root":root,
                "status":"refuted","rounds":0}}


def verify(n,f,r,b):
    if r["schema"]!="mathos-pnp-resolution-algebra/1":
        raise ValueError("invalid simulation schema")
    p=r["source"]
    verify_resolution(n,f,p,b)
    nn,g,_=normalize(n,f)
    w=max([len(c) for c in g]+[len(s["clause"]) for s in p["steps"]],default=0)
    q=r["translation"]
    if (r["width"]!=w or q["degree"]!=min(nn,w+1) or q["status"]!="refuted"
            or len(q["steps"])>(4*w+1)*len(p["steps"])):
        raise ValueError("translation overhead bound violated")
    verify_degree(n,f,q,b)
    return True
