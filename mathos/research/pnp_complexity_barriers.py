"""Bounded, independently replayable demonstrations of model boundaries.

Not a construction of separating infinite oracles, a natural proof
against P/poly, or an algebrization theorem.
"""
from math import comb
from .pnp_evidence_benchmark import digest

MAX_BITS=12


def _n(n):
    if type(n) is not int or not 1<=n<=MAX_BITS:
        raise ValueError("invalid input dimension")
    return 1<<n


def transcript(n,queries):
    """All-zero transcript, with a sparse indistinguishable completion."""
    N=_n(n)
    if (not isinstance(queries,(tuple,list)) or len(queries)>N or
            any(type(q) is not int or not 0<=q<N for q in queries) or
            len(set(queries))!=len(queries)):
        raise ValueError("invalid distinct query list")
    used=set(queries)
    missing=next((q for q in range(N) if q not in used),None)
    return {"schema":"mathos-pnp-zero-transcript/1","n":n,"queries":list(queries),
            "answers":[0]*len(queries),"unqueried":missing,
            "zero_completion":{"ones":[]},"alternative_completion":None if missing is None else {"ones":[missing]},
            "query_lower_bound":N}


def verify_transcript(n,queries,r):
    N=_n(n)
    if (r["schema"]!="mathos-pnp-zero-transcript/1" or r["n"]!=n or
            r["queries"]!=list(queries) or r["query_lower_bound"]!=N or
            len(queries)>N or any(type(q) is not int or not 0<=q<N for q in queries) or
            len(set(queries))!=len(queries) or r["answers"]!=[0]*len(queries) or
            r["zero_completion"]!={"ones":[]}):
        raise ValueError("invalid zero transcript")
    x=r["unqueried"]
    if len(queries)==N:
        if x is not None or r["alternative_completion"] is not None:
            raise ValueError("invalid complete transcript")
    elif (type(x) is not int or not 0<=x<N or x in set(queries) or
            r["alternative_completion"]!={"ones":[x]}):
        raise ValueError("invalid indistinguishable completion")
    return True


def evaluate_extension(n,ones,point):
    """Multilinear extension of a sparse Boolean table over GF(3)."""
    N=_n(n)
    if (len(point)!=n or any(type(x) is not int or not 0<=x<3 for x in point) or
            any(type(i) is not int or not 0<=i<N for i in ones) or
            len(set(ones))!=len(ones)):
        raise ValueError("invalid field query")
    total=0
    for i in ones:
        term=1
        for j,x in enumerate(point):
            term=term*(x if (i>>j)&1 else 1-x)%3
        total=(total+term)%3
    return total


def algebraic_control(n):
    N=_n(n)
    point=[2]*n
    expected=pow(2,n,3)
    return {"n":n,"field":3,"point":point,"zero_value":evaluate_extension(n,[],point),
            "singleton_values":[evaluate_extension(n,[i],point) for i in range(N)],
            "expected_nonzero":expected,
            "promise":"truth table has at most one 1",
            "unrestricted_counterexample":{"ones":[0,1,2],"value":evaluate_extension(n,[0,1,2],point)} if N>=3 else None}


def verify_algebraic(r):
    n=r["n"]
    N=_n(n)
    p=r["point"]
    expected=pow(2,n,3)
    if (r["field"]!=3 or p!=[2]*n or r["zero_value"]!=0 or
            r["expected_nonzero"]!=expected or expected==0 or
            r["singleton_values"]!=[expected]*N or r["promise"]!="truth table has at most one 1"):
        raise ValueError("invalid algebraic promise control")
    # Independent basis check: at 2 both x and (1-x) equal 2 mod 3.
    if any(x%3!=2 or (1-x)%3!=2 for x in p):
        raise ValueError("invalid interpolation point")
    c=r["unrestricted_counterexample"]
    if N>=3:
        if c!={"ones":[0,1,2],"value":0} or evaluate_extension(n,[0,1,2],p)!=0:
            raise ValueError("missing cancellation counterexample")
    elif c is not None:
        raise ValueError("unexpected counterexample")
    return True


