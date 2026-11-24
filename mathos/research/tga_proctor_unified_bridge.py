"""F034 unified typed certificate dispatch and input-binding controls.

The Python mirror is only a differential test oracle. The Lean theorem
concerns independently supplied typed expected data, not DIMACS bytes.
"""
from . import tga_proctor_capacity_bridge as capacity
from . import tga_proctor_xor_bridge as xor
from . import tga_proctor_replay_bridge as replay
from . import tga_proctor_mixed_routing as mixed


def _valid(n,v):
    return type(v) is int and 1<=v<=n


def _row(n,c):
    return all(type(l) is int and _valid(n,abs(l)) for l in c)


def _refs(n,rs):
    return all(_row(n,c) for _,c in rs)


def check(n,expected,envelope):
    """Mirror exact typed binding; no discovery or SAT promotion."""
    try:
        declared,original,proof=envelope
        batches,augmented,tag,payload=proof
        if (type(n) is not int or n<0 or type(declared) is not int
                or n!=declared or expected!=original or type(augmented) is not bool
                or not all(_row(n,c) for c in expected)):
            return False
        if not all(_valid(n,p) and _row(n,t) for batch in batches for _,_,p,t in batch):
            return False
        target=replay.check_shape(n,expected,batches)
        if target is None:
            return False
        if augmented:
            target=expected+target
        if tag=="EMPTY":
            return payload is None and () in target
        if tag=="CAPACITY":
            ds,gs,rs=payload
            return (_refs(n,ds) and _refs(n,rs) and all(_row(n,vs) for vs,_ in gs)
                    and capacity.check(n,target,payload))
        if tag=="XOR":
            return (all(all(_valid(n,v) for v in vs) and _refs(n,rs) for vs,_,rs in payload)
                    and xor.check(n,target,payload))
        return False
    except (TypeError,ValueError,IndexError,AttributeError,KeyError):
        return False


def cases():
    out=[]
    def add(n,f,bs,aug,tag,p,ok):
        out.append((n,f,(n,f,(bs,aug,tag,p)),ok))

    for n,cs,bs,final,p,ok in capacity.cases():
        add(n,cs,bs,False,"CAPACITY",p,ok)
    for n,cs,bs,final,p,ok in xor.cases():
        add(n,cs,bs,False,"XOR",p,ok)

    add(0,((),),(),False,"EMPTY",None,True)
    add(1,((1,),),(),False,"EMPTY",None,False)
    cs=((1,2),(1,-2),(-1,2),(-1,-2))
    a=mixed.derive(2,cs)
    b=mixed.derive(2,a["clauses"])
    bs,final=replay.annotate(2,cs,(a["steps"],b["steps"]))
    add(2,cs,bs,False,"EMPTY",None,True)

    # Actual augmented-only mixed proof: derived unit and original unit.
    cs=((1,2),(1,-2),(-1,))
    r=mixed.solve(2,cs,0,0)
    if r["route"]!="MIXED":
        raise AssertionError("expected mixed proof")
    steps,scope,tag,p=r["proof"]
    if scope!="AUGMENTED" or tag!="XOR":
        raise AssertionError("expected augmented XOR")
    bs,final=replay.annotate(2,cs,(steps,))
    blocks=xor.annotate(2,cs+final,p)
    add(2,cs,bs,True,"XOR",blocks,True)
    add(2,cs,bs,False,"XOR",blocks,False)

    # A valid proof for a different input must not certify this request.
    n,original,env,_=out[0]
    bound,claimed,proof=env
    out.extend((
        (n,(),env,False),
        (n,original[:-1],env,False),
        (n,tuple(reversed(original)),env,False),
        (n,original+(original[0],),env,False),
        (n+1,original,env,False),
        (n,original,(bound,(),proof),False),
        (n,original,(bound+1,claimed,proof),False),
    ))
    # These are representable typed data but invalid declared ranges.
    add(0,((1,),()),(),False,"EMPTY",None,False)
    add(1,((0,),()),(),False,"EMPTY",None,False)
    add(1,((1,),(-1,)),(((0,1,2,(1,-1)),),),False,"EMPTY",None,False)
    add(1,((1,),(-1,)),(((0,1,1,(2,)),),),True,"XOR",(),False)
    # Isolate range rejection: even with an empty original clause and
    # sound weakening, a fresh out-of-range proof label is refused.
    add(1,((),),(((0,0,1,(2,)),),),True,"EMPTY",None,False)
    add(1,((),),(((0,0,2,()),),),True,"EMPTY",None,False)
    return tuple(out)


def emit_lean():
    fs=cases()
    lines=["","namespace UnifiedFixtures",
           "open ProctorHallDeficiency ProctorExecutableReplay ProctorCapacityReplay ProctorUnifiedReplay"]
    data=replay._LeanFixtureData(lines)

    def refs(rs):
        return data.sequence("List RefRow",(
            data.bind("RefRow","⟨"+replay._nat(j)+","+data.clause(c)+"⟩") for j,c in rs))

    def terminal(tag,p):
        if tag=="EMPTY":
            return "Terminal.empty"
        if tag=="CAPACITY":
            ds,gs,rs=p
            groups=data.sequence("List ProctorCapacityDeficiency.Group",(
                data.bind("ProctorCapacityDeficiency.Group","⟨"+data.clause(vs)+","+replay._nat(c)+"⟩")
                for vs,c in gs))
            return "Terminal.capacity "+data.bind("ProctorCapacityReplay.Certificate",
                "⟨"+refs(ds)+","+groups+","+refs(rs)+"⟩")
        if tag=="XOR":
            def block(b):
                vs,rhs,rs=b
                v=data.sequence("List Nat",(replay._nat(x) for x in vs))
                return data.bind("ProctorXorReplay.Block",
                    "⟨"+v+","+("true" if rhs else "false")+","+refs(rs)+"⟩")
            return "Terminal.xor "+data.sequence("List ProctorXorReplay.Block",(block(b) for b in p))
        raise ValueError("unknown terminal")

    for i,(n,f,env,ok) in enumerate(fs):
        if check(n,f,env)!=ok:
            raise AssertionError("fixture mismatch "+str(i))
        bound,original,(bs,aug,tag,p)=env
        ff=data.formula(f)
        orig=data.formula(original)
        bb=data.batches(bs)
        tt=data.bind("Terminal",terminal(tag,p))
        pp=data.bind("Proof","⟨"+bb+","+("true" if aug else "false")+","+tt+"⟩")
        ee=data.bind("Envelope","⟨"+replay._nat(bound)+","+orig+","+pp+"⟩")
        lines.append(f"def ok{i} : Bool := boundCheck {replay._nat(n)} {ff} {ee} == "+
                     ("true" if ok else "false"))
    lines.extend(("end UnifiedFixtures","def main : IO Unit := do",
                  "  if "+replay._list(f"UnifiedFixtures.ok{i}" for i in range(len(fs)))+".all id then",
                  f'    IO.println "F034_UNIFIED_REPLAY_OK cases={len(fs)}"',
                  '  else throw (IO.userError "F034 unified replay disagreement")'))
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    print(emit_lean(),end="")
