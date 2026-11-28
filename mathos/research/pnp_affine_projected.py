"""Bounded affine substitution and residual CDCL with checked lifting."""
from itertools import product
from .pnp_structural_kernel import Budget, Exhausted, validate
from . import pnp_xor_subsystem as xor
from . import pnp_conflict_learning as cdcl
from .pnp_hall_certificate import verify as verify_model

MAX_ROWS = 1024


def eligible(f):
    # Require a plausible parity block plus other scopes. Pure affine
    # and small formulas retain the already verified portfolio.
    counts = {}
    for c in f:
        s = tuple(sorted({abs(x) for x in c}))
        counts[s] = counts.get(s,0)+1
    blocks = {s for s,m in counts.items() if 3<=len(s)<=4 and m>=1<<(len(s)-1)}
    return bool(len(blocks)>=2 and set(counts)-blocks)


def _mask(vs):
    return sum(1<<(v-1) for v in vs)


def _indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()
        mask ^= bit


def parameterize(n,rows,b):
    """Highest-pivot echelon rows, then substitute lower pivots."""
    basis={}
    b.cells(max(1,len(rows))*(min(n,len(rows))+1))
    for i,row in enumerate(rows):
        m,rhs,prov=_mask(row["scope"]),row["rhs"],1<<i
        b.tick(1+len(row["scope"]))
        while m:
            p=m.bit_length()
            b.tick()
            if p not in basis:
                basis[p]=(m,rhs,prov)
                break
            q,r,t=basis[p]
            m,rhs,prov=m^q,rhs^r,prov^t
        if not m and rhs:
            return None,[rows[j-1] for j in _indices(prov)]
    forms={}
    for p,(m,rhs,prov) in sorted(basis.items()):
        m ^= 1<<(p-1)
        for v in list(_indices(m)):
            b.tick()
            if v in forms:
                q,r,t=forms[v]
                m ^= (1<<(v-1))^q
                rhs ^= r
                prov ^= t
        forms[p]=(m,rhs,prov)
    return [{"pivot":p,"support":list(_indices(m)),"rhs":rhs,
             "rows":[j-1 for j in _indices(t)]}
            for p,(m,rhs,t) in sorted(forms.items())],None


def _row_witness(n,f,row,b):
    vs,rhs,ids=row["scope"],row["rhs"],row["sources"]
    if (not isinstance(vs,list) or len(vs)>xor.MAX_WIDTH
            or any(type(v) is not int or not 1<=v<=n for v in vs)
            or vs!=sorted(set(vs)) or type(rhs) is not int or rhs not in (0,1)
            or not isinstance(ids,list) or not ids or len(ids)>16
            or any(type(i) is not int or not 0<=i<len(f) for i in ids)
            or len(set(ids))!=len(ids)):
        raise ValueError("invalid source row")
    cited=[f[i] for i in ids]
    if any(set(map(abs,c))!=set(vs) for c in cited):
        raise ValueError("source scope mismatch")
    # Require equivalence, not merely implication, to justify omitting
    # exactly these source clauses from the residual formula.
    cost=1+sum(1+len(c) for c in cited)
    for bits in product((False,True),repeat=len(vs)):
        b.tick(cost)
        a=dict(zip(vs,bits))
        holds=all(any(a[abs(x)]==(x>0) for x in c) for c in cited)
        if holds!=(sum(bits)%2==rhs):
            raise ValueError("source parity truth table mismatch")


def check_parameterization(n,f,rows,forms,b):
    if not isinstance(rows,list) or not 1<=len(rows)<=MAX_ROWS:
        raise ValueError("invalid row list")
    for row in rows:
        _row_witness(n,f,row,b)
    if not isinstance(forms,list) or len(forms)>n:
        raise ValueError("invalid forms")
    pivots=[r["pivot"] for r in forms]
    if (any(type(p) is not int or not 1<=p<=n for p in pivots)
            or pivots!=sorted(set(pivots))):
        raise ValueError("invalid pivots")
    free=set(range(1,n+1))-set(pivots)
    representations={v:({v},0) for v in free}
    for form in forms:
        p,vs,rhs,ids=(form[k] for k in ("pivot","support","rhs","rows"))
        if (not isinstance(vs,list) or any(type(v) is not int or v not in free for v in vs)
                or vs!=sorted(set(vs)) or type(rhs) is not int or rhs not in (0,1)
                or not isinstance(ids,list) or not ids
                or any(type(i) is not int or not 0<=i<len(rows) for i in ids)
                or ids!=sorted(set(ids))):
            raise ValueError("invalid substitution")
        parity=set()
        value=0
        for i in ids:
            row=rows[i]
            b.tick(1+len(row["scope"]))
            parity.symmetric_difference_update(row["scope"])
            value ^= row["rhs"]
        if parity!=set(vs)|{p} or value!=rhs:
            raise ValueError("substitution not implied")
        representations[p]=(set(vs),rhs)
    # Check the converse: every original extracted row vanishes
    # identically under these substitutions, so every free assignment
    # extends to a model of all omitted source clauses.
    for row in rows:
        parity=set()
        value=row["rhs"]
        for v in row["scope"]:
            s,r=representations[v]
            b.tick(1+len(s))
            parity.symmetric_difference_update(s)
            value ^= r
        if parity or value:
            raise ValueError("substitution does not satisfy a source row")
    return True


