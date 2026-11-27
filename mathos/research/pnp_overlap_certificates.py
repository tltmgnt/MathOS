"""PNP-OVL-001 G: explicit proof-carrying rank compression.

The checker does not invoke the solver, optimizer or certificate generator.
It independently reconstructs the local relations and checks rank, proof
coverage, witnesses and row-sum contradictions. No succinctness claim.
"""
from itertools import product
import json
from mathos.research.pnp_overlap_boundary import (
    project, affine_rows, affine_solve, independent_forms, minimum_rank_forms)

def parity(mask, value):
    return (mask & value).bit_count() % 2

def _dual(rows):
    """Return indices of a row sum equal to (0,1), or None."""
    pivots={}
    for i,(m,b) in enumerate(rows):
        w=1<<i
        while m:
            p=m.bit_length()-1
            if p not in pivots:
                pivots[p]=(m,b,w)
                break
            a,c,v=pivots[p]
            m,b,w=m^a,b^c,w^v
        if not m and b:
            return [j for j in range(i+1) if (w>>j)&1]
    return None

def _lower_tree(width, fixed, groups, budget):
    """Preorder uncovered-group indices for exhaustive budget refutation."""
    if budget<0:
        return []
    proof=[]
    stack=[(tuple(),0)]
    while stack:
        added,depth=stack.pop()
        rows=fixed+[(m,0) for m in added]
        group=next((i for i,g in enumerate(groups)
                    if all(independent_forms(width,rows,[m]) for m in g)),None)
        if group is None:
            raise AssertionError("claimed rank lower bound is false")
        proof.append(group)
        if depth<budget:
            for m in reversed(groups[group]):
                stack.append((added+(m,),depth+1))
    return proof

def _branch(fixed, triples, relations, forms, basis, bits, rep):
    rows=fixed+list(zip(basis,bits))
    for i,form in zip(triples,forms):
        local=form>>(2*i)
        sliced={v for v in relations[i] if parity(local,v)==parity(form,rep)}
        rows.extend((m<<(2*i),b) for m,b in affine_rows(sliced))
    return rows

def certify(domains, rows):
    """Generate a SAT witness or explicit UNSAT proof with optimal-rank proof.

    If the affine relaxation itself is inconsistent, no rank claim is made.
    Proof objects are materialized; their space may be exponential.
    """
    ds,rows=tuple(domains),list(rows)
    width=2*len(ds)
    relations=[project(*d) for d in ds]
    if any(not r for r in relations):
        return {"kind":"empty","index":next(i for i,r in enumerate(relations) if not r)}
    fixed=rows+[(m<<(2*i),b) for i,r in enumerate(relations) if len(r)!=3
                for m,b in affine_rows(r)]
    if affine_solve(width,fixed) is None:
        return {"kind":"affine_unsat","dual":_dual(fixed)}
    triples=[i for i,r in enumerate(relations) if len(r)==3]
    groups=[tuple(m<<(2*i) for m in (1,2,3)) for i in triples]
    opt=minimum_rank_forms(width,fixed,groups)
    forms=list(opt["forms"])
    basis=list(independent_forms(width,fixed,forms))
    d=len(basis)
    cert={"kind":"ranked_unsat","forms":forms,"basis":basis,"d":d,
          "lower":_lower_tree(width,fixed,groups,d-1),"leaves":[]}
    for bits in product(range(2),repeat=d):
        rep=affine_solve(width,fixed+list(zip(basis,bits)))
        if rep is None:
            raise AssertionError("basis is not independent")
        branch=_branch(fixed,triples,relations,forms,basis,bits,rep)
        ans=affine_solve(width,branch)
        if ans is not None:
            cert["kind"]="sat"
            del cert["leaves"]
            cert["witness"]=[list(r[(ans>>(2*i))&3]) for i,r in enumerate(relations)]
            return cert
        dual=_dual(branch)
        if dual is None:
            raise AssertionError("missing contradiction")
        cert["leaves"].append({"rep":rep,"dual":dual})
    return cert

# Checker implementation: independent low-column Gaussian elimination, direct
# enumeration of local domains and constraints; no calls to solver routines.
def _rank(width, masks):
    work=list(masks)
    n=0
    for j in range(width):
        pivot=next((i for i in range(n,len(work)) if (work[i]>>j)&1),None)
        if pivot is None:
            continue
        work[n],work[pivot]=work[pivot],work[n]
        for i in range(n+1,len(work)):
            if (work[i]>>j)&1:
                work[i]^=work[n]
        n+=1
    return n

def _relation(d):
    a,b=d
    return {int(x and y)+2*int(x and z)
            for x,y,z in product((0,1),repeat=3)
            if ((a>>(2*x+y))&1) and ((b>>(2*x+z))&1)}

def _rows(r):
    if not r:
        return [(0,1)]
    if len(r)==3:
        raise ValueError("non-affine relation")
    return [(m,b) for m in (1,2,3) for b in (0,1)
            if all(parity(m,v)==b for v in r)]

def _dual_ok(rows, indices):
    if not isinstance(indices,list) or not indices or any(
            type(i) is not int or not 0<=i<len(rows) for i in indices):
        return False
    if len(indices)!=len(set(indices)):
        return False
    mask=rhs=0
    for i in indices:
        m,b=rows[i]
        mask^=m
        rhs^=b
    return (mask,rhs)==(0,1)

