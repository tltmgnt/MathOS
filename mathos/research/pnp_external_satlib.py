"""Strict external DIMACS ingress and a bounded independent DRUP checker."""
import hashlib
import json
from pathlib import Path
from .pnp_structural_kernel import validate, Budget, Exhausted
from .pnp_proof_library import rup
from .pnp_proof_abstraction import _original_clauses
from .pnp_hall_certificate import verify as verify_model

MANIFEST = Path(__file__).with_name("pnp_external_satlib_manifest.json")
MAX_BYTES=4_000_000
MAX_LINES=40_000


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def blob_sha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def parse_dimacs(data):
    if len(data)>MAX_BYTES:
        raise ValueError("input byte cap")
    n=m=None
    pending,clauses=[],[]
    ended=False
    for line in data.decode("ascii").splitlines():
        line=line.strip()
        if not line or line.startswith("c"):
            continue
        if ended:
            if line!="0":
                raise ValueError("unexpected text after SATLIB terminator")
            continue
        if line=="%":
            if pending or n is None or len(clauses)!=m:
                raise ValueError("premature terminator")
            ended=True
            continue
        if line.startswith("p"):
            fields=line.split()
            if n is not None or len(fields)!=4 or fields[:2]!=["p","cnf"]:
                raise ValueError("invalid or repeated DIMACS header")
            n,m=map(int,fields[2:])
            if not 0<=n<=512 or not 0<=m<=20_000:
                raise ValueError("header outside research scope")
            continue
        if n is None:
            raise ValueError("clause before header")
        for token in line.split():
            v=int(token)
            if abs(v)>n:
                raise ValueError("literal outside header")
            if v:
                pending.append(v)
            else:
                clauses.append(pending)
                pending=[]
                if len(clauses)>m:
                    raise ValueError("too many clauses")
    if n is None or pending or len(clauses)!=m:
        raise ValueError("missing header, clause terminator or clause count mismatch")
    validate(n,clauses)
    return n,clauses


def read_case(root,c):
    path=Path(root)/c["path"]
    data=path.read_bytes()
    if len(data)!=c["size"] or blob_sha(data)!=c["blob"]:
        raise ValueError("pinned external blob mismatch: "+c["path"])
    return data


def verify_drup(n,f,lines,b):
    """Ignore deletion hints, retaining a superset of proved clauses.
    This is sound for RUP (monotone unit-refutation entailment).
    An unsupported or invalid addition is not accepted as a proof.
    """
    if (not isinstance(lines,list) or len(lines)>MAX_LINES
            or any(not isinstance(x,str) for x in lines)
            or sum(len(x)+1 for x in lines)>MAX_BYTES):
        raise Exhausted("proof size cap")
    known=sorted(_original_clauses(n,f))
    literals=0
    for line in lines:
        fields=line.split()
        if not fields:
            raise ValueError("empty proof line")
        deletion=fields[0]=="d"
        if deletion:
            fields=fields[1:]
        vals=list(map(int,fields))
        if not vals or vals[-1]!=0 or 0 in vals[:-1]:
            raise ValueError("invalid DRUP terminator")
        c=validate(n,[vals[:-1]])[0]
        b.tick(1+len(c))
        if deletion:
            continue
        c=tuple(sorted(set(c)))
        if not rup(known,c,b):
            raise ValueError("non-RUP external proof step")
        known.append(c)
        literals+=len(c)
        b.cells(len(known)+literals)
    if () not in known:
        # Some solvers omit the final empty step on a root conflict.
        # Credit only if replay itself proves this step.
        if not rup(known,(),b):
            raise ValueError("external proof did not refute formula")
    return True


def verify_external(n,f,result,b):
    d=result["decision"]
    if d=="sat":
        return verify_model(n,f,result,b)
    if d=="unsat":
        return verify_drup(n,f,result["certificate"],b)
    raise ValueError("unknown is not a proof")


def glucose(n,f):
    from pysat.solvers import Glucose4
    with Glucose4(bootstrap_with=f,with_proof=True) as solver:
        sat=solver.solve()
        stats=solver.accum_stats()
        if sat:
            literals=solver.get_model() or []
            model={abs(x):x>0 for x in literals}
            p=[model.get(i,False) for i in range(1,n+1)]
            return {"decision":"sat","certificate":p,"solver_stats":stats}
        return {"decision":"unsat","certificate":solver.get_proof() or [],"solver_stats":stats}