def compile_residual(n,f,rows,forms,b,*,checker=False):
    """Deterministic projection. XOR gate encoding checked by truth-table
    construction on replay, rather than the proposer's four-clause rule.
    """
    fm={r["pivot"]:r for r in forms}
    free=[v for v in range(1,n+1) if v not in fm]
    names={v:i+1 for i,v in enumerate(free)}
    total=len(free)
    clauses=[]
    cache={}
    omitted={i for row in rows for i in row["sources"]}
    constant=None
    def new():
        nonlocal total
        total+=1
        if total>512:
            raise Exhausted("projected variable limit")
        return total
    def emit(c):
        b.tick(1+len(c))
        if len(clauses)>=20_000:
            raise Exhausted("projected clause limit")
        clauses.append(tuple(c))
    def gate(a,c):
        key=tuple(sorted((a,c)))
        if key in cache:
            return cache[key]
        z=new()
        if checker:
            for x,y,w in product((0,1),repeat=3):
                if (x^y)!=w:
                    emit(tuple(-v if bit else v for v,bit in zip((a,c,z),(x,y,w))))
        else:
            for cl in ((a,c,-z),(a,-c,z),(-a,c,z),(-a,-c,-z)):
                emit(cl)
        cache[key]=z
        return z
    def representative(v):
        nonlocal constant
        if v in names:
            return names[v]
        row=fm[v]
        vs=row["support"]
        b.tick(1+len(vs))
        if not vs:
            if constant is None:
                constant=new()
                emit((constant,))
            lit=constant if row["rhs"] else -constant
        else:
            lit=names[vs[0]]
            for u in vs[1:]:
                lit=gate(lit,names[u])
            if row["rhs"]:
                lit=-lit
        names[v]=lit
        return lit
    for i,c in enumerate(f):
        b.tick(1+len(c))
        if i in omitted or any(-x in set(c) for x in c):
            continue
        emit(tuple(representative(abs(x)) if x>0 else -representative(abs(x)) for x in c))
    validate(total,clauses)
    return total,clauses,free


def lift(n,free,forms,model,b):
    a=[False]*n
    for i,v in enumerate(free):
        b.tick()
        a[v-1]=model[i]
    for row in forms:
        b.tick(1+len(row["support"]))
        a[row["pivot"]-1]=bool(row["rhs"] ^ (sum(a[v-1] for v in row["support"])%2))
    return a


def propose(n,clauses,b):
    f=validate(n,clauses)
    rows=xor.extract(f,b)
    if not rows:
        return None
    if len(rows)>MAX_ROWS:
        raise Exhausted("source row limit")
    forms,dual=parameterize(n,rows,b)
    if dual is not None:
        return {"decision":"unsat","kind":"dual","certificate":dual}
    pn,pf,free=compile_residual(n,f,rows,forms,b)
    p=cdcl.propose(pn,pf,b)
    if p["decision"]=="sat":
        return {"decision":"sat","kind":"lifted","certificate":lift(n,free,forms,p["certificate"],b)}
    return {"decision":"unsat","kind":"projected_rup","certificate":{
        "rows":rows,"forms":forms,"projected_n":pn,"proof":p["certificate"]}}


def verify(n,clauses,result,b):
    f=validate(n,clauses)
    kind,decision=result["kind"],result["decision"]
    if kind=="lifted" and decision=="sat":
        return verify_model(n,f,result,b)
    if kind=="dual" and decision=="unsat":
        return xor.verify(n,f,result,b)
    if kind!="projected_rup" or decision!="unsat":
        raise ValueError("invalid certificate kind")
    p=result["certificate"]
    rows,forms=p["rows"],p["forms"]
    check_parameterization(n,f,rows,forms,b)
    pn,pf,_=compile_residual(n,f,rows,forms,b,checker=True)
    if type(p["projected_n"]) is not int or p["projected_n"]!=pn:
        raise ValueError("projected dimension mismatch")
    return cdcl.verify(pn,pf,{"decision":"unsat","certificate":p["proof"]},b)


def attempt(n,f,total,seconds):
    b=Budget(seconds=seconds,max_steps=total,max_cells=200_000)
    p,status=None,"unrecognized"
    try:
        p=propose(n,f,b)
        if p is not None:
            verify(n,f,p,b)
            status="replayed"
    except Exhausted:
        p,status=None,"resource_exhausted"
    return {"decision":p["decision"] if p else "unknown",
            "status":status,"proof":p,"work_steps":b.steps}


def replay(n,f,r,total):
    p,w=r["proof"],r["work_steps"]
    if type(w) is not int or not 0<=w<=total:
        raise ValueError("invalid work")
    if r["status"]=="replayed":
        if p is None or p["decision"]!=r["decision"]:
            raise ValueError("missing proof")
        verify(n,f,p,Budget(seconds=15,max_steps=4_000_000,max_cells=200_000))
    elif r["status"] not in ("unrecognized","resource_exhausted") or p is not None or r["decision"]!="unknown":
        raise ValueError("invalid unknown")
    return True
