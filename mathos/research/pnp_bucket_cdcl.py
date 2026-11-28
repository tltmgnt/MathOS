"""Same deterministic first-UIP search, indexed branching and monotone conflict cursor.

Adapted from frozen pnp_conflict_learning. No new inference rule,
branch preference or restart schedule. Only unassigned variables
reside in score buckets; assigned score changes are installed on undo.
"""
from collections import defaultdict
from .pnp_structural_kernel import Exhausted, validate
from .pnp_proof_library import MAX_ADDITIONS
from . import pnp_indexed_rup as indexed


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
    buckets=defaultdict(set)
    maxscore=-1
    ready=False

    def put(v):
        nonlocal maxscore
        b.tick()
        buckets[score[v]].add(v)
        maxscore=max(maxscore,score[v])

    def take(v):
        b.tick()
        buckets[score[v]].remove(v)

    def choose():
        nonlocal maxscore
        while maxscore>=0 and not buckets.get(maxscore):
            b.tick()
            maxscore-=1
        if maxscore<0:
            return None
        best=None
        for v in buckets[maxscore]:
            b.tick()
            if best is None or v<best:
                best=v
        return best

    def litval(x):
        return value[abs(x)] if x > 0 else -value[abs(x)]

    def enqueue(x, why):
        v = abs(x)
        if value[v]:
            return litval(x) == 1
        b.tick()
        if ready:
            take(v)
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
    b.cells(len(db) + sum(map(len, db)) + 7*(n+1))
    for v in sorted(active):
        if not value[v]:
            put(v)
    ready=True

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
            put(v)
        del trail[cut:]
        del limits[target:]
        qhead = min(qhead, len(trail))

    def analyze(i):
        # Every literal in the working resolvent is false on the trail.
        # Resolve the latest current-level reason until one remains.
        current = len(limits)
        out = set(db[i])
        # Each reason's other literals were false before its pivot
        # was enqueued. Thus resolution on the latest trail literal
        # introduces only earlier trail positions.
        cursor=len(trail)-1
        while sum(level[abs(x)] == current for x in out) > 1:
            pivot = None
            for j in range(cursor,-1,-1):
                b.tick()
                x=trail[j]
                if -x in out and level[abs(x)] == current:
                    pivot=x
                    cursor=j-1
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
                # All literals in the conflict resolvent are false,
                # hence their variables are currently assigned and
                # absent from the unassigned score index.
                score[abs(x)] += 4
            if target < len(limits)-1:
                jumps += 1
            backtrack(target)
            i = add(c)
            if not enqueue(c[0], i):
                raise AssertionError("learned clause did not assert")
            b.cells(len(db) + learned_literals + 7*(n+1)+len(buckets))
            conflict = None
            continue
        v=choose()
        if v is None:
            return {"decision": "sat", "certificate": [value[v] == 1 for v in range(1,n+1)],
                    "conflicts": conflicts, "nonchronological_jumps": jumps}
        limits.append(len(trail))
        enqueue(v if phase[v] else -v, None)



def attempt(n,f,total,seconds):
    return indexed.attempt(n,f,total,seconds,proposer=propose)


def profile(n,f,total,seconds):
    return indexed.profile(n,f,total,seconds,proposer=propose)
