"""F034: real parity dual export and typed sparse GF(2) replay controls."""
from itertools import product

from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_round_boundary as rounds
from . import tga_proctor_replay_bridge as bridge
from . import tga_proctor_dynamic_resolution as graphs
from . import tga_proctor_blind_parity as blind


def annotate(n,cs,proof):
    cs=xor._input(n,cs)
    if not xor.verify(n,cs,proof) or proof["certificate"][0]!="xor":
        raise ValueError("valid parity dual required")
    return tuple((vs,rhs,tuple((i,cs[i]) for i in refs))
                 for vs,rhs,refs in proof["certificate"][1])


def check(n,cs,blocks):
    """Mirror the sufficient Lean predicate, without XOR discovery."""
    cs=xor._input(n,cs)
    try:
        acc=set()
        rhs_sum=0
        for vs,rhs,refs in blocks:
            vs,refs=tuple(vs),tuple(refs)
            if (len(vs)>5 or any(type(v) is not int or not 1<=v<=n for v in vs)
                    or type(rhs) is not int or rhs not in (0,1)
                    or not all(type(i) is int and 0<=i<len(cs) and tuple(row)==cs[i]
                               for i,row in refs)):
                return False
            for bits in product((False,True),repeat=len(vs)):
                if sum(bits)%2!=rhs:
                    false_lits={-v if b else v for v,b in zip(vs,bits)}
                    if not any(all(l in false_lits for l in row) for _,row in refs):
                        return False
            for v in vs:
                acc.symmetric_difference_update((v,))
            rhs_sum^=rhs
        return not acc and rhs_sum==1
    except (TypeError,ValueError,IndexError,AttributeError):
        return False


def cases():
    fs=[]
    for k in (1,2,3,4,5):
        vs=tuple(10**40+31*i for i in range(k))
        n=2**200
        cs=xor.encode_parity(vs,0)+xor.encode_parity(vs,1)
        p=annotate(n,cs,xor.solve(n,cs))
        fs.append((n,cs,(),cs,p,True))
    for q in (4,8):
        n,cs=graphs.tseitin(q,graphs.cubic_graph(q,11),(True,)+(False,)*(q-1))
        n,cs=blind.relabel(n,cs,29)
        fs.append((n,cs,(),cs,annotate(n,cs,xor.solve(n,cs)),True))
    n,cs=rounds.guarded(*graphs.tseitin(4,graphs.cubic_graph(4,11),(True,False,False,False)),2)
    n,cs=blind.relabel(n,cs,29)
    r=rounds.solve(n,cs,2)
    if r["status"]!="UNSAT" or r["certificate"][1]!="XOR":
        raise AssertionError("expected chained XOR")
    bs,final=bridge.annotate(n,cs,r["certificate"][0])
    fs.append((n,cs,bs,final,annotate(n,final,r["certificate"][2]),True))
    # Corruption controls on two opposite width-three parity rows.
    n=3
    cs=xor.encode_parity((1,2,3),0)+xor.encode_parity((1,2,3),1)
    p=annotate(n,cs,xor.solve(n,cs))
    vs,b,refs=p[0]
    bad=(
        (),
        p[:1],
        ((vs,b,refs[:-1]),)+p[1:],
        ((vs,b,((99,refs[0][1]),)+refs[1:]),)+p[1:],
        ((vs,b,((refs[0][0],()),)+refs[1:]),)+p[1:],
        ((vs,1-b,refs),)+p[1:],
        ((vs+(1,2,3),b,refs),)+p[1:],
        p+p,
    )
    fs.extend((n,cs,(),cs,v,False) for v in bad)
    # Stronger-clause evidence is permitted: contradictory units
    # imply both width-two rows when supplemented by the other unit.
    cs=((1,),(-1,))
    refs=tuple(enumerate(cs))
    fs.append((2,cs,(),cs,(((1,2),0,refs),((1,2),1,refs)),True))
    # SAT negative: one valid parity row does not sum to 0=1.
    cs=xor.encode_parity((1,2),0)
    fs.append((2,cs,(),cs,(((1,2),0,tuple(enumerate(cs))),),False))
    return tuple(fs)


def emit_lean():
    fs=cases()
    lines=["","namespace XorFixtures",
           "open ProctorHallDeficiency ProctorExecutableReplay ProctorCapacityReplay ProctorXorReplay"]
    data=bridge._LeanFixtureData(lines)
    for i,(n,cs,bs,final,blocks,expected) in enumerate(fs):
        if bridge.check_shape(n,cs,bs)!=final or check(n,final,blocks)!=expected:
            raise AssertionError("bridge fixture disagreement")
        def block(row):
            vs,rhs,refs=row
            v=data.sequence("List Nat",(bridge._nat(x) for x in vs))
            rr=data.sequence("List RefRow",(
                data.bind("RefRow","⟨"+bridge._nat(j)+","+data.clause(c)+"⟩")
                for j,c in refs))
            return data.bind("ProctorXorReplay.Block","⟨"+v+","+("true" if rhs else "false")+","+rr+"⟩")
        cert=data.sequence("List ProctorXorReplay.Block",(block(b) for b in blocks))
        ff=data.formula(cs)
        bb=data.batches(bs)
        ft=data.formula(final)
        lines.extend((
            f"def f{i} : Formula := "+ff,
            f"def b{i} : List Batch := "+bb,
            f"def t{i} : Formula := "+ft,
            f"def c{i} : List ProctorXorReplay.Block := "+cert,
            f"def ok{i} : Bool := (decide (frontier f{i} b{i} = t{i})) && "
            + f"(checkChainXor f{i} b{i} c{i} == "+("true" if expected else "false")+")",
        ))
    lines.append("end XorFixtures")
    lines.append("def main : IO Unit := do")
    lines.append("  if "+bridge._list(f"XorFixtures.ok{i}" for i in range(len(fs)))+".all id then")
    lines.append(f'    IO.println "F034_XOR_REPLAY_OK cases={len(fs)}"')
    lines.append('  else throw (IO.userError "F034 XOR replay disagreement")')
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    print(emit_lean(),end="")
