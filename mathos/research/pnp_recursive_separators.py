"""Recursive separator/conditioning certificates with independent replay.

AND nodes partition clauses into disjoint variable sets. OR nodes exhaust
both values of a variable. Leaves use v7 direct algebra or explicit terminal
clauses. Unknown is propagated conservatively. Depth and node caps are
operational limits, not asymptotic hardness claims.
"""
from .pnp_structural_kernel import normalize, Exhausted
from .pnp_constraint_algebra import MODES, propose, verify
from .pnp_compositional import components

MAX_DEPTH = 12
MAX_NODES = 4096
MAX_CANDIDATES = 32


def _options(depth, nodes, candidates):
    for value, lo, hi in ((depth,0,MAX_DEPTH),(nodes,1,MAX_NODES),
                          (candidates,1,MAX_CANDIDATES)):
        if type(value) is not int or not lo <= value <= hi:
            raise ValueError("invalid recursion limit")


def _active(f):
    return {abs(x) for c in f for x in c}


def _restrict(f, v, b, budget):
    lit = v if b else -v
    out = []
    for c in f:
        budget.tick(1+len(c))
        if lit not in c:
            out.append(tuple(x for x in c if x != -lit))
    return tuple(out)


def _split_choice(n, f, limit, budget):
    """Score structural vertex deletion, not speculative SAT decisions."""
    counts = {v:0 for v in _active(f)}
    for c in f:
        budget.tick(1+len(c))
        for x in c:
            counts[abs(x)] += 1
    candidates = sorted(counts, key=lambda v:(-counts[v],v))[:limit]
    best = None
    for v in candidates:
        projected = []
        for c in f:
            budget.tick(1+len(c))
            d = tuple(x for x in c if abs(x)!=v)
            if d:
                projected.append(d)
        pieces = components(n, projected, budget)
        sizes = [len(_active(projected[i] for i in ids)) for ids in pieces]
        score = (max(sizes,default=0),sum(s*s for s in sizes),-counts[v],v)
        if best is None or score < best[0]:
            best = (score,v,len(pieces))
    return best[1],best[2]


def _merge(kind, decisions):
    if kind=="and":
        return "unsat" if "unsat" in decisions else ("sat" if all(x=="sat" for x in decisions) else "unknown")
    return "sat" if "sat" in decisions else ("unsat" if all(x=="unsat" for x in decisions) else "unknown")


class _Meter:
    def __init__(self, cap):
        self.cap=cap
        self.data={"nodes":0,"and_nodes":0,"split_nodes":0,"separator_splits":0,
                   "fallback_splits":0,"leaves":0,"algebra_leaves":0,
                   "unknown_leaves":0,"max_split_depth":0,"literal_visit_proxy":0}
    def enter(self, f, depth, budget):
        self.data["nodes"]+=1
        if self.data["nodes"]>self.cap:
            raise Exhausted("recursive node limit")
        self.data["max_split_depth"]=max(depth,self.data["max_split_depth"])
        self.data["literal_visit_proxy"]+=sum(map(len,f))
        budget.tick(1+len(f)+sum(map(len,f)))
    def kind(self, kind, separator=False):
        d=self.data
        if kind=="and":
            d["and_nodes"]+=1
        elif kind=="split":
            d["split_nodes"]+=1
            d["separator_splits" if separator else "fallback_splits"]+=1
        else:
            d["leaves"]+=1
            d["algebra_leaves"]+=kind=="algebra"
            d["unknown_leaves"]+=kind=="unknown"


def search(n, clauses, budget, *, depth=4, nodes=MAX_NODES, candidates=MAX_CANDIDATES):
    _options(depth,nodes,candidates)
    nn,f,mapping=normalize(n,clauses)
    meter=_Meter(nodes)

    def build(local, remaining, level):
        meter.enter(local,level,budget)
        if not local:
            meter.kind("empty")
            return {"kind":"empty","decision":"sat"}
        if () in local:
            meter.kind("conflict")
            return {"kind":"conflict","decision":"unsat"}
        pieces=components(nn,local,budget)
        if len(pieces)>1:
            meter.kind("and")
            children=[{"indices":ids,"tree":build(tuple(local[i] for i in ids),remaining,level)}
                      for ids in pieces]
            return {"kind":"and","children":children,
                    "decision":_merge("and",[c["tree"]["decision"] for c in children])}
        for mode in MODES:
            proof=propose(nn,local,mode,budget)
            if proof is not None:
                verify(nn,local,proof,budget)
                meter.kind("algebra")
                return {"kind":"algebra","proof":proof,
                        "decision":"sat" if not proof["clauses"] else "unsat"}
        if not remaining:
            meter.kind("unknown")
            return {"kind":"unknown","decision":"unknown"}
        v,parts=_split_choice(nn,local,candidates,budget)
        meter.kind("split",parts>1)
        branches=[build(_restrict(local,v,b,budget),remaining-1,level+1)
                  for b in (False,True)]
        return {"kind":"split","variable":v,"separator_parts":parts,
                "branches":branches,"decision":_merge("or",[t["decision"] for t in branches])}

    tree=build(f,depth,0)
    result={"schema":"mathos-pnp-recursive/1","normalized_n":nn,"new_to_old":mapping,
            "depth_limit":depth,"node_limit":nodes,"candidate_limit":candidates,
            "tree":tree,"decision":tree["decision"],"metrics":meter.data}
    verify_certificate(n,clauses,result,budget)
    return result


