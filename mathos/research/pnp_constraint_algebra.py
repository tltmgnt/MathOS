"""Bounded local Boolean relation algebra and proof-producing decisions.

Whole formulas with affine or bijunctive scope relations, and a bounded
one-variable conditioning extension. Not an unrestricted SAT algorithm.
"""
from itertools import combinations, product
from .pnp_structural_kernel import normalize, truth, Exhausted
from .pnp_certificate_routes import propose as binary_propose, verify as binary_verify

ARITY = 4
MODES = ("bijunctive", "affine")
CONDITION_LIMIT = 8


def _groups(f, budget):
    groups = {}
    for clause in f:
        budget.tick(1 + len(clause))
        key = tuple(sorted(abs(x) for x in clause))
        if len(key) > ARITY:
            return None
        groups.setdefault(key, []).append(clause)
    return groups


def _patterns(key, clauses, budget):
    result = []
    for bits in product((False, True), repeat=len(key)):
        budget.tick(1 + len(clauses)*max(1,len(key)))
        a = dict(zip(key, bits))
        if all(any(a[abs(x)] == (x > 0) for x in c) for c in clauses):
            result.append(bits)
    return result


def _xor(bits):
    return sum(bits) % 2


def _compile_local(key, allowed, mode, budget):
    if not allowed:
        return [()] if mode == "bijunctive" else [((), 1)]
    result = []
    if mode == "bijunctive":
        for size in (1, 2):
            for indices in combinations(range(len(key)), size):
                seen = {tuple(bits[i] for i in indices) for bits in allowed}
                for bits in product((False, True), repeat=size):
                    budget.tick(1 + len(allowed))
                    if bits not in seen:
                        result.append(tuple(sorted(-key[i] if bit else key[i]
                                                   for i, bit in zip(indices,bits))))
    else:
        for size in range(1,len(key)+1):
            for indices in combinations(range(len(key)),size):
                budget.tick(1 + len(allowed))
                rhs = {_xor(bits[i] for i in indices) for bits in allowed}
                if len(rhs) == 1:
                    result.append((tuple(key[i] for i in indices), rhs.pop()))
    return result


def _holds(a, constraints, mode):
    if mode == "bijunctive":
        return all(any(a[abs(x)] == (x > 0) for x in c) for c in constraints)
    return all(_xor(a[v] for v in vs) == rhs for vs,rhs in constraints)


def _mask(vs):
    return sum(1 << (v-1) for v in vs)


def _gauss(n, rows, budget):
    # Provenance is a bitset of input rows. This bounds the logical
    # provenance storage, not process RSS.
    budget.cells(max(1, len(rows)) * (min(n,len(rows))+1))
    basis = {}
    for i,(vs,rhs) in enumerate(rows):
        m, b, provenance = _mask(vs), rhs, 1 << i
        budget.tick(1 + len(vs))
        while m:
            p = m.bit_length()-1
            budget.tick()
            if p not in basis:
                basis[p] = (m,b,provenance)
                break
            q,r,t = basis[p]
            m,b,provenance = m^q,b^r,provenance^t
        if not m and b:
            return {"kind":"xor_conflict","rows":[j for j in range(i+1) if provenance >> j & 1]}
    a = 0
    for p,(m,b,_) in sorted(basis.items()):
        budget.tick()
        if ((m&a).bit_count()%2) != b:
            a |= 1<<p
    return {"kind":"sat_witness","assignment":tuple(bool(a>>i&1) for i in range(n))}


def _verify_gauss(n, rows, proof, budget):
    if proof["kind"] == "sat_witness":
        bits = proof["assignment"]
        if len(bits)!=n or any(type(b) is not bool for b in bits):
            raise ValueError("invalid affine witness")
        for vs,rhs in rows:
            budget.tick(1+len(vs))
            if _xor(bits[v-1] for v in vs)!=rhs:
                raise ValueError("affine witness violates row")
        return True
    if proof["kind"] != "xor_conflict":
        raise ValueError("unknown affine proof")
    indices = proof["rows"]
    if (not indices or len(indices)>len(rows) or
            any(type(i) is not int or not 0<=i<len(rows) for i in indices) or
            len(set(indices))!=len(indices)):
        raise ValueError("invalid XOR provenance")
    variables=set()
    rhs=0
    for i in indices:
        vs,b=rows[i]
        budget.tick(1+len(vs))
        variables.symmetric_difference_update(vs)
        rhs ^= b
    if variables or rhs!=1:
        raise ValueError("XOR combination does not derive 0=1")
    return False


