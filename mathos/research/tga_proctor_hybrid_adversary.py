"""F032: arbitrary-width opt-in and pigeonhole boundary of hybrid routing."""
from collections import Counter
from itertools import combinations
from random import Random

from . import tga_proctor_hybrid_sat as hybrid
from . import tga_proctor_dynamic_components as dynamic
from . import tga_proctor_dynamic_resolution as resolution
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_xor_bve as bve

PNP_RESOLUTION_STATUS = "OPEN"


def pigeonhole(holes, pigeons=None):
    """Unary PHP: every pigeon in at least one hole, no sharing."""
    if type(holes) is not int or holes < 2:
        raise ValueError("holes >=2 required")
    if pigeons is None:
        pigeons = holes+1
    if type(pigeons) is not int or pigeons < 1:
        raise ValueError("positive pigeon count required")
    def var(i,j):
        return i*holes+j+1
    cs = [tuple(var(i,j) for j in range(holes)) for i in range(pigeons)]
    cs.extend((-var(i,j),-var(k,j)) for j in range(holes)
              for i,k in combinations(range(pigeons),2))
    return holes*pigeons, tuple(cs)


def audit_php(holes, limit):
    n,cs = pigeonhole(holes)
    if xor.detect(n,cs) or blind.schedule(n,cs):
        raise AssertionError("PHP unexpectedly recognized")
    r = hybrid.solve(n,cs,1000,limit,allow_wide=True)
    if r["pair_tests"] != 0 or r["search_nodes"] > limit:
        raise AssertionError("unexpected budget use")
    lines = None
    if r["status"] == "UNSAT":
        if r["route"] != "DYNAMIC_PROJECTED" or not hybrid.verify(n,cs,r,allow_wide=True):
            raise AssertionError("unexpected PHP route")
        pre,search = r["proof"]
        if pre["eliminations"] or pre["steps"] or bve.replay(n,cs,pre) != tuple(tuple(sorted(c)) for c in cs):
            raise AssertionError("PHP projection not identity")
        p = resolution.extract(n,cs,search,wide=True)
        if not resolution.verify(n,cs,p,wide=True):
            raise AssertionError("resolution extraction failed")
        lines = len(p["steps"])
    elif r["status"] != "UNKNOWN" or r["reason"] != "SEARCH_BUDGET":
        raise AssertionError("invalid PHP outcome")
    return dict(holes=holes, variables=n, clauses=len(cs), status=r["status"],
                search_nodes=r["search_nodes"], pair_tests=0, resolution_lines=lines)


def controls():
    rng = Random(32005)
    outcomes = Counter()
    for _ in range(1000):
        ids = tuple(10**40+41*i for i in range(rng.randrange(1,8)))
        n = 2**200
        cs = tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                         for _ in range(rng.randrange(0,10)))
                   for _ in range(rng.randrange(20)))
        sat = xor._brute(cs)
        r = hybrid.solve(n,cs,20,10000,allow_wide=True)
        if r["status"] != ("SAT" if sat else "UNSAT") or not hybrid.verify(n,cs,r,allow_wide=True):
            raise AssertionError("wide hybrid mismatch")
        if r["search_nodes"] > 10000 or r["pair_tests"] > 20:
            raise AssertionError("budget mismatch")
        outcomes[r["status"]] += 1
    php = [audit_php(k,100000 if k<=5 else 1000) for k in range(2,8)]
    if any(row["status"]!="UNSAT" for row in php[:4]):
        raise AssertionError("small PHP not completed")
    selectors = []
    for q in (4,8,16):
        for charge in (True,False):
            n,cs = resolution.tseitin(q,resolution.cubic_graph(q,11),(charge,)+(False,)*(q-1))
            m,guarded = blind.shared_selector(n,cs)
            sn,shuffled = blind.relabel(m,guarded,47)
            old = hybrid.solve(sn,shuffled,1000,10000)
            r = hybrid.solve(sn,shuffled,1000,10000,allow_wide=True)
            if (old["status"] != "UNKNOWN" or r["status"] != ("UNSAT" if charge else "SAT")
                    or not hybrid.verify(sn,shuffled,r,allow_wide=True)):
                raise AssertionError("shared selector recovery mismatch")
            selectors.append(dict(vertices=q,odd_charge=charge,status=r["status"],
                                  nodes=r["search_nodes"],route=r["route"]))
    return dict(random_cases=1000,outcomes=dict(outcomes),php=php,shared_selector=selectors,
                resolution_status=PNP_RESOLUTION_STATUS,universal_bound=False,
                machine_refinement=False,independent_review=False)


if __name__ == "__main__":
    import json
    print(json.dumps(controls(),indent=2))
