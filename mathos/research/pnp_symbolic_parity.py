"""Symbolic synthesis of exact charge criteria for explicit GF(2) systems.

Rows and charge vectors are nonnegative integer bit masks. A verified
invertible row-operation trace certifies rank and a complete independent
basis of compatibility checks. No enumeration of charge vectors is needed.
"""
from .pnp_evidence_benchmark import digest

MAX_ROWS=128
MAX_COLS=256


def validate(n,rows):
    if type(n) is not int or not 0<=n<=MAX_COLS:
        raise ValueError("invalid column count")
    if not isinstance(rows,(tuple,list)) or len(rows)>MAX_ROWS:
        raise ValueError("invalid row count")
    if any(type(x) is not int or not 0<=x<1<<n for x in rows):
        raise ValueError("invalid coefficient row")
    return tuple(rows)


def _charge(m,x):
    if type(x) is not int or not 0<=x<1<<m:
        raise ValueError("invalid charge mask")
    return x


def parity(x):
    return x.bit_count()&1


def _op(rows,op):
    kind,i,j=op
    if kind=="swap":
        rows[i],rows[j]=rows[j],rows[i]
    else:
        rows[i]^=rows[j]


def _apply_bits(x,ops,b):
    for kind,i,j in ops:
        b.tick()
        if kind=="swap":
            if ((x>>i)^(x>>j))&1:
                x^=(1<<i)|(1<<j)
        elif x>>j&1:
            x^=1<<i
    return x


def _eliminate(n,rows,b):
    a=list(rows)
    m=len(a)
    b.cells(2*m+n)
    transform=[1<<i for i in range(m)]
    ops=[]
    pivots=[]
    r=0
    def record(kind,i,j):
        b.tick()
        op=(kind,i,j)
        _op(a,op)
        _op(transform,op)
        ops.append(op)
        b.cells(3*len(ops)+2*m+n)
    for col in range(n):
        pivot=None
        for j in range(r,m):
            b.tick()
            if a[j]>>col&1:
                pivot=j
                break
        if pivot is None:
            continue
        if pivot!=r:
            record("swap",r,pivot)
        for j in range(r+1,m):
            b.tick()
            if a[j]>>col&1:
                record("xor",j,r)
        pivots.append(col)
        r+=1
        if r==m:
            break
    return a,transform,ops,pivots


def synthesize(n,rows,b):
    """Counterexamples use inverse row operations, not sampled RHS vectors.

    Before adding check i, charge T^-1 e_(rank+i) passes every earlier
    check, but cannot be satisfied. Each new check is independent.
    """
    rows=validate(n,rows)
    a,t,ops,pivots=_eliminate(n,rows,b)
    rank=len(pivots)
    checks=t[rank:]
    refinements=[]
    for i,check in enumerate(checks):
        charge=_apply_bits(1<<(rank+i),reversed(ops),b)
        refinements.append({"charge":charge,"added_check":check})
    return {"schema":"mathos-pnp-symbolic-parity/1","input_sha256":digest([n,rows]),
            "rank":rank,"echelon":a,"operations":ops,"pivots":pivots,
            "checks":checks,"refinements":refinements}


def verify(n,rows,r,b):
    """Replay invertible operations and validate the symbolic counterexamples.

    No call to the synthesizer, search order, or empirical SAT oracle is
    trusted. Echelon rank and zero rows prove completeness for ALL RHS.
    """
    rows=validate(n,rows)
    m=len(rows)
    if r["schema"]!="mathos-pnp-symbolic-parity/1" or r["input_sha256"]!=digest([n,rows]):
        raise ValueError("input mismatch")
    ops=r["operations"]
    if not isinstance(ops,(tuple,list)) or len(ops)>m*m+m:
        raise ValueError("operation cap")
    b.cells(3*len(ops)+2*m+n)
    a=list(rows)
    t=[1<<i for i in range(m)]
    for op in ops:
        if (len(op)!=3 or op[0] not in ("swap","xor") or
                any(type(i) is not int or not 0<=i<m for i in op[1:]) or op[1]==op[2]):
            raise ValueError("invalid invertible row operation")
        b.tick()
        _op(a,op)
        _op(t,op)
    # Nonzero rows first; strictly increasing leading positions.
    pivots=[]
    zero=False
    for x in a:
        b.tick()
        if not x:
            zero=True
        else:
            k=(x&-x).bit_length()-1
            if zero or (pivots and k<=pivots[-1]):
                raise ValueError("not row echelon form")
            pivots.append(k)
    rank=len(pivots)
    checks=t[rank:]
    if (type(r["rank"]) is not int or r["rank"]!=rank or r["pivots"]!=pivots or
            r["echelon"]!=a or r["checks"]!=checks or len(r["refinements"])!=len(checks)):
        raise ValueError("invalid rank or check basis")
    for j,item in enumerate(r["refinements"]):
        c=_charge(m,item["charge"])
        if item["added_check"]!=checks[j]:
            raise ValueError("incorrect added compatibility equation")
        # Direct dot products establish all earlier checks pass, and
        # in fact exactly the omitted check j fails.
        for i,h in enumerate(checks):
            b.tick()
            if parity(c&h)!=int(i==j):
                raise ValueError("counterexample does not isolate check")
    return True


def decide(n,rows,r,charge,b):
    """Decision for a new RHS using the verified symbolic criterion."""
    rows=validate(n,rows)
    _charge(len(rows),charge)
    verify(n,rows,r,b)
    for h in r["checks"]:
        b.tick()
        if parity(h&charge):
            return {"decision":"unsat","dependency":h}
    rhs=_apply_bits(charge,r["operations"],b)
    x=0
    for i in reversed(range(r["rank"])):
        b.tick()
        if parity(r["echelon"][i]&x)!=((rhs>>i)&1):
            x|=1<<r["pivots"][i]
    return {"decision":"sat","assignment":x}


def verify_decision(n,rows,charge,p,b):
    rows=validate(n,rows)
    m=len(rows)
    _charge(m,charge)
    if p["decision"]=="sat":
        x=p["assignment"]
        if type(x) is not int or not 0<=x<1<<n:
            raise ValueError("invalid assignment")
        for i,a in enumerate(rows):
            b.tick()
            if parity(a&x)!=(charge>>i&1):
                raise ValueError("assignment fails equation")
    elif p["decision"]=="unsat":
        h=_charge(m,p["dependency"])
        a=0
        for i,row in enumerate(rows):
            b.tick()
            if h>>i&1:
                a^=row
        if a or parity(h&charge)!=1:
            raise ValueError("invalid dependency contradiction")
    else:
        raise ValueError("invalid decision")
    return True
