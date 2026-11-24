"""F033: signed structural capacity inference for capacities one and two.

Incomplete UNSAT-only recognition. Original clause certificates establish
a counting contradiction without trusting graph discovery or matching.
"""
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb
from random import Random

from . import tga_proctor_hall as hall
from . import tga_proctor_signed_hall as signed
from . import tga_proctor_xor_cnf as xor
from . import tga_proctor_blind_parity as blind
from . import tga_proctor_hybrid_sat as hybrid
from . import tga_proctor_xor_bve as bve

PNP_RESOLUTION_STATUS = "OPEN"


def _key(lit):
    return abs(lit), lit


def _ordered(lits):
    return tuple(sorted(lits,key=_key))


def _discover(cs,k):
    """Complete (k+1)-uniform components on signed capacity literals.

    Compare component sizes for both polarities of a variable. A tied
    size selects neither. Incomplete components supply no evidence.
    """
    edges = {}
    for i,c in enumerate(cs):
        s = set(c)
        if len(s)==k+1 and not any(-l in s for l in s):
            edges.setdefault(_ordered(-l for l in s),i)
    parent = {}
    def find(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]]
            v=parent[v]
        return v
    for edge in edges:
        for v in edge:
            parent.setdefault(v,v)
        for v in edge[1:]:
            a,b=find(edge[0]),find(v)
            if a!=b:
                parent[b]=a
    components = defaultdict(list)
    counts = Counter()
    for v in parent:
        components[find(v)].append(v)
    for edge in edges:
        counts[find(edge[0])]+=1
    complete = [tuple(sorted(vs,key=_key)) for root,vs in components.items()
                if counts[root]==comb(len(vs),k+1)]
    # The sort key is independent of signs under variable complementation.
    complete.sort(key=lambda g:tuple(abs(l) for l in g))
    owner = {v:i for i,g in enumerate(complete) for v in g}
    size = {v:len(complete[i]) for v,i in owner.items()}
    eligible = {v for v in owner if size[v]>size.get(-v,0)}
    demand_candidates = {}
    for i,c in enumerate(cs):
        s = set(c)
        if s and s<=eligible:
            demand_candidates.setdefault(_ordered(s),i)
    chosen,used = [],set()
    for vs,i in sorted(demand_candidates.items(),
                       key=lambda item:(len(item[0]),tuple(abs(l) for l in item[0]))):
        if not used.intersection(vs):
            chosen.append((i,vs))
            used.update(vs)
    return chosen,complete,owner,edges,eligible


def solve(n,clauses,capacity=1):
    if type(capacity) is not int or capacity not in (1,2):
        raise ValueError("capacity must be 1 or 2")
    cs = xor._input(n,clauses)
    k = capacity
    demands,groups,owner,edges,eligible = _discover(cs,k)
    # Each group is represented by k interchangeable resource slots.
    neighbors = tuple(tuple(sorted({k*owner[l]+j for l in vs for j in range(k)}))
                      for _,vs in demands)
    subset,scans = hall._deficiency(neighbors)
    common = dict(capacity=k,eligible_variables=len(eligible),demands=len(demands),
                  groups=len(groups),edge_scans=scans,resolution_status=PNP_RESOLUTION_STATUS)
    if subset is None:
        return dict(status="UNKNOWN",**common)
    used = {l for i in subset for l in demands[i][1]}
    proof_groups = []
    for group in groups:
        vs = tuple(l for l in group if l in used)
        if vs:
            cap=min(k,len(vs))
            refs=tuple(edges[_ordered(edge)] for edge in combinations(vs,cap+1))
            proof_groups.append((vs,cap,refs))
    cert=dict(demands=tuple(sorted(demands[i][0] for i in subset)),
              groups=tuple(proof_groups))
    out=dict(status="UNSAT",certificate=cert,**common)
    if not verify(n,cs,out):
        raise AssertionError("capacity proof rejected")
    return out


def verify(n,clauses,result):
    """Check signed disjoint demands and a partition into capacity groups.

    For a group of capacity c, all (c+1)-subsets must have their exact
    complementary clause in the original CNF. A capacity equal to
    group size needs no clauses. No matching, graph or orientation.
    """
    cs=xor._input(n,clauses)
    try:
        if result["status"]!="UNSAT":
            return False
        cert=result["certificate"]
        ds=tuple(cert["demands"])
        if (not ds or any(type(i) is not int or not 0<=i<len(cs) for i in ds)
                or tuple(sorted(set(ds)))!=ds):
            return False
        required,ids=set(),set()
        for i in ds:
            lits=set(cs[i])
            vs={abs(l) for l in lits}
            if not lits or len(vs)!=len(lits) or ids.intersection(vs):
                return False
            ids.update(vs)
            required.update(lits)
        covered,total=set(),0
        for variables,cap,refs in cert["groups"]:
            vs,refs=tuple(variables),tuple(refs)
            if (not vs or any(type(l) is not int or l not in required for l in vs)
                    or _ordered(set(vs))!=vs or covered.intersection(vs)
                    or type(cap) is not int or not 1<=cap<=min(2,len(vs))
                    or len(refs)!=comb(len(vs),cap+1)):
                return False
            covered.update(vs)
            total+=cap
            for edge,i in zip(combinations(vs,cap+1),refs):
                if type(i) is not int or not 0<=i<len(cs) or set(cs[i])!={-l for l in edge}:
                    return False
        return covered==required and total<len(ds)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def solve_hybrid(n,clauses,pair_limit=100000,node_limit=1024,*,allow_wide=False):
    bve._budget(pair_limit)
    bve._budget(node_limit)
    if type(allow_wide) is not bool:
        raise ValueError("allow_wide must be Boolean")
    cs=xor._input(n,clauses)
    scans=0
    for k in (1,2):
        r=solve(n,cs,k)
        scans+=r["edge_scans"]
        if r["status"]=="UNSAT":
            return dict(status="UNSAT",route="CAPACITY",proof=r,ids=hybrid._ids(cs),
                        pair_tests=0,search_nodes=0,pair_limit=pair_limit,node_limit=node_limit,
                        capacity_edge_scans=scans,
                        cost_model="SEPARATE_ABSTRACT_PAIR_NODE_AND_CAPACITY_EDGE_COUNTS",
                        resolution_status=PNP_RESOLUTION_STATUS)
    return dict(signed.solve_hybrid(n,cs,pair_limit,node_limit,allow_wide=allow_wide),
                capacity_edge_scans=scans)


