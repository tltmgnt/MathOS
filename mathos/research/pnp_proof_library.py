"""Bounded propositional proof library. Search is untrusted; replay is mandatory."""
from collections import defaultdict
from itertools import permutations, product
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_proof_abstraction import verify_template, _original_clauses

MAX_ADDITIONS = 4096
MAX_TEMPLATES = 128


def clause(xs):
    return tuple(sorted(set(xs)))


def mapped(c, e):
    return clause(e[abs(x)-1] if x > 0 else -e[abs(x)-1] for x in c)


def variables(cs):
    return sorted({abs(x) for c in cs for x in c})


def rup(known, c, budget):
    """Independent reverse unit propagation, not the template search algorithm."""
    assigned = {-x for x in c}
    if any(-x in assigned for x in assigned):
        return True
    while True:
        changed = False
        for a in known:
            budget.tick(1 + len(a))
            if any(x in assigned for x in a):
                continue
            live = [x for x in a if -x not in assigned]
            if not live:
                return True
            if len(live) == 1:
                assigned.add(live[0])
                changed = True
        if not changed:
            return False


def verify_certificate(n, formula, additions, budget, *, contradiction=True):
    """Replay explicit RUP additions against original input, never an index."""
    known = sorted(_original_clauses(n, formula))
    raw = validate(n, additions)
    if len(raw) > MAX_ADDITIONS:
        raise Exhausted("certificate addition cap")
    for c in raw:
        if c != clause(c) or any(-x in c for x in c):
            raise ValueError("noncanonical or tautological addition")
        if not rup(known, c, budget):
            raise ValueError("addition is not RUP")
        known.append(c)
        budget.cells(len(known))
    if contradiction and () not in known:
        raise ValueError("no empty clause")
    return True


def fragments(t, budget):
    """Extract exact dependency cones of independently checked v15 proofs."""
    ax = verify_template(t, budget)
    known = list(ax)
    parents = {}
    for p, q, v in t["steps"]:
        parents[len(known)] = (p, q, v)
        known.append(clause((set(known[p])-{v}) | (set(known[q])-{-v})))
    for root in sorted(parents):
        todo, used = [root], set()
        while todo:
            i = todo.pop()
            budget.tick()
            if i not in used:
                used.add(i)
                if i in parents:
                    todo.extend(parents[i][:2])
        ids = sorted(used & parents.keys())
        if len(ids) < 2 and root != t["root"]:
            continue
        premises = [known[i] for i in sorted(used - parents.keys())]
        steps = [known[i] for i in ids]
        vs = variables(premises)
        if len(vs) > 9 or len(ids) > 64:
            continue
        label = {v: i+1 for i, v in enumerate(vs)}
        def rename(c):
            return clause(label[abs(x)] if x > 0 else -label[abs(x)] for x in c)
        f = {"n": len(vs), "axioms": tuple(sorted(map(rename, premises))),
             "steps": tuple(map(rename, steps)),
             "edges": tuple((rename(known[parents[i][0]]),
                             rename(known[parents[i][1]]), rename(known[i]),
                             label[parents[i][2]]) for i in ids)}
        verify_certificate(f["n"], f["axioms"], f["steps"], budget, contradiction=False)
        yield f
    if t["root"] < len(ax):  # an explicit empty input clause
        yield {"n": 0, "axioms": ((),), "steps": ((),), "edges": ()}


def canonical_structure(f, budget):
    """Exact signed-isomorphism canonical form for small resolution DAGs.
    Larger patterns use a labelled key, not a claimed isomorphism test.
    """
    n = f["n"]
    def key(e):
        edges = tuple(sorted((min(mapped(a,e), mapped(b,e)),
                              max(mapped(a,e), mapped(b,e)), mapped(c,e),
                              abs(e[v-1])) for a,b,c,v in f["edges"]))
        return (tuple(sorted(mapped(c,e) for c in f["axioms"])),
                mapped(f["steps"][-1],e), edges,
                tuple(sorted(mapped(c,e) for c in f["steps"])))
    if n > 4:
        return ("labelled", n, key(tuple(range(1,n+1))))
    best = None
    for p in permutations(range(1,n+1)):
        for signs in product((-1,1), repeat=n):
            budget.tick(1 + len(f["axioms"]) + len(f["steps"]))
            k = key(tuple(x*s for x,s in zip(p,signs)))
            if best is None or k < best:
                best = k
    return ("signed-orbit", n, best)


def counterexample(n, premises, goal, budget):
    """Return a complete signed assignment satisfying premises and falsifying goal."""
    for bits in product((-1,1), repeat=n):
        budget.tick(1 + sum(map(len,premises)) + len(goal))
        model = {i*s for i,s in enumerate(bits,1)}
        if all(model.intersection(c) for c in premises) and not model.intersection(goal):
            return tuple(sorted(model))
    return None


def refine(f, budget):
    """CEGAR on premise deletion: retain counterexample witnesses.
    Only accept a weakened guard when the full derivation independently replays.
    Deletion minimality is not claimed when replay blocks a deletion.
    """
    ax = list(f["axioms"])
    evidence = []
    for c in tuple(ax):
        trial = [a for a in ax if a != c]
        witness = counterexample(f["n"], trial, f["steps"][-1], budget)
        if witness is not None:
            evidence.append({"removed": c, "status": "counterexample", "model": witness,
                             "candidate_axioms": trial})
            continue
        try:
            verify_certificate(f["n"], trial, f["steps"], budget, contradiction=False)
        except ValueError:
            evidence.append({"removed": c, "status": "replay_blocked"})
            continue
        ax = trial
        evidence.append({"removed": c, "status": "verified_deletion"})
    # Edges refer to original source proof; retain them only for unchanged guards.
    return {**f, "axioms": tuple(ax), "edges": f["edges"] if tuple(ax)==f["axioms"] else ()}, evidence


