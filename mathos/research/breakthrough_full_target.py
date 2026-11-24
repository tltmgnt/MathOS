"""Exact AND/affine SAT decision, with an explicit exponential rank parameter."""
from itertools import product
import json

def affine(n, rows):
    """Return particular solution and homogeneous basis, or None."""
    piv={}
    for mask,rhs in rows:
        if not isinstance(mask,int) or not 0<=mask<1<<n or rhs not in (0,1):
            raise ValueError("invalid equation")
        while mask:
            p=mask.bit_length()-1
            if p not in piv:
                piv[p]=(mask,rhs); break
            a,b=piv[p]; mask^=a; rhs^=b
        if mask==0 and rhs: return None
    def lift(free,homogeneous):
        x=free
        for p,(a,b) in sorted(piv.items()):
            if (a&x).bit_count()%2 != (0 if homogeneous else b): x|=1<<p
        return x
    return lift(0,False),[lift(1<<i,True) for i in range(n) if i not in piv]

def solve(n, rows, gates):
    """All variables may overlap. Gate (a,b,y) means y=a AND b."""
    rows=list(rows);gates=list(gates)
    if n<0 or any(not all(isinstance(i,int) and 0<=i<n for i in g) or len(g)!=3 for g in gates):
        raise ValueError("invalid gate")
    base=affine(n,rows)
    if base is None:return {"sat":False,"rank":None,"branches":0}
    x,basis=base
    mask=sum(1<<i for i in set(a for a,b,y in gates))
    proj={}
    for v in basis:
        v&=mask
        while v:
            p=v.bit_length()-1
            if p not in proj:
                proj[p]=v;break
            v^=proj[p]
    directions=list(proj.values());r=len(directions)
    count=0
    for bits in range(1<<r):
        z=x&mask
        for i,v in enumerate(directions):
            if bits>>i&1:z^=v
        eq=rows+[(1<<a,z>>a&1) for a in sorted({g[0] for g in gates})]
        for a,b,y in gates:
            eq.append(((1<<y)^((1<<b) if z>>a&1 else 0),0))
        count+=1
        ans=affine(n,eq)
        if ans is not None:
            w=ans[0]
            assert verify(w,rows,gates)
            return {"sat":True,"witness":w,"rank":r,"branches":count}
    return {"sat":False,"rank":r,"branches":count}

def verify(w,rows,gates):
    return all((a&w).bit_count()%2==b for a,b in rows) and all(
        (w>>y&1)==((w>>a&1)&(w>>b&1)) for a,b,y in gates)

def encode_3cnf(n,clauses):
    """Three fresh negated literal variables and two AND outputs per clause."""
    rows=[];gates=[];k=n
    for clause in clauses:
        if len(clause)!=3 or any(not 1<=abs(l)<=n for l in clause):
            raise ValueError("expected three valid literals")
        a,b,c,y,z=range(k,k+5);k+=5
        for v,l in zip((a,b,c),clause):
            rows.append(((1<<v)^(1<<(abs(l)-1)),int(l>0)))
        gates.extend([(a,b,y),(y,c,z)])
        rows.append((1<<z,0))
    return k,rows,gates

def replay():
    cases=0;sat=0
    clauses=list(product((-1,1,-2,2),repeat=3))
    # All 64 single clauses plus 64 deterministic two-clause combinations.
    for i,c in enumerate(clauses):
        for cs in ([c],[c,clauses[(i*17+7)%len(clauses)]]):
            n,rows,gates=encode_3cnf(2,cs)
            expected=any(all(any(bool(w>>(abs(l)-1)&1)==(l>0) for l in cl) for cl in cs) for w in range(4))
            result=solve(n,rows,gates)
            assert result["sat"]==expected
            if expected:assert verify(result["witness"],rows,gates)
            cases+=1;sat+=expected
    # Encode all eight falsifying triples on three variables: unsatisfiable.
    n,rows,gates=encode_3cnf(3,list(product((1,-1),(2,-2),(3,-3))))
    assert not solve(n,rows,gates)["sat"]
    # Every left operand is independent under the affine constraints, but
    # a_i AND (1+a_i)=1 is impossible. This implementation enumerates all.
    bad=[]
    for k in (1,2,4,8,12):
        rows=[];gates=[]
        for i in range(k):
            a,b,y=3*i,3*i+1,3*i+2
            rows.extend([((1<<a)^(1<<b),1),(1<<y,1)])
            gates.append((a,b,y))
        result=solve(3*k,rows,gates)
        assert result=={"sat":False,"rank":k,"branches":1<<k}
        bad.append({"gates":k,"rank":k,"branches":result["branches"]})
    # Independent arbitrary overlap cases with repeated gate variables.
    count=0
    for g in product(range(3),repeat=3):
        for h in product(range(3),repeat=3):
            for rhs in (0,1):
                rows=[(7,rhs)]
                got=solve(3,rows,[g,h])
                assert got["sat"]==any(verify(w,rows,[g,h]) for w in range(8))
                count+=1
    return {"status":"FULL_TARGET_NOT_SOLVED","promotion":"NONE",
            "three_cnf_controls":cases+1,"satisfiable_controls":sat,
            "overlap_controls":count,"adversarial_rank_cases":bad,
            "unrestricted_decision_correctness_argument":True,
            "unrestricted_polynomial_runtime_proved":False,
            "all_prime_sha_finiteness_proved":False}

if __name__=="__main__":print(json.dumps(replay(),indent=2))
