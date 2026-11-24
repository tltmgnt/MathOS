"""F034: data-only DIMACS subset fixtures, no generated Lean source."""
from pathlib import Path
import sys

from . import tga_proctor_unified_bridge as unified
from . import tga_proctor_data_fixtures as wire


def encode_dimacs(n,cs):
    # Deliberately preserve order, duplicates and empty clauses.
    return (f"p cnf {n} {len(cs)}\n"+"".join(
        " ".join(str(l) for l in (*c,0))+"\n" for c in cs)).encode("ascii")


def cases():
    out=[]
    for n,f,env,ok in unified.cases():
        valid=all(type(l) is int and 1<=abs(l)<=n for c in f for l in c)
        out.append((encode_dimacs(n,f),wire.encode_envelope(env),
                    wire.encode_expected(n,f) if valid else None,ok))
    empty=wire.encode_envelope((0,((),),((),False,"EMPTY",None)))
    expected=wire.encode_expected(0,((),))
    out.extend((
        (b"p cnf 0 1\n0\n",empty,expected,True),
        (b"p cnf 0 1\n\t0 \r\n",empty,expected,True),
        (b"p cnf 0 1\r\n0",empty,expected,True),
        (b"p cnf 0 0\n",empty,wire.encode_expected(0,()),False),
        (b"p cnf 2 2\n1\n-2 1 0 0\n",empty,
         wire.encode_expected(2,((1,-2,1),())),False),
    ))
    bad=(
        b"p cnf 0 1",                 # header requires LF
        b"c comment\np cnf 0 1\n0\n", # comments unsupported
        b"p cnf 0 2\n0\n",           # too few clauses
        b"p cnf 0 1\n0 0\n",         # too many clauses
        b"p cnf 1 1\n1\n",           # missing zero
        b"p cnf 0 1\n-0\n",          # negative zero
        b"p cnf 1 1\n+1 0\n",        # plus unsupported
        b"p cnf 1 1\n01 0\n",        # leading zero
        b"p cnf 1 1\n2 0\n",         # out of range
        b"p cnf 0 1\n0 x\n",         # trailing token
        b"p cnf 0 1 0\n",             # extra header token
        b"p cnf 0 100001\n",          # count limit
        b"p cnf "+b"9"*129+b" 1\n0\n", # digit limit
        b"p cnf 0 1\n\xff0\n",      # non-ASCII
        b" "*1000001,                 # byte limit
    )
    out.extend((a,empty,None,False) for a in bad)
    return tuple(out)


def emit(directory):
    d=Path(directory)
    d.mkdir(parents=True,exist_ok=True)
    for i,(a,b,ref,ok) in enumerate(cases()):
        (d/f"{i}.cnf").write_bytes(a)
        (d/f"{i}.proofdata").write_bytes(b)
        (d/f"{i}.cnfdata").write_bytes(ref if ref is not None else b"")
        (d/f"{i}.parse").write_bytes(b"1\n" if ref is not None else b"0\n")
        (d/f"{i}.verdict").write_bytes(b"1\n" if ok else b"0\n")
    return len(cases())


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python -m mathos.research.tga_proctor_dimacs_fixtures OUTPUT_DIR")
    print("F034_DIMACS_FIXTURES",emit(sys.argv[1]))
