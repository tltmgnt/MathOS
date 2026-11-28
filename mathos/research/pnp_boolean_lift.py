"""Certified bounded Boolean monomial lifting.

Each normalized clause is encoded as its falsification indicator = 0
in GF(2)[x]/(x_i^2-x_i). Multiplying by a monomial preserves necessity.
Independent monomial columns relax the nonlinear consistency conditions.
An inconsistent linear system refutes the CNF; a consistent one does not
establish SAT unless the projected assignment satisfies the original CNF.
"""
from itertools import product
from .pnp_structural_kernel import normalize,Exhausted
from .pnp_unified_portfolio import fingerprint
from .pnp_symbolic_parity import (MAX_ROWS,MAX_COLS,synthesize,decide,
                                 verify_decision)

MAX_VARIABLES=12
MAX_DEGREE=4


def _input(n,f,degree,mode):
    if type(degree) is not int or not 1<=degree<=MAX_DEGREE or mode not in ("base","multiply"):
        raise ValueError("invalid lift configuration")
    nn,g,m=normalize(n,f)
    if nn>MAX_VARIABLES or any(len(c)>degree for c in g):
        raise Exhausted("lift variable or degree cap")
    return nn,g,m


def polynomial(c):
    """Expand the product of literal falsification indicators."""
    p={0}
    for x in c:
        v=1<<(abs(x)-1)
        q=set()
        for a in p:
            if x>0:
                q.symmetric_difference_update((a,))
            q.symmetric_difference_update((a|v,))
        p=q
    return p


def _multiply(p,v):
    q=set()
    for a in p:
        q.symmetric_difference_update((a|v,))
    return q


def _expected_polynomial(c,multiplier,b):
    """Independent coefficient reconstruction via truth-table Möbius transform.

    Only the clause variables and at most one multiplier variable occur.
    """
    scope=sorted({abs(x)-1 for x in c}|{i for i in range(MAX_VARIABLES) if multiplier>>i&1})
    values=[]
    for bits in range(1<<len(scope)):
        b.tick(1+len(c))
        a=sum((bits>>i&1)<<v for i,v in enumerate(scope))
        values.append(int((a&multiplier)==multiplier and
                          not any(bool(a>>(abs(x)-1)&1)==(x>0) for x in c)))
    for i in range(len(scope)):
        for j in range(1<<len(scope)):
            if j>>i&1:
                b.tick()
                values[j]^=values[j^(1<<i)]
    return {sum((j>>i&1)<<v for i,v in enumerate(scope))
            for j,val in enumerate(values) if val}


def _matrix(nn,g,degree,mode,b,*,replay=False):
    polys=[]
    sources=[]
    seen=set()
    columns={1<<i for i in range(nn)}
    multipliers=[0]+([1<<i for i in range(nn)] if mode=="multiply" else [])
    for j,c in enumerate(g):
        p=polynomial(c) if not replay else None
        for v in multipliers:
            b.tick()
            q=_multiply(p,v) if not replay else _expected_polynomial(c,v,b)
            if not q or any(x.bit_count()>degree for x in q):
                continue
            key=tuple(sorted(q))
            if key in seen:
                continue
            if len(polys)>=MAX_ROWS:
                raise Exhausted("linear row cap")
            seen.add(key)
            polys.append(q)
            sources.append((j,v))
            columns.update(q-{0})
            if len(columns)>MAX_COLS:
                raise Exhausted("monomial column cap")
    columns=sorted(columns)
    indices={x:i for i,x in enumerate(columns)}
    rows=[sum(1<<indices[x] for x in q if x) for q in polys]
    rhs=sum((0 in q)<<i for i,q in enumerate(polys))
    return columns,rows,rhs,sources


def _project(nn,columns,assignment):
    index={x:i for i,x in enumerate(columns)}
    return sum((assignment>>index[1<<i]&1)<<i for i in range(nn))


def _sat(g,x,b):
    valid=True
    for c in g:
        b.tick(1+len(c))
        valid &= any(bool(x>>(abs(v)-1)&1)==(v>0) for v in c)
    return bool(valid)


def _inconsistent_products(columns,assignment,x):
    return [a for i,a in enumerate(columns)
            if bool(assignment>>i&1)!=((x&a)==a)]


def propose(n,clauses,b,*,degree=3,mode="base"):
    nn,g,m=_input(n,clauses,degree,mode)
    cols,rows,rhs,sources=_matrix(nn,g,degree,mode,b)
    criterion=synthesize(len(cols),rows,b)
    proof=decide(len(cols),rows,criterion,rhs,b)
    if proof["decision"]=="unsat":
        x=None
        mismatches=[]
        decision="unsat"
    else:
        a=proof["assignment"]
        x=_project(nn,cols,a)
        mismatches=_inconsistent_products(cols,a,x)
        decision="sat" if _sat(g,x,b) else "unknown"
    return {"schema":"mathos-pnp-boolean-lift/1","input_sha256":fingerprint(n,clauses),
            "normalized_n":nn,"new_to_old":m,"degree":degree,"mode":mode,
            "monomials":cols,"sources":sources,"rows":rows,"rhs":rhs,
            "linear_proof":proof,"projected_assignment":x,
            "inconsistent_products":mismatches,"decision":decision}


def verify(n,clauses,r,b):
    nn,g,m=_input(n,clauses,r["degree"],r["mode"])
    if (r["schema"]!="mathos-pnp-boolean-lift/1" or r["input_sha256"]!=fingerprint(n,clauses)
            or r["normalized_n"]!=nn or tuple(r["new_to_old"])!=m):
        raise ValueError("lift binding mismatch")
    cols,rows,rhs,sources=_matrix(nn,g,r["degree"],r["mode"],b,replay=True)
    if (r["monomials"]!=cols or r["rows"]!=rows or r["rhs"]!=rhs or
            [tuple(x) for x in r["sources"]]!=sources):
        raise ValueError("lifted equations or provenance mismatch")
    p=r["linear_proof"]
    verify_decision(len(cols),rows,rhs,p,b)
    if p["decision"]=="unsat":
        x=None
        mismatches=[]
        decision="unsat"
    else:
        x=_project(nn,cols,p["assignment"])
        mismatches=_inconsistent_products(cols,p["assignment"],x)
        decision="sat" if _sat(g,x,b) else "unknown"
    if (r["projected_assignment"]!=x or r["inconsistent_products"]!=mismatches
            or r["decision"]!=decision):
        raise ValueError("incorrect lifted decision")
    return True