def _lower_ok(width, fixed, groups, budget, proof):
    if not isinstance(proof,list):
        return False
    if budget<0:
        return not proof
    base=tuple(m for m,b in fixed)
    stack=[(base,0)]
    pos=0
    while stack:
        space,depth=stack.pop()
        if pos==len(proof):
            return False
        index=proof[pos]
        pos+=1
        if type(index) is not int or not 0<=index<len(groups):
            return False
        group=groups[index]
        rank=_rank(width,space)
        if any(_rank(width,space+(m,))!=rank+1 for m in group):
            return False
        if depth<budget:
            for m in reversed(group):
                stack.append((space+(m,),depth+1))
    return pos==len(proof)

def _witness_ok(ds,rows,w):
    if not isinstance(w,list) or len(w)!=len(ds):
        return False
    value=0
    for i,((a,b),t) in enumerate(zip(ds,w)):
        if not isinstance(t,list) or len(t)!=3 or any(type(x) is not int or x not in (0,1) for x in t):
            return False
        x,y,z=t
        if not ((a>>(2*x+y))&1 and (b>>(2*x+z))&1):
            return False
        value|=((x&y)+2*(x&z))<<(2*i)
    return all(parity(m,value)==b for m,b in rows)

def check(domains, rows, cert):
    """Fail closed for malformed proof content. Input is supplied separately."""
    try:
        ds,rows=tuple(tuple(d) for d in domains),list(tuple(r) for r in rows)
        width=2*len(ds)
        if any(len(d)!=2 or any(type(v) is not int or not 0<=v<16 for v in d) for d in ds):
            return False
        if any(len(r)!=2 or type(r[0]) is not int or not 0<=r[0]<(1<<width)
               or type(r[1]) is not int or r[1] not in (0,1) for r in rows):
            return False
        if not isinstance(cert,dict):
            return False
        relations=[_relation(d) for d in ds]
        kind=cert.get("kind")
        if kind=="empty":
            i=cert.get("index")
            return set(cert)=={"kind","index"} and type(i) is int and 0<=i<len(ds) and not relations[i]
        if any(not r for r in relations):
            return False
        fixed=rows+[(m<<(2*i),b) for i,r in enumerate(relations) if len(r)!=3
                    for m,b in _rows(r)]
        if kind=="affine_unsat":
            return set(cert)=={"kind","dual"} and _dual_ok(fixed,cert.get("dual"))
        if kind not in ("sat","ranked_unsat"):
            return False
        if set(cert)!={"kind","forms","basis","d","lower",
                       "witness" if kind=="sat" else "leaves"}:
            return False
        triples=[i for i,r in enumerate(relations) if len(r)==3]
        groups=[tuple(m<<(2*i) for m in (1,2,3)) for i in triples]
        forms,basis,d=cert["forms"],cert["basis"],cert["d"]
        if type(d) is not int or not 0<=d<=len(groups):
            return False
        if not isinstance(forms,list) or len(forms)!=len(groups) or any(
                type(m) is not int or m not in g for m,g in zip(forms,groups)):
            return False
        if not isinstance(basis,list) or len(basis)!=d or any(
                type(m) is not int or m not in forms for m in basis):
            return False
        masks=[m for m,b in fixed]
        r0=_rank(width,masks)
        if _rank(width,masks+basis)!=r0+d or _rank(width,masks+forms)!=r0+d:
            return False
        if not _lower_ok(width,fixed,groups,d-1,cert["lower"]):
            return False
        if kind=="sat":
            return _witness_ok(ds,rows,cert["witness"])
        leaves=cert["leaves"]
        if not isinstance(leaves,list) or len(leaves)!=(1<<d):
            return False
        for bits,leaf in zip(product(range(2),repeat=d),leaves):
            if not isinstance(leaf,dict) or set(leaf)!={"rep","dual"}:
                return False
            rep=leaf["rep"]
            branch=fixed+list(zip(basis,bits))
            if type(rep) is not int or not 0<=rep<(1<<width) or any(
                    parity(m,rep)!=b for m,b in branch):
                return False
            for i,form in zip(triples,forms):
                local=form>>(2*i)
                sliced={v for v in relations[i] if parity(local,v)==parity(form,rep)}
                branch.extend((m<<(2*i),b) for m,b in _rows(sliced))
            if not _dual_ok(branch,leaf["dual"]):
                return False
        return True
    except (TypeError, ValueError, KeyError, IndexError, OverflowError):
        return False

def contradiction_demo():
    """Four translates of an implication forbid all four common output pairs."""
    ds=[(10,15)]*4
    rows=[((1<<(2*i))|1,i&1) for i in range(1,4)]
    rows += [((2<<(2*i))|2,i>>1) for i in range(1,4)]
    return ds,rows

def evidence():
    from mathos.research.pnp_overlap_boundary import parity_gap_instance
    out={}
    for name,instance in (("parity_21",parity_gap_instance(21)),
                          ("four_translate_unsat",contradiction_demo())):
        ds,rows=instance
        cert=certify(ds,rows)
        assert check(ds,rows,cert)
        out[name]={"kind":cert["kind"],"d":cert["d"],
                   "lower_nodes":len(cert["lower"]),
                   "contradiction_leaves":len(cert.get("leaves",[])),
                   "json_bytes":len(json.dumps(cert,separators=(",",":")).encode()),
                   "checker_accepted":True,"certificate":cert}
    return {"scope":"structured controls; no novelty or global promotion","cases":out}

if __name__=="__main__":
    print(json.dumps(evidence(),indent=2,sort_keys=True))
