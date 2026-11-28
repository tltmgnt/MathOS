"""Theorem S: exact static degree on implication chains via reversible pebbling.

Classical pebbling/Nullstellensatz correspondence, specialized to R's
Boolean quotient convention. Bounded BFS controls, not general SAT hardness.
"""
from collections import deque
from math import comb
import json

def chain(n):
    """Source x1=1, implications xi -> x(i+1), sink xn=0.

    Fixed endpoint coordinates belong to the affine coupling; the unary
    constraints themselves remain local, so all n variables are free.
    """
    if type(n) is not int or n<1:
        raise ValueError("positive chain length required")
    ds=[(10,15)]*(n+1)
    rows=[(2,1)]
    prev=0
    for i in range(1,n):
        rows.append(((1<<prev)|(2<<(2*i)),0))
        prev=2*i
    rows.extend([(1<<(2*n),0),((1<<prev)|(2<<(2*n)),0)])
    return ds,rows

def neighbors(n,d,s):
    for j in range(n):
        if j and not s&(1<<(j-1)):
            continue
        v=s^(1<<j)
        if v.bit_count()<=d:
            yield v

def search(n,d):
    if type(n) is not int or type(d) is not int or not 1<=n<=63 or not 0<=d<=n:
        raise ValueError("invalid finite pebbling parameters")
    if sum(comb(n,i) for i in range(d+1))>300000:
        raise ValueError("configuration budget exceeded")
    target=1<<(n-1)
    pred={0:None}
    todo=deque([0])
    while todo:
        s=todo.popleft()
        if s&target:
            path=[]
            while s is not None:
                path.append(s)
                s=pred[s]
            return {"kind":"path","degree":d,"configurations":path[::-1]}
        for v in neighbors(n,d,s):
            if v not in pred:
                pred[v]=s
                todo.append(v)
    return {"kind":"closed","degree":d,"configurations":sorted(pred)}

def check_chain_certificate(n,cert):
    """Independent move/closure checking; no BFS or algebraic solver call."""
    try:
        if type(n) is not int or not 1<=n<=63 or not isinstance(cert,dict):
            return False
        if set(cert)!={"kind","degree","configurations"}:
            return False
        d,ss=cert["degree"],cert["configurations"]
        if type(d) is not int or not 0<=d<=n or not isinstance(ss,list) or not ss or len(ss)>300000:
            return False
        if any(type(s) is not int or not 0<=s<1<<n or s.bit_count()>d for s in ss):
            return False
        if ss[0]!=0 or len(set(ss))!=len(ss):
            return False
        target=1<<(n-1)
        if cert["kind"]=="path":
            if not ss[-1]&target:
                return False
            for a,b in zip(ss,ss[1:]):
                change=a^b
                if change==0 or change&(change-1):
                    return False
                j=change.bit_length()-1
                if j and not a&(1<<(j-1)):
                    return False
            return True
        if cert["kind"]!="closed" or any(s&target for s in ss):
            return False
        seen=set(ss)
        for s in ss:
            for j in range(n):
                v=s^(1<<j)
                if v.bit_count()<=d and (j==0 or s&(1<<(j-1))) and v not in seen:
                    return False
        return True
    except (TypeError,ValueError,KeyError,IndexError,OverflowError):
        return False

def exact(n):
    """Finite two-sided certificates at the classical line-pebbling threshold."""
    if type(n) is not int or not 1<=n<=63:
        raise ValueError("invalid finite chain length")
    d=n.bit_length()
    lower=search(n,d-1)
    upper=search(n,d)
    if lower["kind"]!="closed" or upper["kind"]!="path":
        raise AssertionError("line pebbling theorem mismatch")
    return {"minimum":d,"lower":lower,"upper":upper}

def check_exact(n,cert):
    try:
        if not isinstance(cert,dict) or set(cert)!={"minimum","lower","upper"}:
            return False
        d=cert["minimum"]
        return (type(d) is int and d>=1 and cert["lower"]["kind"]=="closed"
                and cert["upper"]["kind"]=="path" and cert["lower"]["degree"]==d-1
                and cert["upper"]["degree"]==d
                and check_chain_certificate(n,cert["lower"])
                and check_chain_certificate(n,cert["upper"]))
    except (TypeError,KeyError):
        return False

def identity_terms(n,path):
    """Translate a legal path to R's monomial multiples in original x-coordinates.

    Tags are [block, forbidden output, multiplier mask].  Source forbidden
    output is 2, sink forbidden output is 2, internal forbidden output is 2.
    The final sink multiple eliminates the final monomial.
    """
    if not isinstance(path,dict) or path.get("kind")!="path" or not check_chain_certificate(n,path):
        raise ValueError("valid path certificate required")
    ss=path["configurations"]
    terms=set()
    for a,b in zip(ss,ss[1:]):
        j=(a^b).bit_length()-1
        smaller=a&b
        m=smaller if j==0 else smaller^(1<<(j-1))
        term=(j,2,m)
        if term in terms:
            terms.remove(term)
        else:
            terms.add(term)
    terms.symmetric_difference_update({(n,2,ss[-1]^(1<<(n-1)))})
    return [list(t) for t in sorted(terms)]

def original_frame(n):
    dirs=[0]*n
    dirs[0]|=1
    for i in range(1,n):
        dirs[i-1]|=2<<(2*i)
        dirs[i]|=1<<(2*i)
    dirs[n-1]|=2<<(2*n)
    return 2,dirs

def evidence():
    from mathos.research.pnp_overlap_degree import check_degree
    cases=[]
    for n in (1,3,7,15,31):
        cert=exact(n)
        assert check_exact(n,cert)
        ds,rs=chain(n)
        a,dirs=original_frame(n)
        proof={"kind":"refutation","anchor":a,"directions":dirs,
               "degree":cert["minimum"],"terms":identity_terms(n,cert["upper"])}
        # R's generic matrix budget need not cover the larger chain.
        cross_checked=n<=15
        if cross_checked:
            assert check_degree(ds,rs,proof)
        cases.append({"variables":n,"blocks":n+1,"minimum_static_degree":cert["minimum"],
                      "lower_configurations":len(cert["lower"]["configurations"]),
                      "upper_moves":len(cert["upper"]["configurations"])-1,
                      "identity_terms":len(proof["terms"]),"checker_accepted":True,
                      "generic_checker_accepted":True if cross_checked else None,
                      "certificate":cert})
    return {"scope":"classical reversible line pebbling transferred to R, no general SAT hardness",
            "cases":cases,"formula":"ceil(log2(n+1))","dynamic_degree_upper":2}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
