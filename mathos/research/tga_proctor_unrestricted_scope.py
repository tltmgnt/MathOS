"""F024: exact signed 3-CNF compiler and parameterized affine branching.

This is not a polynomial-time unrestricted SAT algorithm. The F014 mirror
solves each conditional affine system; the number of branches can be 2**k.
"""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Compiled:
    original: int
    width: int
    # Sparse affine rows: XOR of the listed coordinates equals rhs.
    rows: tuple
    # Nonlinear relations: output = left AND right.
    gates: tuple


def compile_cnf(n, clauses):
    """Signed, one-based literal IDs; exactly three literals per clause."""
    if type(n) is not int or n < 0:
        raise ValueError("invalid variable count")
    clauses = tuple(tuple(c) for c in clauses)
    if any(len(c) != 3 or any(type(l) is not int or not 1 <= abs(l) <= n
                             for l in c) for c in clauses):
        raise ValueError("invalid 3-CNF")
    # First n variables are original, next n are complements.
    rows = [((i, n+i), True) for i in range(n)]
    gates = []
    def neg_literal(l):
        return n+l-1 if l > 0 else -l-1
    for j, clause in enumerate(clauses):
        a, b, c = map(neg_literal, clause)
        t, z = 2*n+2*j, 2*n+2*j+1
        gates.extend(((a,b,t), (t,c,z)))
        rows.append(((z,), False))
    return Compiled(n, 2*n+2*len(clauses), tuple(rows), tuple(gates))


def evaluate(cnf, x):
    return all(any(bool(x[abs(l)-1]) == (l > 0) for l in c) for c in cnf)


def verify_compiled(p, x):
    return (len(x) == p.width and all(v in (0,1) for v in x)
            and all(sum(x[i] for i in ix)%2 == b for ix,b in p.rows)
            and all(x[z] == (x[a] and x[b]) for a,b,z in p.gates))


def extend(p, x):
    if len(x) != p.original or any(v not in (0,1) for v in x):
        raise ValueError("invalid assignment")
    x = list(map(bool,x))
    x += [not b for b in x]
    for a,b,z in p.gates:
        assert z == len(x)
        x.append(x[a] and x[b])
    return tuple(x)


def backdoor(p):
    """Fix one input of every AND gate, using a deterministic ordering."""
    return tuple(sorted({a for a,_,_ in p.gates}))


def branch_rows(p, values):
    """All gates become affine when their first input has been fixed."""
    keys = backdoor(p)
    if len(values) != len(keys) or any(v not in (0,1) for v in values):
        raise ValueError("invalid branch")
    fixed = dict(zip(keys, values))
    sparse = list(p.rows) + [((i,), v) for i,v in zip(keys,values)]
    for a,b,z in p.gates:
        sparse.append(((z,b), False) if fixed[a] else ((z,), False))
    dense = []
    for ix,rhs in sparse:
        row = [False]*p.width
        for i in ix:
            row[i] = not row[i]
        dense.append((tuple(row),bool(rhs)))
    return tuple(dense)


def dual_valid(rows, weights, width):
    if len(weights) != len(rows) or any(v not in (0,1) for v in weights):
        return False
    acc = [False]*width
    rhs = False
    for (a,b),w in zip(rows,weights):
        if w:
            acc = [x^y for x,y in zip(acc,a)]
            rhs ^= b
    return rhs and not any(acc)


def solve(n, clauses):
    """Experimental exact solver. UNSAT certificate lists every branch dual."""
    from mathos.research.tga_proctor_tape_solver import mirror_cells
    clauses = tuple(tuple(c) for c in clauses)
    p = compile_cnf(n, clauses)
    rejected = []
    steps = 0
    for values in product((False,True), repeat=len(backdoor(p))):
        rows = branch_rows(p, values)
        (ok,payload),cost = mirror_cells(p.width, rows)
        steps += cost
        if ok:
            if not verify_compiled(p,payload) or not evaluate(clauses,payload):
                raise AssertionError("invalid affine branch witness")
            return {"sat":True, "witness":tuple(payload[:n]),
                    "duals":(), "branches":len(rejected)+1,
                    "affine_structural_steps":steps}
        if not dual_valid(rows,payload,p.width):
            raise AssertionError("invalid affine branch dual")
        rejected.append(tuple(payload))
    return {"sat":False, "witness":(), "duals":tuple(rejected),
            "branches":len(rejected), "affine_structural_steps":steps}


def verify(n, clauses, result):
    """Rebuild branch rows; never trust claimed branch count or solver steps."""
    clauses = tuple(tuple(c) for c in clauses)
    p = compile_cnf(n, clauses)
    if result["sat"] is True:
        x = result["witness"]
        return (len(x)==n and all(v in (0,1) for v in x)
                and evaluate(clauses,x))
    if result["sat"] is not False:
        return False
    duals = result["duals"]
    k = len(backdoor(p))
    if len(duals) != 2**k:
        return False
    return all(dual_valid(branch_rows(p,v),w,p.width)
               for v,w in zip(product((False,True),repeat=k),duals))


def relation_counts():
    counts = {}
    for mask in range(256):
        s = {i for i in range(8) if mask >> i & 1}
        if all(a^b^c in s for a,b,c in product(s,repeat=3)):
            counts[len(s)] = counts.get(len(s),0)+1
    return counts


def controls():
    counts = relation_counts()
    assert counts == {0:1,1:8,2:28,4:14,8:1}
    signed = 0
    for signs in product((-1,1),repeat=3):
        c = tuple(s*(i+1) for i,s in enumerate(signs))
        p = compile_cnf(3,(c,))
        for x in product((False,True),repeat=3):
            assert verify_compiled(p,extend(p,x)) == evaluate((c,),x)
            # Exhaust all auxiliary assignments at this fixed original x.
            assert any(verify_compiled(p,x+z) for z in
                       product((False,True),repeat=p.width-3)) == evaluate((c,),x)
            signed += 1
    formulas = [(0,()),(2,())]
    base = [(1,1,1),(-1,-1,-1),(1,-2,1),(-1,2,-1)]
    formulas += [(2,(a,b)) for a,b in product(base,repeat=2)]
    formulas += [(3,(tuple(s*(i+1) for i,s in enumerate(signs)),))
                 for signs in product((-1,1),repeat=3)]
    sat = unsat = branches = steps = 0
    for n,cs in formulas:
        res = solve(n,cs)
        brute = any(evaluate(cs,x) for x in product((False,True),repeat=n))
        assert res["sat"] == brute and verify(n,cs,res)
        if not brute:
            assert not verify(n,cs,{**res,"duals":res["duals"][:-1]})
            w = res["duals"][0]
            bad = (tuple(False for _ in w),)+res["duals"][1:]
            assert not verify(n,cs,{**res,"duals":bad})
        sat += brute
        unsat += not brute
        branches += res["branches"]
        steps += res["affine_structural_steps"]
    return {"relations":256,"affine":sum(counts.values()),"nonaffine":204,
            "affine_by_cardinality":counts,"signed_clause_checks":signed,
            "formulas":len(formulas),"sat":sat,"unsat":unsat,
            "branches":branches,"affine_structural_steps":steps}
