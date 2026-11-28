"""Checked restriction simulation, fresh-variable padding and parity escape.

Proof translators operate on ordinary non-tautological binary resolution
DAGs. The v13 verifier is the independent authority for both source
and translated proofs; no assumption about search optimality is made.
"""
from .pnp_structural_kernel import validate,normalize,Exhausted
from .pnp_resolution_refutation import verify,MAX_WIDTH,MAX_RECORDS
from .pnp_unified_portfolio import fingerprint


def _original(n,f):
    _,g,m=normalize(n,f)
    return tuple(tuple(sorted(m[x-1] if x>0 else -m[-x-1] for x in c)) for c in g)


def pad(n,clauses):
    """Replace each C by (C OR z) AND (C OR NOT z), z fresh."""
    f=_original(n,clauses)
    z=n+1
    g=tuple(tuple(sorted(c+(x,))) for c in f for x in (z,-z))
    validate(z,g)
    return z,g


def _fixed(n,assignments):
    result={}
    for v,bit in assignments:
        if type(v) is not int or not 1<=v<=n or type(bit) is not bool or v in result:
            raise ValueError("invalid partial assignment")
        result[v]=bit
    return result


def _restrict_clause(c,fixed):
    if any(abs(x) in fixed and fixed[abs(x)]==(x>0) for x in c):
        return None
    return tuple(x for x in c if abs(x) not in fixed)


def restrict(n,clauses,assignments):
    fixed=_fixed(n,assignments)
    return tuple(sorted({q for c in _original(n,clauses)
                         if (q:=_restrict_clause(c,fixed)) is not None}))


def verify_padding(n,f,g,b):
    """Check the entire transformed CNF, plus both constant restrictions."""
    validate(n+1,g)
    base=_original(n,f)
    expected={tuple(sorted(c+(x,))) for c in base for x in (n+1,-(n+1))}
    actual=set(_original(n+1,g))
    b.tick(1+sum(map(len,actual))+sum(map(len,expected)))
    if actual!=expected:
        raise ValueError("padding does not match source")
    for bit in (False,True):
        if set(restrict(n+1,g,[(n+1,bit)]))!=set(base):
            raise ValueError("padding restriction mismatch")
    return True


def _proof(nn,m,base,steps,root,width):
    count=len(base)+len(steps)
    if count>MAX_RECORDS or width>MAX_WIDTH:
        raise Exhausted("translated proof cap")
    return {"schema":"mathos-pnp-resolution-dag/1","normalized_n":nn,
            "new_to_old":m,"width_cap":max(1,width),"record_cap":max(1,count),
            "strategy":"ascending","steps":steps,"root":root}


def _literals(c,m):
    return tuple(sorted(m[x-1] if x>0 else -m[-x-1] for x in c))


def _dense(c,labels):
    return tuple(sorted(labels[x] if x>0 else -labels[-x] for x in c))


def lift_padding(n,clauses,source,b):
    """Derive each normalized source axiom once and replay the original DAG.

    At most m new resolution steps are introduced for m source axioms.
    Width increases at most to the maximum source axiom width.
    """
    verify(n,clauses,source,b)
    oldn,old,oldmap=normalize(n,clauses)
    z,g=pad(n,clauses)
    nn,base,m=normalize(z,g)
    labels={v:i+1 for i,v in enumerate(m)}
    refs={c:i for i,c in enumerate(base)}
    steps=[]
    remap={}
    width=source["width_cap"]
    if old:
        pivot=labels[z]
        for i,c in enumerate(old):
            actual=_dense(_literals(c,oldmap),labels)
            p=refs[tuple(sorted(actual+(pivot,)))]
            q=refs[tuple(sorted(actual+(-pivot,)))]
            b.tick(1+len(actual))
            remap[i]=len(base)+len(steps)
            steps.append({"positive":p,"negative":q,"pivot":pivot,"clause":actual})
            width=max(width,len(actual))
    for i,s in enumerate(source["steps"],len(old)):
        b.tick(1+len(s["clause"]))
        remap[i]=len(base)+len(steps)
        steps.append({"positive":remap[s["positive"]],"negative":remap[s["negative"]],
                      "pivot":labels[oldmap[s["pivot"]-1]],
                      "clause":_dense(_literals(s["clause"],oldmap),labels)})
    proof=_proof(nn,m,base,steps,remap[source["root"]],width)
    verify(z,g,proof,b)
    return proof