def essential(n,table):
    N=_n(n)
    if len(table)!=N or any(type(x) is not int or x not in (0,1) for x in table):
        raise ValueError("invalid truth table")
    witnesses=[]
    for j in range(n):
        bit=1<<j
        i=next((i for i in range(N) if not i&bit and table[i]!=table[i|bit]),None)
        witnesses.append(None if i is None else [i,i|bit])
    return witnesses


def essential_count(n):
    """Inclusion-exclusion over coordinates on which the function is constant."""
    _n(n)
    return sum((-1)**j*comb(n,j)*(1<<(1<<(n-j))) for j in range(n+1))


def natural_control(n):
    N=_n(n)
    parity=[i.bit_count()%2 for i in range(N)]
    return {"n":n,"table":parity,"essential_witnesses":essential(n,parity),
            "accepted_tables":essential_count(n),"total_tables":1<<N,
            "gate_lower_bound":n-1,
            "model":"single-output acyclic Boolean circuits, fan-in at most two",
            "scope":"linear gate lower bound; not useful against P/poly"}


def verify_natural(r):
    n=r["n"]
    N=_n(n)
    if (r["table"]!=[i.bit_count()%2 for i in range(N)] or
            r["accepted_tables"]!=essential_count(n) or r["total_tables"]!=1<<N or
            r["gate_lower_bound"]!=n-1 or
            r["model"]!="single-output acyclic Boolean circuits, fan-in at most two" or
            r["scope"]!="linear gate lower bound; not useful against P/poly"):
        raise ValueError("invalid natural-property control")
    witnesses=r["essential_witnesses"]
    if len(witnesses)!=n:
        raise ValueError("incomplete coordinate witnesses")
    for j,pair in enumerate(witnesses):
        if not isinstance(pair,(list,tuple)) or len(pair)!=2:
            raise ValueError("missing coordinate witness")
        a,b=pair
        if (any(type(x) is not int or not 0<=x<N for x in pair) or
                a^b!=1<<j or r["table"][a]==r["table"][b]):
            raise ValueError("incorrect essential coordinate")
    return True


BARRIERS={
    "relativization":{"reference":"https://doi.org/10.1137/0204037",
        "result":"there exist oracles A and B with P^A=NP^A and P^B!=NP^B",
        "assumptions":"none for the published oracle theorem",
        "required_analysis":"identify the exact step that fails to extend to arbitrary oracle machines",
        "status":"not_assessed"},
    "natural_proofs":{"reference":"https://doi.org/10.1006/jcss.1997.1494",
        "result":"strong pseudorandomness excludes P-natural properties useful against P/poly",
        "assumptions":"sufficiently strong pseudorandom generators as in Razborov–Rudich",
        "required_analysis":"specify circuit class, truth-table constructivity, density, usefulness and cryptographic assumption",
        "status":"not_assessed"},
    "algebrization":{"reference":"https://www.scottaaronson.com/papers/alg.pdf",
        "result":"P versus NP requires non-algebrizing techniques in the Aaronson–Wigderson framework",
        "assumptions":"their specified algebraic oracle model",
        "required_analysis":"test the claimed inclusion or separation with the appropriate low-degree oracle extension on the specified side",
        "status":"not_assessed"}
}


def dossier():
    """Explicit obligations, not a classifier that can certify barrier avoidance."""
    return {"schema":"mathos-pnp-barrier-dossier/1",
            "barriers":{k:v.copy() for k,v in BARRIERS.items()},
            "universal_algorithm":{"status":"unresolved","obligations":[
                "uniform deterministic SAT algorithm for every encoded CNF",
                "correctness on both SAT and UNSAT inputs",
                "polynomial bit complexity including recognition, transformation and proof construction"]},
            "universal_lower_bound":{"status":"unresolved","obligations":[
                "quantify over all uniform polynomial-time SAT algorithms",
                "show why any proposed restricted proof-system transfer covers those algorithms",
                "account for construction cost, proof lengths and correctness of the simulation"]},
            "scope":"finite controls do not establish avoidance of any published barrier",
            "p_equals_np_established":False,"p_not_equals_np_established":False}


def verify_dossier(r):
    if digest(r)!=digest(dossier()):
        raise ValueError("unsupported barrier or universal claim")
    return True
