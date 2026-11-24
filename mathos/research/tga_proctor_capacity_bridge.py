"""F034: export actual signed capacity certificates to the typed Lean checker.

Use original demand/conflict indices and annotate their exact rows. The
Lean checker accepts a broader sufficient proof language than Python.
"""
from itertools import product
from random import Random

from . import tga_proctor_capacity as cap
from . import tga_proctor_round_boundary as rounds
from . import tga_proctor_replay_bridge as bridge
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_xor_cnf as xor


def annotate(n,cs,proof):
    cs=xor._input(n,cs)
    if not cap.verify(n,cs,proof):
        raise ValueError("invalid capacity certificate")
    cert=proof["certificate"]
    ds=tuple((i,cs[i]) for i in cert["demands"])
    gs=tuple((vs,c) for vs,c,_ in cert["groups"])
    refs=tuple((i,cs[i]) for _,_,ids in cert["groups"] for i in ids)
    return ds,gs,refs


def check(n,cs,cert):
    """Same-author Python mirror of sufficient typed capacity semantics."""
    cs=xor._input(n,cs)
    try:
        ds,gs,refs=cert
        ds,gs,refs=tuple(ds),tuple(gs),tuple(refs)
        if not all(type(i) is int and 0<=i<len(cs) and tuple(row)==cs[i]
                   for i,row in ds+refs):
            return False
        used=set()
        for _,row in ds:
            vs={abs(l) for l in row}
            if used.intersection(vs):
                return False
            used.update(vs)
        covered=set()
        total=0
        for vs,c in gs:
            if type(c) is not int or not 0<=c<=2 or len(set(vs))!=len(vs):
                return False
            total+=c
            covered.update(vs)
            for ys in product(vs,repeat=c+1):
                if len(set(ys))==len(ys) and not any(
                    all(-l in ys for l in row) for _,row in refs):
                    return False
        return total<len(ds) and all(l in covered for _,row in ds for l in row)
    except (TypeError,ValueError,IndexError,AttributeError):
        return False


def cases():
    fs=[]
    for k,h in ((1,3),(1,4),(2,2),(2,3)):
        n,cs=cap.php(h,k)
        n,cs=blind.relabel(n,cs,29)
        proof=cap.solve(n,cs,k)
        cert=annotate(n,cs,proof)
        fs.append((n,cs,(),cs,cert,True))
    n,cs=rounds.guarded(*cap.php(4,1),2)
    n,cs=blind.relabel(n,cs,29)
    result=rounds.solve(n,cs,2)
    if result["status"]!="UNSAT" or result["certificate"][1]!="CAPACITY":
        raise AssertionError("expected chained capacity")
    batches,final=bridge.annotate(n,cs,result["certificate"][0])
    cert=annotate(n,final,result["certificate"][2])
    fs.append((n,cs,batches,final,cert,True))
    # Mixed capacities with duplicate literal occurrences in input.
    cs=((1,1),(2,),(3,),(4,),(-1,-2,-3))
    proof=dict(status="UNSAT",certificate=dict(demands=(0,1,2,3),
                 groups=(((1,2,3),2,(4,)),((4,),1,()))))
    cert=annotate(4,cs,proof)
    fs.append((4,cs,(),cs,cert,True))
    ds,gs,refs=cert
    bad=(
        (((99,ds[0][1]),)+ds[1:],gs,refs),
        (((0,(2,)),)+ds[1:],gs,refs),
        (ds+(ds[0],),gs,refs),
        (ds,gs[:-1],refs),
        (ds,(((1,1,2,3),2),)+gs[1:],refs),
        (ds,gs,()),
        (ds,gs,((4,(-1,-2)),)),
        (ds,gs,((99,refs[0][1]),)),
        (ds,(((1,2,3),3),)+gs[1:],refs),
    )
    fs.extend((4,cs,(),cs,c,False) for c in bad)
    # A satisfiable formula with enough slots: no strict deficiency.
    cs=((1,),(2,))
    fs.append((2,cs,(),cs,(((0,cs[0]),(1,cs[1])),(((1,),1),((2,),1)),()),False))
    # Sound zero-capacity extension: unit negative conflict.
    cs=((1,),(-1,))
    fs.append((1,cs,(),cs,(((0,cs[0]),),(((1,),0),),((1,cs[1]),)),True))
    return tuple(fs)


def emit_lean():
    fs=cases()
    lines=["","namespace CapacityFixtures",
           "open ProctorHallDeficiency ProctorCapacityReplay ProctorExecutableReplay"]
    data=bridge._LeanFixtureData(lines)
    for i,(n,cs,bs,final,cert,expected) in enumerate(fs):
        if bridge.check_shape(n,cs,bs)!=final or check(n,final,cert)!=expected:
            raise AssertionError("bridge fixture disagreement")
        ds,gs,refs=cert
        def references(rs):
            return data.sequence("List RefRow",(
                data.bind("RefRow","⟨"+bridge._nat(j)+","+data.clause(row)+"⟩")
                for j,row in rs))
        dr=references(ds)
        gr=data.sequence("List ProctorCapacityDeficiency.Group",(
            data.bind("ProctorCapacityDeficiency.Group","⟨"+data.clause(vs)+","+bridge._nat(c)+"⟩")
            for vs,c in gs))
        cr=references(refs)
        ff=data.formula(cs)
        bb=data.batches(bs)
        ft=data.formula(final)
        lines.extend((
            f"def f{i} : Formula := "+ff,
            f"def b{i} : List Batch := "+bb,
            f"def t{i} : Formula := "+ft,
            f"def c{i} : Certificate := ⟨{dr},{gr},{cr}⟩",
            f"def ok{i} : Bool := (decide (frontier f{i} b{i} = t{i})) && "
            + f"(checkChainCapacity f{i} b{i} c{i} == "+("true" if expected else "false")+")",
        ))
    lines.append("end CapacityFixtures")
    lines.append("def main : IO Unit := do")
    lines.append("  if "+bridge._list(f"CapacityFixtures.ok{i}" for i in range(len(fs)))+".all id then")
    lines.append(f'    IO.println "F034_CAPACITY_REPLAY_OK cases={len(fs)}"')
    lines.append('  else throw (IO.userError "F034 capacity replay disagreement")')
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    print(emit_lean(),end="")
