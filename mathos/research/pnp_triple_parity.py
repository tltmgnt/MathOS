"""Exact signed triple-block to 2-CNF reduction, with independent replay.

Each supported block has six distinct ternary clauses on one triple, leaving
exactly two complementary satisfying assignments. Arbitrary mixtures of
overlapping supported blocks are allowed. This is not unrestricted 3-SAT.
"""
from itertools import product
from .pnp_structural_kernel import normalize, truth
from .pnp_certificate_routes import propose as propose_route, verify as verify_route

BITS = tuple(product((False, True), repeat=3))


def _groups(f, budget):
    groups = {}
    for clause in f:
        budget.tick(1 + len(clause))
        if len(clause) != 3:
            return None
        key = tuple(sorted(abs(x) for x in clause))
        if len(set(key)) != 3:
            return None
        groups.setdefault(key, []).append(clause)
    return groups


def _allowed_from_missing(key, clauses):
    # A ternary clause forbids precisely its all-false assignment.
    patterns = {tuple(-v in c for v in key) for c in clauses}
    return [bits for bits in BITS if bits not in patterns]


def _pair_clauses(a, b, different):
    if different:
        return ((a, b), (-a, -b))
    return ((-a, b), (a, -b))


def propose(n, clauses, budget):
    nn, f, mapping = normalize(n, clauses)
    groups = _groups(f, budget)
    if groups is None:
        return None
    blocks, binary = [], []
    for key, block in sorted(groups.items()):
        budget.tick(1 + len(block))
        if len(block) != 6:
            return None
        allowed = _allowed_from_missing(key, block)
        if len(allowed) != 2 or any(a == b for a, b in zip(*allowed)):
            return None
        a, b, c = key
        bits = allowed[0]
        parities = (bits[0] != bits[1], bits[0] != bits[2])
        blocks.append({"variables": key, "parities": parities})
        binary.extend(_pair_clauses(a, b, parities[0]))
        binary.extend(_pair_clauses(a, c, parities[1]))
    bn, bf, active = normalize(nn, binary)
    if bn != nn or active != tuple(range(1, nn+1)):
        raise AssertionError("binary reduction lost active variables")
    proof = propose_route(bn, bf, "two_sat", budget)
    if proof is None:
        raise AssertionError("binary solver rejected binary reduction")
    return {"schema": "mathos-pnp-triple-parity/1", "normalized_n": nn,
            "new_to_old": mapping, "blocks": blocks, "binary_clauses": bf,
            "decision_certificate": proof, "n": 0,
            "clauses": proof["clauses"]}


def verify(n, clauses, artifact, budget):
    """Verify each local truth table, exact binary assembly and nested proof.

    Does not trust the generator's missing-pattern derivation or claimed
    parity bits. A malformed or out-of-scope artifact is rejected.
    """
    nn, f, mapping = normalize(n, clauses)
    if (artifact["schema"] != "mathos-pnp-triple-parity/1" or
            type(artifact["normalized_n"]) is not int or artifact["normalized_n"] != nn or
            tuple(artifact["new_to_old"]) != mapping):
        raise ValueError("normalization metadata mismatch")
    groups = {}
    for clause in f:
        budget.tick(1 + len(clause))
        if len(clause) != 3:
            raise ValueError("nonternary clause")
        support = tuple(sorted({abs(x) for x in clause}))
        if len(support) != 3:
            raise ValueError("invalid block support")
        groups.setdefault(support, []).append(clause)
    seen, assembled = set(), set()
    for block in artifact["blocks"]:
        key = tuple(block["variables"])
        parity = tuple(block["parities"])
        if (len(key) != 3 or any(type(v) is not int for v in key) or
                key in seen or key not in groups or len(groups[key]) != 6 or
                len(parity) != 2 or any(type(x) is not bool for x in parity)):
            raise ValueError("invalid or repeated block")
        seen.add(key)
        a, b, c = key
        # Construct each relation by enumerating its forbidden pair patterns.
        local = []
        for neighbor, different in zip((b, c), parity):
            for x, y in product((False, True), repeat=2):
                if (x != y) != different:
                    local.append(tuple(sorted((-a if x else a,
                                               -neighbor if y else neighbor))))
        for bits in BITS:
            budget.tick(1 + len(groups[key]) + len(local))
            assignment = dict(zip(key, bits))
            def holds(q):
                return all(any(assignment[abs(x)] == (x > 0) for x in clause)
                           for clause in q)
            if holds(groups[key]) != holds(local):
                raise ValueError("triple-to-binary truth table mismatch")
        assembled.update(local)
    if seen != set(groups):
        raise ValueError("missing block")
    bn, bf, active = normalize(nn, tuple(assembled))
    if (bn != nn or active != tuple(range(1, nn+1)) or
            bf != tuple(tuple(c) for c in artifact["binary_clauses"])):
        raise ValueError("binary assembly mismatch")
    proof = artifact["decision_certificate"]
    if proof["route"] != "two_sat":
        raise ValueError("binary proof has wrong route")
    verify_route(bn, bf, proof, budget)
    expected = tuple(tuple(c) for c in proof["clauses"])
    if (type(artifact["n"]) is not int or artifact["n"] != 0 or
            tuple(tuple(c) for c in artifact["clauses"]) != expected):
        raise ValueError("constant output mismatch")
    if proof["kind"] == "sat_witness":
        budget.tick(1 + len(f) + sum(map(len, f)))
        if not truth(f, proof["assignment"]):
            raise ValueError("lifted witness rejected")
    return True


def block(variables, bits):
    """Six clauses forbidding every assignment except bits and its complement."""
    variables, bits = tuple(variables), tuple(bits)
    if (len(variables) != 3 or tuple(sorted(set(variables))) != variables or
            any(type(v) is not int or v <= 0 for v in variables) or
            len(bits) != 3 or any(type(x) is not bool for x in bits)):
        raise ValueError("expected sorted triple and three Boolean bits")
    return [tuple(-v if b else v for v, b in zip(variables, pattern))
            for pattern in BITS
            if pattern != bits and pattern != tuple(not b for b in bits)]


def signed_family(n, *, inconsistent=False):
    """Finite instantiation of an unbounded mathematical family.

    Consistent: all triples restrict one common nonuniform seed, up to
    complement. Inconsistent: flip one local relation on (1,2,4) to
    contradict the relation on (1,2,3). No general hardness claim.
    """
    from itertools import combinations
    if type(n) is not int or not 4 <= n <= 24:
        raise ValueError("family size must be 4..24")
    f = []
    for key in combinations(range(1, n+1), 3):
        bits = tuple(v == 1 for v in key)
        if inconsistent and key == (1, 2, 4):
            bits = (not bits[0], bits[1], bits[2])
        f.extend(block(key, bits))
    return f
