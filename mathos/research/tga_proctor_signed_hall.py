"""F033: polarity-equivariant rare-side Hall recognition.

Recognizes a restricted signed matching encoding, not arbitrary CNF.
Reuses the F033 positive Hall checker after a certified variable flip.
"""
from collections import Counter
from itertools import product
from random import Random

from . import tga_proctor_hall as hall
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_hybrid_sat as hybrid
from . import tga_proctor_xor_bve as bve
from .tga_proctor_hybrid_adversary import pigeonhole

PNP_RESOLUTION_STATUS = "OPEN"


def orientation(n, clauses):
    """Rare demand side occurs once; the opposite side does not occur once.

    Ignore tautologies and repeated clauses/literals before counting.
    Ambiguous variables are excluded, rather than assigned an orientation
    that depends on their original signs.
    """
    cs = xor._input(n,clauses)
    rows = {frozenset(c) for c in cs}
    counts = Counter(l for c in rows if not any(-l in c for l in c) for l in c)
    return tuple(sorted((l for l in counts if counts[l]==1 and counts[-l]!=1),
                        key=abs))


def _flip(cs, flips):
    f = set(flips)
    return tuple(tuple(-l if abs(l) in f else l for l in c) for c in cs)


def solve(n, clauses):
    cs = xor._input(n,clauses)
    oriented = orientation(n,cs)
    eligible = {abs(l) for l in oriented}
    flips = tuple(-l for l in oriented if l<0)
    # Preserve original clause indices, even when dropping clauses with
    # ineligible variables. An empty clause is harmless to this route.
    selected = tuple(i for i,c in enumerate(cs) if all(abs(l) in eligible for l in c))
    sub = _flip(tuple(cs[i] for i in selected),flips)
    r = hall.solve(n,sub)
    common = dict(eligible_variables=len(eligible), selected_clauses=len(selected),
                  edge_scans=r["edge_scans"], resolution_status=PNP_RESOLUTION_STATUS)
    if r["status"]!="UNSAT":
        return dict(status="UNKNOWN",**common)
    cert = r["certificate"]
    remapped = dict(demands=tuple(selected[i] for i in cert["demands"]),
                    groups=tuple((vs,tuple(selected[i] for i in refs))
                                 for vs,refs in cert["groups"]))
    out = dict(status="UNSAT",flips=flips,certificate=remapped,**common)
    if not verify(n,cs,out):
        raise AssertionError("signed Hall replay failed")
    return out


def verify(n, clauses, result):
    """Original-CNF replay with explicit canonical flip list.

    The orientation heuristic, subset selection and matching are not
    trusted. Any variable complementation is an involution on models.
    """
    cs = xor._input(n,clauses)
    try:
        if result["status"]!="UNSAT":
            return False
        flips = tuple(result["flips"])
        ids = {abs(l) for c in cs for l in c}
        if (any(type(v) is not int or v not in ids for v in flips)
                or tuple(sorted(set(flips)))!=flips):
            return False
        return hall.verify(n,_flip(cs,flips),
                           dict(status="UNSAT",certificate=result["certificate"]))
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def solve_hybrid(n, clauses, pair_limit=100000, node_limit=1024, *, allow_wide=False):
    bve._budget(pair_limit)
    bve._budget(node_limit)
    if type(allow_wide) is not bool:
        raise ValueError("allow_wide must be Boolean")
    cs = xor._input(n,clauses)
    r = solve(n,cs)
    if r["status"]=="UNSAT":
        return dict(status="UNSAT",route="SIGNED_HALL",proof=r,ids=hybrid._ids(cs),
                    pair_tests=0,search_nodes=0,pair_limit=pair_limit,node_limit=node_limit,
                    signed_hall_edge_scans=r["edge_scans"],
                    cost_model="SEPARATE_ABSTRACT_PAIR_NODE_AND_HALL_EDGE_COUNTS",
                    resolution_status=PNP_RESOLUTION_STATUS)
    return dict(hall.solve_hybrid(n,cs,pair_limit,node_limit,allow_wide=allow_wide),
                signed_hall_edge_scans=r["edge_scans"])


def verify_hybrid(n,clauses,result,*,allow_wide=False):
    cs = xor._input(n,clauses)
    try:
        if result["route"]=="SIGNED_HALL":
            return (result["status"]=="UNSAT" and tuple(result["ids"])==hybrid._ids(cs)
                    and verify(n,cs,result["proof"]))
        return hall.verify_hybrid(n,cs,result,allow_wide=allow_wide)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def noisy_php(holes):
    """Preserve UNSAT while defeating rare-side recognition by extra clauses."""
    n,cs = pigeonhole(holes)
    g = n+1
    return g,cs+tuple((v,g) for v in range(1,n+1))


def controls():
    rng = Random(33002)
    counts = Counter()
    for _ in range(1600):
        ids = tuple(10**40+37*i for i in range(rng.randrange(1,7)))
        n = 2**200
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(0,6)))
                   for _ in range(rng.randrange(18)))
        flips = tuple(v for v in ids if rng.randrange(2))
        flipped = _flip(cs,flips)
        a,b = solve(n,cs),solve(n,flipped)
        if a["status"]!=b["status"] or a["edge_scans"]!=b["edge_scans"]:
            raise AssertionError("polarity invariance failed")
        sat = xor._brute(cs)
        for formula,r in ((cs,a),(flipped,b)):
            if r["status"]=="UNSAT":
                if sat or not verify(n,formula,r):
                    raise AssertionError("unsound signed certificate")
            elif r["status"]!="UNKNOWN" or verify(n,formula,r):
                raise AssertionError("invalid result")
        counts[a["status"]] += 1
    php = []
    for holes in (2,3,4,5,6,7,16,32,64):
        for seed in (11,29):
            n,cs = pigeonhole(holes)
            sn,shuffled = blind.relabel(n,cs,seed)
            r = solve_hybrid(sn,shuffled,0,0)
            if (r["route"]!="SIGNED_HALL" or not verify_hybrid(sn,shuffled,r)
                    or r["search_nodes"] or r["pair_tests"]):
                raise AssertionError("signed PHP recovery failed")
            proof = r["proof"]
            if (len(proof["certificate"]["demands"])!=holes+1
                    or len(proof["certificate"]["groups"])!=holes):
                raise AssertionError("wrong deficiency")
            # Equal-size canonical encoding is satisfiable.
            en,ec = pigeonhole(holes,holes)
            en,ec = blind.relabel(en,ec,seed)
            if solve(en,ec)["status"]!="UNKNOWN":
                raise AssertionError("equal-size false refutation")
            php.append(dict(holes=holes,seed=seed,variables=len(r["ids"]),
                            clauses=len(shuffled),flips=len(proof["flips"]),
                            edge_scans=r["signed_hall_edge_scans"],search_nodes=0,pair_tests=0))
    negative = []
    for holes in (2,3,4,5,8,16):
        n,cs = noisy_php(holes)
        n,cs = blind.relabel(n,cs,29)
        r = solve(n,cs)
        if r["status"]!="UNKNOWN" or r["eligible_variables"]!=0:
            raise AssertionError("rare-side negative control failed")
        negative.append(dict(holes=holes,clauses=len(cs),status=r["status"],
                             eligible_variables=r["eligible_variables"]))
    return dict(random_cases=1600,paired_polarity_runs=3200,outcomes=dict(counts),
                signed_php=php,equal_size_controls=len(php),noisy_negative=negative,
                resolution_status=PNP_RESOLUTION_STATUS,complete_cnf_solver=False,
                machine_refinement=False,independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