def _independent_parts(f,v,budget):
    # Connected components of the primal graph after deleting v, via DFS.
    g={}
    for c in f:
        s={abs(x) for x in c}-{v}
        for x in s:
            budget.tick(1+len(s))
            g.setdefault(x,set()).update(s-{x})
    unseen=set(g)
    count=0
    while unseen:
        count+=1
        pending=[unseen.pop()]
        while pending:
            x=pending.pop()
            budget.tick(1+len(g[x]))
            new=g[x]&unseen
            unseen.difference_update(new)
            pending.extend(new)
    return count


def verify_certificate(n,clauses,artifact,budget):
    """Recompute every branch, partition, result and structural metric."""
    nn,f,mapping=normalize(n,clauses)
    depth,nodes,candidates=(artifact[k] for k in ("depth_limit","node_limit","candidate_limit"))
    _options(depth,nodes,candidates)
    if (artifact["schema"]!="mathos-pnp-recursive/1" or
            type(artifact["normalized_n"]) is not int or artifact["normalized_n"]!=nn or
            tuple(artifact["new_to_old"])!=mapping):
        raise ValueError("invalid recursion metadata")
    meter=_Meter(nodes)

    def replay(local,t,level,previous_and=False):
        meter.enter(local,level,budget)
        kind=t["kind"]
        if kind=="empty":
            if local:
                raise ValueError("nonempty SAT terminal")
            decision="sat"
        elif kind=="conflict":
            if () not in local:
                raise ValueError("missing empty clause")
            decision="unsat"
        elif kind=="unknown":
            decision="unknown"
        elif kind=="algebra":
            verify(nn,local,t["proof"],budget)
            decision="sat" if not t["proof"]["clauses"] else "unsat"
        elif kind=="and":
            if previous_and or len(t["children"])<2:
                raise ValueError("invalid partition tree")
            used,variables=set(),set()
            outcomes=[]
            for child in t["children"]:
                ids=child["indices"]
                if (not ids or any(type(i) is not int or not 0<=i<len(local) for i in ids)
                        or len(set(ids))!=len(ids) or used.intersection(ids)):
                    raise ValueError("invalid clause partition")
                used.update(ids)
                piece=tuple(local[i] for i in ids)
                active=_active(piece)
                if variables.intersection(active):
                    raise ValueError("partition shares variables")
                variables.update(active)
                outcomes.append(replay(piece,child["tree"],level,True))
            if used!=set(range(len(local))):
                raise ValueError("partition omits clauses")
            decision="unsat" if "unsat" in outcomes else ("sat" if set(outcomes)=={"sat"} else "unknown")
        elif kind=="split":
            v=t["variable"]
            if (level>=depth or type(v) is not int or v not in _active(local)
                    or len(t["branches"])!=2):
                raise ValueError("invalid binary split")
            parts=_independent_parts(local,v,budget)
            if type(t["separator_parts"]) is not int or t["separator_parts"]!=parts:
                raise ValueError("separator metric mismatch")
            meter.kind(kind,parts>1)
            outcomes=[]
            for b,child in zip((False,True),t["branches"]):
                residual=[]
                for c in local:
                    budget.tick(1+len(c))
                    if any(abs(x)==v and (x>0)==b for x in c):
                        continue
                    residual.append(tuple(x for x in c if abs(x)!=v))
                outcomes.append(replay(tuple(residual),child,level+1))
            decision="sat" if "sat" in outcomes else ("unsat" if set(outcomes)=={"unsat"} else "unknown")
        else:
            raise ValueError("unknown tree kind")
        if kind!="split":
            meter.kind(kind)
        if t["decision"]!=decision:
            raise ValueError("node decision mismatch")
        return decision

    decision=replay(f,artifact["tree"],0)
    metrics=artifact["metrics"]
    if (decision!=artifact["decision"] or metrics!=meter.data or
            any(type(v) is not int for v in metrics.values())):
        raise ValueError("root decision or accounting mismatch")
    return True


def scope_obstruction(n,clauses,budget):
    """Greedy packing of disjoint exclusive ternary clause supports.

    Unlike v8 isolated scopes, other clauses may connect these variables.
    No other clause may contain the whole support, so fixing only outside
    variables cannot change that exact-support relation.
    """
    _,f,mapping=normalize(n,clauses)
    supports=[{abs(x) for x in c} for c in f]
    used=set()
    indices=[]
    for i,s in enumerate(supports):
        if len(s)!=3 or used&s:
            continue
        exclusive=True
        for j,t in enumerate(supports):
            budget.tick()
            if j!=i and s<=t:
                exclusive=False
                break
        if exclusive:
            indices.append(i)
            used.update(s)
    cert={"schema":"mathos-pnp-exclusive-scope/1","new_to_old":mapping,
          "clause_indices":indices,"global_backdoor_lower":len(indices)}
    verify_obstruction(n,clauses,cert,budget)
    return cert


def verify_obstruction(n,clauses,cert,budget):
    _,f,mapping=normalize(n,clauses)
    ids=cert["clause_indices"]
    if (cert["schema"]!="mathos-pnp-exclusive-scope/1" or
            tuple(cert["new_to_old"])!=mapping or
            any(type(i) is not int or not 0<=i<len(f) for i in ids) or
            len(set(ids))!=len(ids) or type(cert["global_backdoor_lower"]) is not int or
            cert["global_backdoor_lower"]!=len(ids)):
        raise ValueError("invalid exclusive scope metadata")
    used=set()
    for i in ids:
        s={abs(x) for x in f[i]}
        if len(s)!=3 or used&s:
            raise ValueError("scopes must be disjoint triples")
        used.update(s)
        for j,c in enumerate(f):
            budget.tick(1+len(c))
            if i!=j and s<={abs(x) for x in c}:
                raise ValueError("scope is not exclusive")
    return True
