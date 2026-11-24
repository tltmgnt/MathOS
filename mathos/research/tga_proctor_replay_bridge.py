"""F034: bridge real Python paired certificates into executable Lean.

Python exports explicit annotated tails and checked natural indices.
Lean independently checks parent shape and indices, not discovery.
Terminal capacity/XOR proofs are still checked by Python only.
"""
from random import Random

from . import tga_proctor_round_boundary as rounds
from . import tga_proctor_combined_boundary as paired
from . import tga_proctor_mixed_routing as mixed
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_dynamic_resolution as graphs
from . import tga_proctor_blind_parity as blind
from .tga_proctor_hybrid_adversary import pigeonhole

PNP_RESOLUTION_STATUS = "OPEN"


def annotate(n,clauses,batches):
    """Convert existing replay triples to explicit checked-tail records."""
    current=xor._input(n,clauses)
    out=[]
    for batch in batches:
        batch=tuple(batch)
        if not batch:
            raise ValueError("empty batch")
        derived=paired.replay(n,current,batch)
        if derived is None:
            raise ValueError("invalid parent reference or tail")
        out.append(tuple((a,b,p,tail) for (a,b,p),tail in zip(batch,derived)))
        current=derived
    return tuple(out),current


def check_shape(n,clauses,batches):
    """Independent Python mirror of the weaker Lean shape predicate.

    Does not call paired.replay, normalization, inference or matching.
    Python input validation still shared. Accepts entailed weakening.
    """
    current=xor._input(n,clauses)
    try:
        for batch in batches:
            out=[]
            for a,b,p,tail in batch:
                if (any(type(i) is not int or not 0<=i<len(current) for i in (a,b))
                        or type(p) is not int or not 1<=p<=n):
                    return None
                tail=tuple(tail)
                if any(type(l) is not int or not 1<=abs(l)<=n for l in tail):
                    return None
                if not all(l==p or l in tail for l in current[a]):
                    return None
                if not all(l==-p or l in tail for l in current[b]):
                    return None
                out.append(tail)
            current=tuple(out)
        return current
    except (TypeError,ValueError,IndexError,AttributeError):
        return None


def _list(items):
    return "["+",".join(items)+"]"


def _nat(v):
    if type(v) is not int or v<0:
        raise ValueError("natural integer required")
    return str(v)


def _clause(c):
    return _list("("+_nat(abs(l))+","+("true" if l>0 else "false")+")" for l in c)


def _formula(cs):
    return _list(_clause(c) for c in cs)


def _batches(bs):
    return _list(_list("⟨"+",".join((_nat(a),_nat(b),_nat(p),_clause(t)))+"⟩"
                       for a,b,p,t in batch) for batch in bs)


def cases():
    """Actual certificates plus malformed and sound weakening controls."""
    fixtures=[]
    for name,base in (
        ("php4",pigeonhole(4)),
        ("tseitin4",graphs.tseitin(4,graphs.cubic_graph(4,11),(True,False,False,False))),
    ):
        n,cs=rounds.guarded(*base,2)
        n,cs=blind.relabel(n,cs,29)
        r=rounds.solve(n,cs,2)
        if r["status"]!="UNSAT" or not rounds.verify(n,cs,r):
            raise AssertionError("expected actual chained certificate")
        bs,final=annotate(n,cs,r["certificate"][0])
        fixtures.append((name,n,cs,bs,final,True,False))
    # Explicit two-round derivation to empty, not an assumed terminal proof.
    cs=((1,2),(1,-2),(-1,2),(-1,-2))
    a=mixed.derive(2,cs)
    b=mixed.derive(2,a["clauses"])
    bs,final=annotate(2,cs,(a["steps"],b["steps"]))
    if () not in final:
        raise AssertionError("missing empty clause")
    fixtures.append(("empty",2,cs,bs,final,True,True))
    # Index, dropped tail, and legitimate weakened tail controls.
    fixtures.extend((
        ("bad_index",2,((1,2),(-1,2)),(((2,1,1,(2,)),),),(),False,False),
        ("bad_tail",2,((1,2),(-1,2)),(((0,1,1,()),),),(),False,False),
        ("weakening",3,((1,2),(-1,2)),(((0,1,1,(2,3)),),),((2,3),),True,False),
    ))
    rng=Random(34003)
    for i in range(80):
        n=2**200
        ids=(10**40+1,10**40+31,10**40+61)
        cs=tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                       for _ in range(rng.randrange(5)))
                 for _ in range(rng.randrange(12)))
        a=mixed.derive(n,cs)
        bs,final=annotate(n,cs,(a["steps"],)) if a["steps"] else ((),cs)
        fixtures.append(("random"+str(i),n,cs,bs,final,True,() in final))
    return tuple(fixtures)


def emit_lean():
    """Generate only typed literal data from checked integer fields.

    No certificate-supplied identifiers or code. Lean checks the data
    using its executable definitions, not Python's verdict alone.
    """
    fs=cases()
    lines=["", "namespace ReplayFixtures", "open ProctorHallDeficiency ProctorExecutableReplay"]
    for i,(_,n,cs,bs,final,ok,empty) in enumerate(fs):
        expected=check_shape(n,cs,bs)
        if (expected is not None)!=ok or (ok and expected!=final):
            raise AssertionError("bridge fixture disagrees")
        lines.extend((
            f"def f{i} : Formula := "+_formula(cs),
            f"def b{i} : List Batch := "+_batches(bs),
            f"def t{i} : Formula := "+_formula(final),
            f"def ok{i} : Bool := "+
            (f"(chainCheck f{i} b{i}) && (decide (frontier f{i} b{i} = t{i})) && "+
             (f"checkEmpty f{i} b{i}" if empty else f"!(checkEmpty f{i} b{i})")
             if ok else f"!(chainCheck f{i} b{i}) && !(checkEmpty f{i} b{i})"),
        ))
    lines.append("end ReplayFixtures")
    lines.append("def main : IO Unit := do")
    lines.append("  if "+" && ".join(f"ReplayFixtures.ok{i}" for i in range(len(fs)))+" then")
    lines.append(f'    IO.println "F034_EXECUTABLE_REPLAY_OK cases={len(fs)}"')
    lines.append('  else throw (IO.userError "F034 executable replay disagreement")')
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    print(emit_lean(),end="")