def verify_hybrid(n,clauses,result,*,allow_wide=False):
    cs=xor._input(n,clauses)
    try:
        if result["route"]=="CAPACITY":
            return (result["status"]=="UNSAT" and tuple(result["ids"])==hybrid._ids(cs)
                    and verify(n,cs,result["proof"]))
        return signed.verify_hybrid(n,cs,result,allow_wide=allow_wide)
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):
        return False


def capacity_cnf(neighbors,k):
    """One variable per demand/resource incidence; complete capacity clauses."""
    if type(k) is not int or k not in (1,2):
        raise ValueError("capacity must be 1 or 2")
    resources,rows=defaultdict(list),[]
    top=0
    for ns in neighbors:
        row=[]
        for j in sorted(set(ns)):
            top+=1
            row.append(top)
            resources[j].append(top)
        if not row:
            raise ValueError("empty fixture demand")
        rows.append(tuple(row))
    for vs in resources.values():
        rows.extend(tuple(-l for l in edge) for edge in combinations(vs,k+1))
    return top,tuple(rows)


def php(holes,k,pigeons=None):
    if pigeons is None:
        pigeons=k*holes+1
    return capacity_cnf((range(holes) for _ in range(pigeons)),k)


def noisy(n,cs):
    """Same shared-variable noise as the rare-side negative family."""
    return n+1,tuple(cs)+tuple((v,n+1) for v in range(1,n+1))


def controls():
    rng=Random(33003)
    counts=Counter()
    for _ in range(1600):
        ids=tuple(10**40+19*i for i in range(rng.randrange(1,7)))
        n=2**200
        cs=tuple(tuple(rng.choice((-1,1))*rng.choice(ids)
                       for _ in range(rng.randrange(0,6)))
                 for _ in range(rng.randrange(18)))
        sat=xor._brute(cs)
        flipped=signed._flip(cs,tuple(v for v in ids if rng.randrange(2)))
        for k in (1,2):
            a,b=solve(n,cs,k),solve(n,flipped,k)
            if a["status"]!=b["status"]:
                raise AssertionError("polarity equivariance failed")
            for f,r in ((cs,a),(flipped,b)):
                if r["status"]=="UNSAT":
                    if sat or not verify(n,f,r):
                        raise AssertionError("false capacity certificate")
                elif r["status"]!="UNKNOWN" or verify(n,f,r):
                    raise AssertionError("bad status")
            counts[a["status"]]+=1
    fixtures=[]
    for k,sizes in ((1,(2,3,4,5,8,16,32)),(2,(2,3,4,5,8,16))):
        for holes in sizes:
            for seed in (11,29):
                n,cs=php(holes,k)
                n,cs=noisy(n,cs)
                sn,shuffled=blind.relabel(n,cs,seed)
                old=signed.solve(sn,shuffled)
                r=solve(sn,shuffled,k)
                if r["status"]!="UNSAT" or not verify(sn,shuffled,r):
                    raise AssertionError("capacity fixture failed")
                if k==1 and old["status"]!="UNKNOWN":
                    raise AssertionError("rare-side control changed")
                wrapped=solve_hybrid(sn,shuffled,0,0)
                if wrapped["route"]!="CAPACITY" or not verify_hybrid(sn,shuffled,wrapped):
                    raise AssertionError("capacity route failed")
                en,ec=php(holes,k,k*holes)
                en,ec=noisy(en,ec)
                en,ec=blind.relabel(en,ec,seed)
                if solve(en,ec,k)["status"]!="UNKNOWN":
                    raise AssertionError("equal capacity refuted")
                cert=r["certificate"]
                fixtures.append(dict(capacity=k,holes=holes,seed=seed,clauses=len(shuffled),
                                     demands=len(cert["demands"]),
                                     total_capacity=sum(g[1] for g in cert["groups"]),
                                     edge_scans=r["edge_scans"],search_nodes=0,pair_tests=0))
    return dict(random_cases=1600,paired_capacity_runs=6400,outcomes=dict(counts),
                fixtures=fixtures,equal_controls=len(fixtures),resolution_status=PNP_RESOLUTION_STATUS,
                complete_cnf_solver=False,machine_refinement=False,independent_review=False)


if __name__=="__main__":
    import json
    print(json.dumps(controls(),indent=2))
