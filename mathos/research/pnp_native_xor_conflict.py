"""Native Gaussian explanations in a bounded watched-literal CDCL search.

No auxiliary XOR gate variables. Search is untrusted: check source rows,
XOR explanation clauses and ordinary RUP additions in chronological order.
The watched search is adapted from the frozen pnp_conflict_learning module.
"""
from collections import defaultdict
from .pnp_structural_kernel import Budget, Exhausted, validate
from .pnp_proof_library import MAX_ADDITIONS, rup
from .pnp_proof_abstraction import _original_clauses
from .pnp_hall_certificate import verify as verify_model
from .pnp_affine_projected import _row_witness, MAX_ROWS
from .pnp_xor_subsystem import extract

MAX_LITERALS = 99_000


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()
        mask ^= bit


def row_masks(rows):
    return [(sum(1 << (v-1) for v in r["scope"]),r["rhs"]) for r in rows]


def scan(masks,trail,b):
    """Recompute elimination under the current assignment; return conflict
    or a batch of forced literals, with full-row provenance. No trail state
    is retained across backtracking.
    """
    assigned = true = 0
    for x in trail:
        b.tick()
        bit=1<<(abs(x)-1)
        assigned |= bit
        if x>0:
            true |= bit
    basis={}
    def explanation(m,rhs,prov,lit):
        b.tick(1+m.bit_count()+prov.bit_count())
        clause=[]
        for v in indices(m):
            if lit is not None and v==abs(lit):
                clause.append(lit)
            else:
                clause.append(-v if true>>(v-1)&1 else v)
        return {"kind":"xor","clause":sorted(clause),
                "rows":[j-1 for j in indices(prov)]},lit
    for i,(full,rhs) in enumerate(masks):
        b.tick()
        m=full & ~assigned
        r=rhs ^ ((full & true).bit_count()%2)
        prov=1<<i
        while m:
            p=m.bit_length()
            b.tick()
            if p not in basis:
                basis[p]=(m,r,full,prov)
                break
            q,s,t,u=basis[p]
            m,r,full,prov=m^q,r^s,full^t,prov^u
        if not m and r:
            return [explanation(full,r,prov,None)]
    # Reduced row echelon form exposes all unit consequences of the
    # affine subsystem under the current trail.
    pivots=sum(1<<(p-1) for p in basis)
    out=[]
    for p,(m,r,full,prov) in sorted(basis.items()):
        b.tick()
        for v in indices((m & pivots) ^ (1<<(p-1))):
            b.tick()
            q,s,t,u=basis[v]
            m,r,full,prov=m^q,r^s,full^t,prov^u
        basis[p]=(m,r,full,prov)
        if m.bit_count()==1:
            out.append(explanation(full,r,prov,p if r else -p))
    return out


def verify_explanation(n,rows,event,b):
    raw=event["clause"]
    c=validate(n,[raw])[0]
    ids=event["rows"]
    if (list(c)!=sorted(set(c)) or len({abs(x) for x in c})!=len(c)
            or not isinstance(ids,list) or not ids
            or any(type(i) is not int or not 0<=i<len(rows) for i in ids)
            or ids!=sorted(set(ids))):
        raise ValueError("invalid XOR explanation")
    vs=set()
    rhs=0
    for i in ids:
        r=rows[i]
        b.tick(1+len(r["scope"]))
        vs.symmetric_difference_update(r["scope"])
        rhs ^= r["rhs"]
    # Exactly one literal per variable. The assignment falsifying the
    # clause must violate the implied equation. This is a semantic check,
    # independent of the Gaussian search and of the original trail.
    b.tick(1+len(c))
    if vs!={abs(x) for x in c} or sum(x<0 for x in c)%2==rhs:
        raise ValueError("explanation not implied by equation")
    return c


def verify(n,clauses,result,b):
    f=validate(n,clauses)
    if result["decision"]=="sat":
        return verify_model(n,f,result,b)
    if result["decision"]!="unsat":
        raise ValueError("unknown is not a proof")
    p=result["certificate"]
    rows,events=p["rows"],p["events"]
    if (not isinstance(rows,list) or not 1<=len(rows)<=MAX_ROWS
            or not isinstance(events,list) or not 1<=len(events)<=MAX_ADDITIONS
            or events[-1]!={"kind":"rup","clause":[]}):
        raise ValueError("invalid mixed certificate")
    for row in rows:
        _row_witness(n,f,row,b)
    known=sorted(_original_clauses(n,f))
    literals=0
    for event in events:
        if event["kind"]=="xor":
            c=verify_explanation(n,rows,event,b)
        elif event["kind"]=="rup":
            c=validate(n,[event["clause"]])[0]
            if list(c)!=sorted(set(c)) or any(-x in c for x in c):
                raise ValueError("invalid RUP addition")
            if not rup(known,c,b):
                raise ValueError("addition is not RUP")
        else:
            raise ValueError("unknown proof event")
        literals+=len(c)
        if literals>MAX_LITERALS:
            raise Exhausted("certificate literal cap")
        known.append(c)
        b.cells(len(known)+literals)
    return True


