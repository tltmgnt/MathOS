"""F036: exact adaptive probing + static GF(2) lifting experiment.

No claim of asymptotic lower bounds or polynomial-calculus completeness.
The minimax recurrence explores all available choices of split variable.
Unit propagation is free in the depth measure, not in a runtime measure.
"""
from functools import lru_cache
from itertools import combinations, product

N = 12
F = tuple([tuple((3*i+j+1, True) for j in range(3)) for i in range(4)] +
          [((3*i+j+1, False),(3*k+j+1, False))
           for j in range(3) for i,k in combinations(range(4),2)])

@lru_cache(None)
def propagate(mask, value):
    while True:
        units = ones = 0
        residual = []
        for c in F:
            r = []
            for v,b in c:
                bit = 1 << (v-1)
                if mask & bit:
                    if bool(value & bit) == b:
                        break
                else:
                    r.append((v,b))
            else:
                if not r:
                    return None
                if len(r) == 1:
                    v,b = r[0]
                    bit = 1 << (v-1)
                    if units & bit and bool(ones & bit) != b:
                        return None
                    units |= bit
                    if b:
                        ones |= bit
                residual.append(tuple(r))
        if not units:
            return mask, value, tuple(residual)
        mask |= units
        value |= ones

def polynomial(c):
    p = {0}
    for v,b in c:
        q = set()
        for m in p:
            q.symmetric_difference_update({m | (1 << (v-1))})
            if b:
                q.symmetric_difference_update({m})
        p = q
    return p

@lru_cache(None)
def refutes(state, d):
    if state is None:
        return True
    mask, _, g = state
    mons = [m for m in range(1 << N)
            if not m & mask and m.bit_count() <= d]
    index = {m:i for i,m in enumerate(mons)}
    basis = {}
    for c in g:
        p = polynomial(c)
        for m in mons:
            q = set()
            for a in p:
                q.symmetric_difference_update({a | m})
            if any(t.bit_count() > d for t in q):
                continue
            r = sum(1 << index[t] for t in q)
            while r:
                if r == 1:
                    return True
                k = r.bit_length()-1
                if k not in basis:
                    basis[k] = r
                    break
                r ^= basis[k]
    return False

@lru_cache(None)
def win(state, degree, depth):
    if refutes(state, degree):
        return True
    if depth == 0:
        return False
    mask, value, _ = state
    for v in range(N):
        bit = 1 << v
        if mask & bit:
            continue
        if (win(propagate(mask|bit, value), degree, depth-1)
            and win(propagate(mask|bit, value|bit), degree, depth-1)):
            return True
    return False

def run():
    assert len(F) == 22
    assert not any(all(any(x[v-1] == b for v,b in c) for c in F)
                   for x in product((False,True), repeat=N))
    root = propagate(0,0)
    expected = {2:3,3:3,4:2,5:1}
    for d,minimum in expected.items():
        results = [win(root,d,k) for k in range(minimum+1)]
        assert results == [False]*minimum+[True], (d,results)
        # No symmetry assumption: exhaustively check all root choices.
        if minimum > 0:
            for v in range(N):
                bit = 1 << v
                if minimum >= 2:
                    assert not (win(propagate(bit,0),d,minimum-2)
                                and win(propagate(bit,bit),d,minimum-2))
        print(f"degree={d} minimum_depth={minimum}")
    print("F036_PROBING_LIFT_OK degrees=4 min_depths=3,3,2,1")

if __name__ == "__main__":
    run()
