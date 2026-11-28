"""Bounded first-UIP CDCL proposer; independent v17 RUP replay is mandatory."""
from collections import defaultdict

from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_proof_library import MAX_ADDITIONS, verify_certificate
from .pnp_hall_certificate import verify as verify_model


def verify(n, clauses, result, budget):
    decision = result["decision"]
    proof = result["certificate"]
    if decision == "sat":
        return verify_model(n, clauses, result, budget)
    if decision == "unsat":
        if not isinstance(proof, list) or not proof or proof[-1] not in ([], ()):
            raise ValueError("missing final empty addition")
        return verify_certificate(n, clauses, proof, budget)
    raise ValueError("unknown is not a proof")


def propose(n, clauses, b):
    f = validate(n, clauses)
    db, watched, watch = [], [], defaultdict(list)
    value = [0] * (n+1)
    level = [0] * (n+1)
    reason = [None] * (n+1)
    score = [0] * (n+1)
    phase = [False] * (n+1)
    trail, limits, additions = [], [], []
    active = set()
    qhead = 0
    conflicts = jumps = learned_literals = 0

    def litval(x):
        return value[abs(x)] if x > 0 else -value[abs(x)]

    def enqueue(x, why):
        v = abs(x)
        if value[v]:
            return litval(x) == 1
        b.tick()
        value[v] = 1 if x > 0 else -1
        level[v] = len(limits)
        reason[v] = why
        phase[v] = x > 0
        trail.append(x)
        return True

    def add(c):
        b.tick(1 + len(c))
        i = len(db)
        db.append(tuple(c))
        watched.append([0, 1] if len(c) >= 2 else [0, 0])
        if len(c) >= 2:
            watch[c[0]].append(i)
            watch[c[1]].append(i)
        return i

    root_conflict = None
    for raw in f:
        b.tick(1+len(raw))
        s = set(raw)
        if any(-x in s for x in s):
            continue
        c = sorted(s)
        i = add(c)
        for x in c:
            score[abs(x)] += 1
            active.add(abs(x))
        if not c or (len(c) == 1 and not enqueue(c[0], i)):
            root_conflict = i
    b.cells(len(db) + sum(map(len, db)) + 6*(n+1))

    def propagate():
        nonlocal qhead
        while qhead < len(trail):
            false = -trail[qhead]
            qhead += 1
            b.tick()
            entries = watch[false]
            k = 0
            while k < len(entries):
                b.tick()
                i = entries[k]
                c, w = db[i], watched[i]
                side = 0 if c[w[0]] == false else 1
                other = c[w[1-side]]
                if litval(other) == 1:
                    k += 1
                    continue
                replacement = None
                for j, x in enumerate(c):
                    b.tick()
                    if j not in w and litval(x) != -1:
                        replacement = j
                        break
                if replacement is not None:
                    w[side] = replacement
                    entries[k] = entries[-1]
                    entries.pop()
                    watch[c[replacement]].append(i)
                    continue
                if litval(other) == -1:
                    return i
                if not enqueue(other, i):
                    return i
                k += 1
        return None

    def backtrack(target):
        nonlocal qhead
        cut = limits[target]
        for x in reversed(trail[cut:]):
            b.tick()
            v = abs(x)
            value[v], level[v], reason[v] = 0, 0, None
        del trail[cut:]
        del limits[target:]
        qhead = min(qhead, len(trail))

    def analyze(i):
        # Every literal in the working resolvent is false on the trail.
        # Resolve the latest current-level reason until one remains.
        current = len(limits)
        out = set(db[i])
        while sum(level[abs(x)] == current for x in out) > 1:
            pivot = None
            for x in reversed(trail):
                b.tick()
                if -x in out and level[abs(x)] == current:
                    pivot = x
                    break
            if pivot is None or reason[abs(pivot)] is None:
                raise AssertionError("missing implication reason")
            c = db[reason[abs(pivot)]]
            b.tick(1+len(out)+len(c))
            if pivot not in c:
                raise AssertionError("bad implication reason")
            out.remove(-pivot)
            out.update(x for x in c if x != pivot)
            if any(litval(x) != -1 for x in out):
                raise AssertionError("non-conflict resolvent")
        current_lits = [x for x in out if level[abs(x)] == current]
        if len(current_lits) != 1:
            raise AssertionError("missing asserting literal")
        first = current_lits[0]
        rest = sorted(out-{first}, key=lambda x: (-level[abs(x)], x))
        return [first, *rest], max((level[abs(x)] for x in rest), default=0)

    conflict = root_conflict
    while True:
        b.tick()
        if conflict is None:
            conflict = propagate()
        if conflict is not None:
            conflicts += 1
            if len(additions) >= MAX_ADDITIONS:
                raise Exhausted("learned-clause cap")
            if not limits:
                additions.append([])
                return {"decision": "unsat", "certificate": additions,
                        "conflicts": conflicts, "nonchronological_jumps": jumps}
            c, target = analyze(conflict)
            learned_literals += len(c)
            if learned_literals > 99_000:
                raise Exhausted("learned-literal cap")
            additions.append(sorted(c))
            for x in c:
                score[abs(x)] += 4
            if target < len(limits)-1:
                jumps += 1
            backtrack(target)
            i = add(c)
            if not enqueue(c[0], i):
                raise AssertionError("learned clause did not assert")
            b.cells(len(db) + learned_literals + 6*(n+1))
            conflict = None
            continue
        unassigned = []
        for v in sorted(active):
            b.tick()
            if value[v] == 0:
                unassigned.append(v)
        if not unassigned:
            return {"decision": "sat", "certificate": [value[v] == 1 for v in range(1,n+1)],
                    "conflicts": conflicts, "nonchronological_jumps": jumps}
        v = max(unassigned, key=lambda v: (score[v], -v))
        limits.append(len(trail))
        enqueue(v if phase[v] else -v, None)


def attempt(n, clauses, total, seconds):
    b = Budget(seconds=seconds, max_steps=total, max_cells=200_000)
    try:
        p = propose(n, clauses, b)
        verify(n, clauses, p, b)
        return {"decision": p["decision"], "proof": p,
                "status": "replayed", "work_steps": b.steps}
    except Exhausted:
        return {"decision": "unknown", "proof": None,
                "status": "resource_exhausted", "work_steps": b.steps}


def replay(n, clauses, r, total):
    w, p = r["work_steps"], r["proof"]
    if type(w) is not int or not 0 <= w <= total:
        raise ValueError("invalid work")
    if r["status"] == "replayed":
        if p is None or p["decision"] != r["decision"]:
            raise ValueError("missing decision certificate")
        for k in ("conflicts", "nonchronological_jumps"):
            if type(p[k]) is not int or p[k] < 0:
                raise ValueError("invalid observed statistic")
        if p["nonchronological_jumps"] > p["conflicts"]:
            raise ValueError("invalid jump statistic")
        verify(n, clauses, p, Budget(seconds=15, max_steps=4_000_000, max_cells=200_000))
    elif r["status"] != "resource_exhausted" or p is not None or r["decision"] != "unknown":
        raise ValueError("invalid exhausted result")
    return True