def project(n,clauses,source,assignments,b):
    """Restrict a refutation without increasing inference count or width.

    Every unsatisfied projected source record gets a derived subclause.
    Satisfied records need no representative. If a pivot was fixed,
    use the parent with the false pivot; if a representative lost its
    pivot, reuse it; otherwise resolve the representatives. The empty
    conclusion can have only the empty subclause.
    """
    verify(n,clauses,source,b)
    fixed=_fixed(n,assignments)
    _,old,oldmap=normalize(n,clauses)
    target=restrict(n,clauses,assignments)
    nn,base,m=normalize(n,target)
    labels={v:i+1 for i,v in enumerate(m)}
    known=[set(_literals(c,m)) for c in base]
    refs={tuple(sorted(c)):i for i,c in enumerate(known)}
    remap={}
    for i,c in enumerate(old):
        q=_restrict_clause(_literals(c,oldmap),fixed)
        if q is not None:
            remap[i]=refs[q]
    steps=[]
    for i,s in enumerate(source["steps"],len(old)):
        q=_restrict_clause(_literals(s["clause"],oldmap),fixed)
        b.tick(1+len(s["clause"]))
        if q is None:
            continue
        p0,q0=s["positive"],s["negative"]
        v=oldmap[s["pivot"]-1]
        if v in fixed:
            rep=remap[q0 if fixed[v] else p0]
        else:
            p,r=remap[p0],remap[q0]
            a,c=known[p],known[r]
            if v not in a:
                rep=p
            elif -v not in c:
                rep=r
            else:
                d=(a-{v})|(c-{-v})
                rep=len(known)
                steps.append({"positive":p,"negative":r,"pivot":labels[v],
                              "clause":_dense(d,labels)})
                known.append(d)
                b.cells(len(known))
        if not known[rep]<=set(q):
            raise ValueError("restricted representative not a subclause")
        remap[i]=rep
    proof=_proof(nn,m,base,steps,remap[source["root"]],source["width_cap"])
    verify(n,target,proof,b)
    if len(steps)>len(source["steps"]):
        raise AssertionError("restriction increased inference count")
    return target,proof


def actual_width(proof):
    return max((len(s["clause"]) for s in proof["steps"]),default=0)


def simulation(n,f,p,b):
    z,g=pad(n,f)
    verify_padding(n,f,g,b)
    lifted=lift_padding(n,f,p,b)
    projections=[]
    for bit in (False,True):
        residual,q=project(z,g,lifted,[(z,bit)],b)
        if set(residual)!=set(_original(n,f)):
            raise AssertionError("projection did not recover source")
        # z is unused after restriction, so v13 normalizes identically.
        verify(n,f,q,b)
        projections.append({"value":bit,"proof":q})
    return {"schema":"mathos-pnp-padding-simulation/1","source_sha256":fingerprint(n,f),
            "target_sha256":fingerprint(z,g),"source_proof":p,
            "lifted":lifted,"projections":projections}


def verify_simulation(n,f,r,b):
    z,g=pad(n,f)
    if (r["schema"]!="mathos-pnp-padding-simulation/1" or
            r["source_sha256"]!=fingerprint(n,f) or r["target_sha256"]!=fingerprint(z,g)):
        raise ValueError("simulation binding mismatch")
    verify_padding(n,f,g,b)
    p,l=r["source_proof"],r["lifted"]
    verify(n,f,p,b)
    verify(z,g,l,b)
    _,base,_=normalize(n,f)
    if (len(l["steps"])>len(p["steps"])+len(base) or
            actual_width(l)>max(actual_width(p),max(map(len,base),default=0))):
        raise ValueError("lift exceeded simulation bound")
    if len(r["projections"])!=2 or [x["value"] for x in r["projections"]]!=[False,True]:
        raise ValueError("missing restriction branch")
    for a in r["projections"]:
        bit=a["value"]
        if type(bit) is not bool:
            raise ValueError("invalid restriction value")
        residual=restrict(z,g,[(z,bit)])
        if set(residual)!=set(_original(n,f)):
            raise ValueError("restriction mismatch")
        verify(n,f,a["proof"],b)
        if len(a["proof"]["steps"])>len(l["steps"]) or actual_width(a["proof"])>actual_width(l):
            raise ValueError("projection exceeded simulation bound")
    return True
