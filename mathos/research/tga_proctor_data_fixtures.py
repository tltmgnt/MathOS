"""F034 data-only serialization and fixtures. No generated Lean source."""
from pathlib import Path
import sys

from . import tga_proctor_unified_bridge as unified


def _nat(v):
    if type(v) is not int or v<0:
        raise ValueError("natural token required")
    return [v]


def _seq(items,encode):
    items=tuple(items)
    return [len(items)]+[v for item in items for v in encode(item)]


def _lit(l):
    if type(l) is not int:
        raise ValueError("integer literal required")
    return [abs(l),int(l>0)]


def _clause(c):
    return _seq(c,_lit)


def _formula(cs):
    return _seq(cs,_clause)


def _ref(r):
    i,c=r
    return _nat(i)+_clause(c)


def _group(g):
    vs,c=g
    return _clause(vs)+_nat(c)


def _block(b):
    vs,rhs,rs=b
    return _seq(vs,_nat)+_nat(rhs)+_seq(rs,_ref)


def _step(s):
    a,b,p,t=s
    return _nat(a)+_nat(b)+_nat(p)+_clause(t)


def _terminal(tag,p):
    if tag=="EMPTY" and p is None:
        return [0]
    if tag=="CAPACITY":
        ds,gs,rs=p
        return [1]+_seq(ds,_ref)+_seq(gs,_group)+_seq(rs,_ref)
    if tag=="XOR":
        return [2]+_seq(p,_block)
    raise ValueError("unknown terminal")


def _bytes(values):
    return ("".join(str(v)+"\n" for v in values)).encode("ascii")


def encode_expected(n,f):
    return _bytes([3401]+_nat(n)+_formula(f))


def encode_envelope(env):
    n,f,(bs,aug,tag,p)=env
    if type(aug) is not bool:
        raise ValueError("Boolean scope required")
    return _bytes([3402]+_nat(n)+_formula(f)+
                  _seq(bs,lambda batch:_seq(batch,_step))+
                  [int(aug)]+_terminal(tag,p))


def cases():
    fs=[]
    for n,f,env,ok in unified.cases():
        if unified.check(n,f,env)!=ok:
            raise AssertionError("unified fixture disagreement")
        fs.append((encode_expected(n,f),encode_envelope(env),ok))
    # Known accepted empty-clause input; mutate either file in isolation.
    a=encode_expected(0,((),))
    b=encode_envelope((0,((),),((),False,"EMPTY",None)))
    bad=(
        (a+b"0\n",b),                          # trailing expected token
        (a,b+b"0\n"),                          # trailing certificate token
        (a[:-1],b),                            # missing LF
        (a,b[:-1]),                            # truncated proof
        (a.replace(b"3401",b"34x1",1),b),       # nondecimal
        (a,b.replace(b"\n",b"\r\n",1)),        # CRLF not canonical
        (b"0"+a,b),                            # leading zero
        (a,b.replace(b"3402",b"3401",1)),       # wrong file magic
        (b"3401\n0\n100001\n",b),              # oversized list count
        (b"3401\n"+b"9"*129+b"\n1\n0\n",b),   # oversized number
        (a,b[:-2]+b"9\n"),                     # unknown terminal tag
        (a,b[:-4]+b"2\n0\n"),                  # invalid scope bit
        (b"3401\n1\n1\n1\n1\n2\n",b),        # invalid literal bit
        (b"0"*1000001,b),                      # byte limit
    )
    fs.extend((x,y,False) for x,y in bad)
    return tuple(fs)


def emit(directory):
    d=Path(directory)
    d.mkdir(parents=True,exist_ok=True)
    fs=cases()
    for i,(a,b,ok) in enumerate(fs):
        (d/f"{i}.cnfdata").write_bytes(a)
        (d/f"{i}.proofdata").write_bytes(b)
        (d/f"{i}.verdict").write_bytes(b"1\n" if ok else b"0\n")
    return len(fs)


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python -m mathos.research.tga_proctor_data_fixtures OUTPUT_DIR")
    print("F034_DATA_FIXTURES",emit(sys.argv[1]))