def propose(n, clauses, b, *, state_factory=None):
    f = validate(n, clauses)
    rows=extract(f,b)
    if not rows:
        return None
    if len(rows)>MAX_ROWS:
        raise Exhausted("source row cap")
    masks=row_masks(rows)
    b.cells(max(1,len(rows))*(min(n,len(rows))+1))
    state=state_factory(masks,b) if state_factory is not None else None
    explanation_cache={}
    xor_events=xor_units=xor_conflicts=scans=0
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

    def add(c, attach=True):
        b.tick(1 + len(c))
        i = len(db)
        db.append(tuple(c))
        watched.append([0, 1] if len(c) >= 2 else [0, 0])
        if attach and len(c) >= 2:
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

    def record(event):
        nonlocal learned_literals
        if len(additions)>=MAX_ADDITIONS:
            raise Exhausted("proof event cap")
        learned_literals+=len(event["clause"])
        if learned_literals>MAX_LITERALS:
            raise Exhausted("proof literal cap")
        b.tick(1+len(event["clause"]))
        additions.append(event)

    def native():
        nonlocal xor_events,xor_units,xor_conflicts,scans
        scans+=1
        inferred=scan(masks,trail,b) if state is None else state.sync(trail,b)
        for event,lit in inferred:
            key=tuple(event["clause"])
            if key not in explanation_cache:
                record(event)
                xor_events+=1
                # A native reason is not attached to the watch lists:
                # after backtracking it is rediscovered by elimination.
                # RUP replay retains the globally valid reason clause.
                explanation_cache[key]=add(key,attach=False)
                b.cells(len(db)+learned_literals+6*(n+1))
            i=explanation_cache[key]
            if lit is None:
                xor_conflicts+=1
                return i,False
            if not enqueue(lit,i):
                raise AssertionError("inconsistent Gaussian unit batch")
            xor_units+=1
        return None,bool(inferred)

    def stats():
        return {"conflicts":conflicts,"nonchronological_jumps":jumps,
                "xor_events":xor_events,"xor_units":xor_units,
                "xor_conflicts":xor_conflicts,"gaussian_scans":scans}

    conflict = root_conflict
    while True:
        b.tick()
        if conflict is None:
            conflict = propagate()
        if conflict is None:
            conflict,changed=native()
            if changed:
                continue
        if conflict is not None:
            conflicts += 1
            if len(additions) >= MAX_ADDITIONS:
                raise Exhausted("learned-clause cap")
            if not limits:
                record({"kind":"rup","clause":[]})
                return {"decision":"unsat",
                        "certificate":{"rows":rows,"events":additions},**stats()}
            c, target = analyze(conflict)
            record({"kind":"rup","clause":sorted(c)})
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
                    **stats()}
        v = max(unassigned, key=lambda v: (score[v], -v))
        limits.append(len(trail))
        enqueue(v if phase[v] else -v, None)


def attempt(n, clauses, total, seconds, *, state_factory=None, transform=None):
    b = Budget(seconds=seconds, max_steps=total, max_cells=200_000)
    try:
        p = propose(n, clauses, b, state_factory=state_factory)
        if p is None:
            return {"decision":"unknown","proof":None,
                    "status":"unrecognized","work_steps":b.steps}
        if transform is not None:
            p=transform(p,b)
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
        for k in ("conflicts","nonchronological_jumps","xor_events","xor_units","xor_conflicts","gaussian_scans"):
            if type(p[k]) is not int or p[k] < 0:
                raise ValueError("invalid observed statistic")
        if p["nonchronological_jumps"] > p["conflicts"]:
            raise ValueError("invalid jump statistic")
        verify(n, clauses, p, Budget(seconds=15, max_steps=4_000_000, max_cells=200_000))
        if p["decision"]=="unsat" and p["xor_events"]!=sum(e["kind"]=="xor" for e in p["certificate"]["events"]):
            raise ValueError("explanation count mismatch")
    elif r["status"] not in ("resource_exhausted","unrecognized") or p is not None or r["decision"] != "unknown":
        raise ValueError("invalid exhausted result")
    return True