def propose(n, clauses, mode, budget):
    if mode not in MODES:
        raise ValueError("unknown algebra")
    nn,f,mapping=normalize(n,clauses)
    groups=_groups(f,budget)
    if groups is None:
        return None
    blocks,combined=[],set()
    for key,group in sorted(groups.items()):
        allowed=_patterns(key,group,budget)
        local=_compile_local(key,allowed,mode,budget)
        expected=set(allowed)
        for bits in product((False,True),repeat=len(key)):
            budget.tick(1+len(local))
            if _holds(dict(zip(key,bits)),local,mode)!=(bits in expected):
                return None
        blocks.append({"scope":key,"constraints":local})
        combined.update(local)
        budget.cells(len(combined))
    constraints=tuple(sorted(combined))
    if mode=="bijunctive":
        if len(constraints)>20_000:
            raise Exhausted("compiled CNF exceeds clause limit")
        proof=binary_propose(nn,constraints,"two_sat",budget)
        if proof is None:
            raise AssertionError("binary compilation rejected")
    else:
        proof=_gauss(nn,constraints,budget)
    sat=proof["kind"]=="sat_witness"
    return {"schema":"mathos-pnp-relation-algebra/1","mode":mode,
            "normalized_n":nn,"new_to_old":mapping,"blocks":blocks,
            "constraints":constraints,"decision_certificate":proof,
            "n":0,"clauses":() if sat else ((),)}


def _parse_local(key, raw, mode):
    if not isinstance(raw,(list,tuple)) or len(raw)>32:
        raise ValueError("invalid local constraint list")
    out=[]
    for c in raw:
        if mode=="bijunctive":
            q=tuple(c)
            if (len(q)>2 or any(type(x) is not int or abs(x) not in key for x in q)
                    or len({abs(x) for x in q})!=len(q) or tuple(sorted(q))!=q):
                raise ValueError("invalid local binary clause")
            out.append(q)
        else:
            vs,rhs=c
            vs=tuple(vs)
            if (type(rhs) is not int or rhs not in (0,1) or
                    any(type(v) is not int or v not in key for v in vs) or
                    tuple(sorted(set(vs)))!=vs):
                raise ValueError("invalid local affine equation")
            out.append((vs,rhs))
    if len(set(out))!=len(out):
        raise ValueError("duplicate local constraint")
    return tuple(out)


def verify(n, clauses, artifact, budget):
    """Independently compare each original scope truth table against the
    certificate's relation and check the assembled decision proof."""
    nn,f,mapping=normalize(n,clauses)
    mode=artifact["mode"]
    if (artifact["schema"]!="mathos-pnp-relation-algebra/1" or mode not in MODES or
            type(artifact["normalized_n"]) is not int or artifact["normalized_n"]!=nn or
            tuple(artifact["new_to_old"])!=mapping):
        raise ValueError("invalid algebra metadata")
    groups=_groups(f,budget)
    if groups is None:
        raise ValueError("scope too wide")
    seen,combined=set(),set()
    for entry in artifact["blocks"]:
        key=tuple(entry["scope"])
        if any(type(v) is not int for v in key) or key in seen or key not in groups:
            raise ValueError("invalid or repeated scope")
        seen.add(key)
        local=_parse_local(key,entry["constraints"],mode)
        for bits in product((False,True),repeat=len(key)):
            budget.tick(1+len(groups[key])*max(1,len(key))+len(local)*max(1,len(key)))
            true_lits={v if b else -v for v,b in zip(key,bits)}
            source=all(not true_lits.isdisjoint(c) for c in groups[key])
            if mode=="bijunctive":
                target=all(not true_lits.isdisjoint(c) for c in local)
            else:
                target=all(len(true_lits.intersection(vs))%2==rhs for vs,rhs in local)
            if source!=target:
                raise ValueError("local equivalence rejected")
        combined.update(local)
        budget.cells(len(combined))
    if seen!=set(groups):
        raise ValueError("missing scope")
    expected=tuple(sorted(combined))
    raw=artifact["constraints"]
    if mode=="bijunctive":
        actual=tuple(tuple(c) for c in raw)
    else:
        actual=tuple((tuple(vs),rhs) for vs,rhs in raw)
    if actual!=expected:
        raise ValueError("assembled algebra mismatch")
    proof=artifact["decision_certificate"]
    if mode=="bijunctive":
        if proof["route"]!="two_sat":
            raise ValueError("incorrect binary proof route")
        binary_verify(nn,expected,proof,budget)
        sat=proof["kind"]=="sat_witness"
        if sat:
            _,_,active=normalize(nn,expected)
            model=dict(zip(active,proof["assignment"]))
            a=tuple(model.get(v,False) for v in range(1,nn+1))
    else:
        sat=_verify_gauss(nn,expected,proof,budget)
        if sat:
            a=proof["assignment"]
    if sat:
        budget.tick(1+len(f)+sum(map(len,f)))
        if not truth(f,a):
            raise ValueError("original CNF rejects lifted model")
    if (type(artifact["n"]) is not int or artifact["n"]!=0 or
            tuple(tuple(c) for c in artifact["clauses"])!=( () if sat else ((),) )):
        raise ValueError("constant decision mismatch")
    return True


