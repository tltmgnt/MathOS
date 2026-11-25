"""Exact residual-cache stress case, not a general SAT lower bound."""
from itertools import product

def family(k):
    # Selectors 1..k, common hub 3k+1, two leaves per selector.
    h = 3*k+1
    f = []
    for i in range(1, k+1):
        f.extend([(i, k+2*i-1, h), (-i, k+2*i, h)])
    f.append((h, h+1, h+2))
    return tuple(f), h

def restrict(f, v, b):
    good = v if b else -v
    return tuple(tuple(l for l in c if l != -good) for c in f if good not in c)

def canonical(f):
    return tuple(sorted(set(tuple(sorted(set(c))) for c in f)))

def connected(f):
    supports = [set(map(abs, c)) for c in f]
    if not supports:
        return True
    reached = set(supports[0])
    pending = supports[1:]
    while pending:
        rest = [s for s in pending if reached.isdisjoint(s)]
        if len(rest) == len(pending):
            return False
        for s in pending:
            if not reached.isdisjoint(s):
                reached.update(s)
        pending = rest
    return True

def run(k):
    f, h = family(k)
    states = {canonical(f)}
    for i in range(1, k+1):
        states = {canonical(restrict(r, i, b)) for r in states for b in (False, True)}
        assert len(states) == 2**i
        assert all(connected(r) for r in states)
        assert all(any(len(c)>2 for c in r) for r in states)
        assert all(all(h in c for c in r) for r in states)
    return len(states)

if __name__ == "__main__":
    for k in range(1, 13):
        print(k, run(k))
    print("F035_RESIDUAL_CACHE_STRESS_OK k=1..12")
