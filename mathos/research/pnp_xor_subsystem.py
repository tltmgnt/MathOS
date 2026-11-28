"""Partial affine CNF extraction with independently checked original-clause witnesses."""
from collections import defaultdict
from itertools import product
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_hall_certificate import verify as verify_model

MAX_WIDTH = 4
MAX_FREE = 12


def eligible(f):
    # Cheap route gate, not a semantic claim. Repeated clauses can trigger
    # a probe but cannot establish an equation.
    counts = defaultdict(int)
    for c in f:
        scope = {abs(x) for x in c}
        if 3 <= len(scope) <= MAX_WIDTH:
            counts[tuple(sorted(scope))] += 1
    return sum(m >= 1 << (len(s)-1) for s,m in counts.items()) >= 2


def extract(f, b):
    groups = defaultdict(dict)
    for i,c in enumerate(f):
        b.tick(1+len(c))
        s = set(c)
        if any(-x in s for x in s):
            continue
        vs = tuple(sorted(abs(x) for x in s))
        if len(vs)>MAX_WIDTH:
            continue
        pattern = sum(1<<j for j,v in enumerate(vs) if -v in s)
        groups[vs].setdefault(pattern,i)
    rows = []
    for vs,found in sorted(groups.items()):
        for rhs in (0,1):
            forbidden = [p for p in range(1<<len(vs)) if p.bit_count()%2 != rhs]
            b.tick(1+len(forbidden))
            if forbidden and all(p in found for p in forbidden):
                rows.append({"scope":list(vs),"rhs":rhs,
                             "sources":[found[p] for p in forbidden]})
    return rows


def verify(n, clauses, result, b):
    f = validate(n, clauses)
    if result["decision"]=="sat":
        return verify_model(n,f,result,b)
    if result["decision"]!="unsat":
        raise ValueError("not a decision")
    rows = result["certificate"]
    if not isinstance(rows,list) or not rows or len(rows)>2*len(f):
        raise ValueError("invalid dual length")
    parity, rhs_total = set(),0
    for row in rows:
        vs,rhs,ids = row["scope"],row["rhs"],row["sources"]
        if (not isinstance(vs,list) or len(vs)>MAX_WIDTH
                or any(type(v) is not int or not 1<=v<=n for v in vs)
                or vs!=sorted(set(vs)) or type(rhs) is not int or rhs not in (0,1)
                or not isinstance(ids,list) or not ids or len(ids)>1<<MAX_WIDTH
                or any(type(i) is not int or not 0<=i<len(f) for i in ids)
                or len(set(ids))!=len(ids)):
            raise ValueError("invalid equation witness")
        cited = []
        for i in ids:
            c = f[i]
            b.tick(1+len(c))
            if set(map(abs,c))!=set(vs):
                raise ValueError("source scope mismatch")
            cited.append(c)
        # Deliberately independent of the extraction bit-pattern map:
        # evaluate all wrong-parity assignments against original clauses.
        for bits in product((False,True),repeat=len(vs)):
            if sum(bits)%2 == rhs:
                continue
            assignment = dict(zip(vs,bits))
            b.tick(1+sum(1+len(c) for c in cited))
            if all(any(assignment[abs(x)]==(x>0) for x in c) for c in cited):
                raise ValueError("equation not implied by cited clauses")
        parity.symmetric_difference_update(vs)
        rhs_total ^= rhs
        b.tick(1+len(vs))
    if parity or rhs_total!=1:
        raise ValueError("dual does not derive 0=1")
    return True


def propose(n, clauses, b):
    f = validate(n,clauses)
    rows = extract(f,b)
    if not rows:
        return None
    basis = {}
    # Bound logical provenance storage, not process RSS.
    b.cells(max(1,len(rows))*(min(n,len(rows))+1))
    for i,row in enumerate(rows):
        vs,rhs = row["scope"],row["rhs"]
        m = sum(1<<(v-1) for v in vs)
        t = 1<<i
        b.tick(1+len(vs))
        while m:
            b.tick()
            p = m.bit_length()-1
            if p not in basis:
                basis[p]=(m,rhs,t)
                break
            q,r,u=basis[p]
            m,rhs,t=m^q,rhs^r,t^u
        if not m and rhs:
            b.tick(i+1)
            return {"decision":"unsat",
                    "certificate":[rows[j] for j in range(i+1) if t>>j&1]}
    active = {abs(x)-1 for c in f for x in c}
    free = sorted(active-basis.keys())
    ordered = sorted(basis.items())
    # Try the zero-free solution first, even when nullity is large.
    # Enumerate only bounded nullspaces; failed enumeration is UNKNOWN.
    count = 1<<len(free) if len(free)<=MAX_FREE else 1
    for j in range(count):
        b.tick(1+len(free))
        a = sum(1<<v for k,v in enumerate(free) if j>>k&1)
        for p,(m,rhs,_) in ordered:
            b.tick()
            if (m&a).bit_count()%2 != rhs:
                a |= 1<<p
        model = [bool(a>>i&1) for i in range(n)]
        ok = True
        for c in f:
            b.tick(1+len(c))
            if not any(model[abs(x)-1]==(x>0) for x in c):
                ok=False
                break
        if ok:
            return {"decision":"sat","certificate":model}
    return None


def attempt(n,f,total,seconds):
    b = Budget(seconds=seconds,max_steps=total,max_cells=200_000)
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