def _direct(n,f,budget):
    for mode in MODES:
        a=propose(n,f,mode,budget)
        if a is not None:
            verify(n,f,a,budget)
            return a
    return None


def _restrict(f,v,b,budget):
    literal=v if b else -v
    out=[]
    for c in f:
        budget.tick(1+len(c))
        if literal not in c:
            out.append(tuple(x for x in c if x!=-literal))
    return tuple(out)


def solve(n,clauses,budget,*,condition_limit=CONDITION_LIMIT):
    """Try homogeneous modes, then up to eight single-variable splits.

    SAT requires a certified SAT branch; UNSAT requires both certified
    UNSAT branches of the SAME split. Unknown is not a decision.
    """
    if type(condition_limit) is not int or not 0<=condition_limit<=CONDITION_LIMIT:
        raise ValueError("invalid conditioning limit")
    nn,f,mapping=normalize(n,clauses)
    direct=_direct(nn,f,budget)
    if direct is not None:
        result={"kind":"direct","proof":direct,"n":0,"clauses":direct["clauses"]}
    else:
        counts={v:0 for v in range(1,nn+1)}
        for c in f:
            budget.tick(1+len(c))
            for x in c:
                counts[abs(x)]+=1
        result=None
        for v in sorted(counts,key=lambda x:(-counts[x],x))[:condition_limit]:
            branches=[]
            for b in (False,True):
                residual=_restrict(f,v,b,budget)
                proof=_direct(nn,residual,budget)
                if proof is None:
                    continue
                entry={"value":b,"proof":proof}
                if not proof["clauses"]:
                    result={"kind":"conditioned","variable":v,"branches":[entry],"n":0,"clauses":()}
                    break
                branches.append(entry)
            if result is not None:
                break
            if len(branches)==2:
                result={"kind":"conditioned","variable":v,"branches":branches,"n":0,"clauses":((),)}
                break
    if result is None:
        return None
    result["schema"]="mathos-pnp-mixed-algebra/1"
    verify_solution(n,clauses,result,budget)
    return result


def verify_solution(n,clauses,artifact,budget):
    nn,f,_=normalize(n,clauses)
    if artifact["schema"]!="mathos-pnp-mixed-algebra/1":
        raise ValueError("unknown mixed certificate schema")
    if artifact["kind"]=="direct":
        proof=artifact["proof"]
        verify(nn,f,proof,budget)
        sat=not proof["clauses"]
    elif artifact["kind"]=="conditioned":
        v=artifact["variable"]
        if type(v) is not int or not 1<=v<=nn:
            raise ValueError("invalid split variable")
        seen=set()
        sat=False
        branches=artifact["branches"]
        if not 1<=len(branches)<=2:
            raise ValueError("invalid branch count")
        for entry in branches:
            b=entry["value"]
            if type(b) is not bool or b in seen:
                raise ValueError("invalid branch value")
            seen.add(b)
            # Replay substitution directly as a truth restriction.
            residual=[]
            for c in f:
                budget.tick(1+len(c))
                fixed=[x for x in c if abs(x)==v]
                if any((x>0)==b for x in fixed):
                    continue
                residual.append(tuple(x for x in c if abs(x)!=v))
            proof=entry["proof"]
            verify(nn,residual,proof,budget)
            sat=sat or not proof["clauses"]
        if not sat and seen!={False,True}:
            raise ValueError("UNSAT requires both branches")
    else:
        raise ValueError("unknown mixed proof kind")
    if (type(artifact["n"]) is not int or artifact["n"]!=0 or
            tuple(tuple(c) for c in artifact["clauses"])!=( () if sat else ((),) )):
        raise ValueError("mixed decision mismatch")
    return True
