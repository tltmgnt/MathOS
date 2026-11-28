"""Counterexample-guided refinement of grouped parity criteria.

The finite grammar consists of conjunctions of parity checks on
partitions of graph components. A bounded symbolic search is followed
by independent CNF certificate replay; survival is not a universal proof.
"""
from itertools import combinations, product
import random
from .pnp_cross_model import prism
from .pnp_component_parity import propose,verify
from .pnp_inference_complexity import budget
from .pnp_evidence_benchmark import digest

PARTITIONS=("global","size","mod2","mod3")
MAX_COMPONENTS=6
TRAIN_SIZES=(3,4)
SEED=27027
HOLDOUT_COUNT=24


def grammar():
    # Component-local is the strongest primitive; prefer cheaper
    # aggregation rules first, including conjunctions of two rules.
    return [(p,) for p in PARTITIONS]+list(combinations(PARTITIONS,2))+[("component",)]


def _case(case):
    if not isinstance(case,(list,tuple)) or not 1<=len(case)<=12:
        raise ValueError("invalid component count")
    out=[]
    for m,odd in case:
        if type(m) is not int or not 3<=m<=8 or type(odd) is not bool:
            raise ValueError("invalid component descriptor")
        out.append((m,odd))
    return tuple(out)


def build(case):
    n=0
    f=[]
    for m,odd in _case(case):
        k,g,_=prism(m,inconsistent=odd)
        f.extend(tuple(x+n if x>0 else x-n for x in c) for c in g)
        n+=k
    return n,tuple(f)


def groups(rule,case):
    """Group component indices by the declared partition."""
    bins={}
    for i,(m,_) in enumerate(case):
        key=0 if rule=="global" else m if rule=="size" else i%2 if rule=="mod2" else i%3 if rule=="mod3" else i
        bins.setdefault(key,[]).append(i)
    return tuple(bins.values())


def predict(candidate,case):
    if tuple(candidate) not in grammar():
        raise ValueError("unknown hypothesis")
    case=_case(case)
    return all(sum(case[i][1] for i in group)%2==0
               for rule in candidate for group in groups(rule,case))


def reference(case):
    return not any(odd for _,odd in case)


def training():
    """Total order defines exact bounded counterexample minimality.

    Minimize component count, then variable count (sum of prism sizes),
    then lexicographic descriptor. This is not CNF deletion minimality.
    """
    symbols=tuple(product(TRAIN_SIZES,(False,True)))
    for k in range(1,MAX_COMPONENTS+1):
        yield from sorted(product(symbols,repeat=k),key=lambda c:(sum(m for m,_ in c),c))


def holdout():
    rng=random.Random(SEED)
    cases=[]
    # Include even controls, odd global controls, and even-global
    # contradictions; choose sizes outside the training alphabet.
    for i in range(HOLDOUT_COUNT):
        k=rng.randint(7,12)
        sizes=[rng.randint(5,8) for _ in range(k)]
        charged=set(rng.sample(range(k),(0,1,2,4)[i%4]))
        cases.append(tuple((m,j in charged) for j,m in enumerate(sizes)))
    return cases


def certify(case):
    n,f=build(case)
    proof=propose(n,f,budget())
    if proof is None:
        raise AssertionError("parity recognition failed")
    verify_case(case,proof)
    return proof


def verify_case(case,proof):
    case=_case(case)
    n,f=build(case)
    verify(n,f,proof,budget())
    rows=proof["rows"]
    # Each prism has 2m vertex equations; dense labels of separate
    # prisms occupy successive disjoint intervals.
    expected=[]
    offset=0
    for m,odd in case:
        expected.append((2*m,int(odd),offset+1,offset+3*m))
        offset+=3*m
    actual=[]
    for ids in proof["components"]:
        support={v for i in ids for v in rows[i][0]}
        actual.append((len(ids),sum(rows[i][1] for i in ids)%2,min(support),max(support)))
    if sorted(actual,key=lambda a:a[2])!=expected or (proof["decision"]=="sat")!=reference(case):
        raise ValueError("component signature or verdict mismatch")
    return True


def first_counterexample(candidate):
    examined=0
    for case in training():
        examined+=1
        if predict(candidate,case)!=reference(case):
            return case,examined
    return None,examined


def refine():
    remaining=grammar()
    rounds=[]
    while remaining:
        candidate=remaining[0]
        case,examined=first_counterexample(candidate)
        if case is None:
            return {"rounds":rounds,"selected":candidate,"final_examined":examined,
                    "remaining":remaining,"status":"bounded_survivor"}
        proof=certify(case)
        sat=proof["decision"]=="sat"
        eliminated=[p for p in remaining if predict(p,case)!=sat]
        if candidate not in eliminated:
            raise AssertionError("counterexample failed to eliminate candidate")
        remaining=[p for p in remaining if p not in eliminated]
        rounds.append({"candidate":candidate,"case":case,"examined":examined,
                       "eliminated":eliminated,"remaining":remaining.copy(),"proof":proof})
    return {"rounds":rounds,"selected":None,"final_examined":0,
            "remaining":[],"status":"grammar_exhausted"}


def verify_refinement(r):
    """Replay finite order and elimination independently of proof generation."""
    remaining=grammar()
    for row in r["rounds"]:
        if not remaining or tuple(row["candidate"])!=remaining[0]:
            raise ValueError("candidate not first surviving rule")
        candidate=remaining[0]
        case,examined=first_counterexample(candidate)
        if case is None or digest(row["case"])!=digest(case) or row["examined"]!=examined:
            raise ValueError("incorrect or nonminimal bounded counterexample")
        verify_case(case,row["proof"])
        sat=row["proof"]["decision"]=="sat"
        eliminated=[p for p in remaining if predict(p,case)!=sat]
        remaining=[p for p in remaining if p not in eliminated]
        if digest(row["eliminated"])!=digest(eliminated) or digest(row["remaining"])!=digest(remaining):
            raise ValueError("incorrect refinement")
    if not remaining:
        expected=(None,0,"grammar_exhausted")
    else:
        case,examined=first_counterexample(remaining[0])
        if case is not None:
            raise ValueError("premature bounded survivor")
        expected=(remaining[0],examined,"bounded_survivor")
    if (digest(r["selected"])!=digest(expected[0]) or r["final_examined"]!=expected[1] or
            r["status"]!=expected[2] or digest(r["remaining"])!=digest(remaining)):
        raise ValueError("invalid refinement conclusion")
    return True