def build(templates, budget):
    """Freeze a bounded library; deduplicate by exact small signed orbit."""
    candidates = []
    for t in templates:
        candidates.extend(fragments(t,budget))
    candidates.sort(key=lambda f: (f["steps"][-1] != (), len(f["axioms"]),
                                   f["n"], -len(f["steps"]), f["axioms"]))
    out, seen, refinement = [], set(), []
    for f in candidates:
        if len(out) >= MAX_TEMPLATES:
            break
        # Refine full contradiction guards only; retain proof DAGs for fragments.
        if f["steps"][-1] == () and f["n"] <= 7:
            f, evidence = refine(f,budget)
        else:
            evidence = []
        key = canonical_structure(f,budget)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
        refinement.append(evidence)
    return tuple(out), refinement


def find(f, n, known, budget, *, subsumption=True, limit=4096):
    """Clause-driven signed injection search. All leaves are checked by replay.
    A target premise may be stronger (a subset), never a superset.
    """
    vs = variables(known)
    if len(vs) < f["n"]:
        return None
    by_width = defaultdict(list)
    for c in sorted(known):
        by_width[len(c)].append(c)
    options = [(a, tuple(c for w in sorted(by_width) if
                        (w <= len(a) if subsumption else w == len(a))
                        for c in by_width[w])) for a in f["axioms"]]
    options.sort(key=lambda pair: (len(pair[1]), -len(pair[0]), pair[0]))
    attempts = 0
    goal = f["steps"][-1]
    def tick():
        nonlocal attempts
        attempts += 1
        budget.tick()
        return attempts <= limit
    def finish(d, used):
        missing = [v for v in range(1,f["n"]+1) if v not in d]
        if not missing:
            e = tuple(d[v] for v in range(1,f["n"]+1))
            return e if mapped(goal,e) not in known else None
        v = missing[0]
        for u in vs:
            if u in used:
                continue
            for x in (u,-u):
                if not tick():
                    return None
                answer = finish({**d,v:x},used|{u})
                if answer is not None:
                    return answer
        return None
    def visit(i,d,used):
        if attempts >= limit:
            return None
        if i == len(options):
            return finish(d,used)
        a, choices = options[i]
        fixed = {d[abs(x)] if x>0 else -d[abs(x)] for x in a if abs(x) in d}
        free = [x for x in a if abs(x) not in d]
        for c in choices:
            if not tick():
                return None
            remaining = sorted(set(c)-fixed)
            if len(remaining)>len(free) or any(abs(x) in used for x in remaining):
                continue
            for lits in permutations(free,len(remaining)):
                if not tick():
                    return None
                add = {abs(x): y if x>0 else -y for x,y in zip(lits,remaining)}
                result = visit(i+1,{**d,**add},used|{abs(y) for y in remaining})
                if result is not None:
                    return result
        return None
    return visit(0,{},set())


class Index:
    """Width postings, a necessary filter for subsumption, not a proof oracle."""
    def __init__(self, templates):
        self.templates = tuple(templates)
        self.postings = defaultdict(list)
        for i,f in enumerate(self.templates):
            self.postings[min(map(len,f["axioms"]),default=512)].append(i)

    def retrieve(self, known):
        width = min(map(len,known),default=513)
        return sorted(i for w, ids in self.postings.items() if w >= width for i in ids)


def reconstruct(n, formula, index, transfers, budget):
    """Verify each signed guard, each fragment, then the whole composed proof."""
    known = set(_original_clauses(n,formula))
    additions = []
    for i,e in transfers:
        if type(i) is not int or not 0<=i<len(index.templates):
            raise ValueError("invalid template id")
        f = index.templates[i]
        if (len(e)!=f["n"] or any(type(x) is not int or not 0<abs(x)<=n for x in e)
                or len({abs(x) for x in e})!=len(e)):
            raise ValueError("invalid signed injection")
        for a in f["axioms"]:
            ma = set(mapped(a,e))
            if not any(set(c)<=ma for c in known):
                raise ValueError("missing stronger premise")
        part = [mapped(c,e) for c in f["steps"]]
        verify_certificate(n,sorted(known),part,budget,contradiction=False)
        additions.extend(part)
        known.update(part)
    verify_certificate(n,formula,additions,budget)
    return additions


def reuse(n, formula, index, budget, *, rounds=4, max_transfers=32, compose=True,
          subsumption=True, shared_replay=False):
    """Unknown on exhaustion or miss. No fallback solver is credited as reuse."""
    known = set(_original_clauses(n,formula))
    transfers = []
    examined = 0
    try:
        for _ in range(rounds):
            changed = False
            for i in index.retrieve(known):
                f = index.templates[i]
                if not compose and f["steps"][-1] != ():
                    continue
                examined += 1
                e = find(f,n,known,budget,subsumption=subsumption)
                if e is None:
                    continue
                part = [mapped(c,e) for c in f["steps"]]
                verify_certificate(n,sorted(known),part,budget,contradiction=False)
                transfers.append((i,e))
                known.update(part)
                changed = True
                if () in known:
                    proof = reconstruct(n,formula,index,transfers,
                                        budget if shared_replay else Budget(seconds=10,max_steps=4_000_000))
                    return {"status":"verified","transfers":transfers,"proof":proof,
                            "examined":examined}
                if len(transfers)>=max_transfers:
                    return {"status":"transfer_limit","examined":examined}
            if not changed:
                break
    except Exhausted:
        return {"status":"resource_exhausted","examined":examined}
    return {"status":"not_found","examined":examined}
