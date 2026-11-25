"""Parity CNF projection stress; no general algorithm lower bound."""
from itertools import product

def xor_rows(a, b, c):
    # c = a xor b, block the four violating assignments.
    return {frozenset(v if not bit else -v for v, bit in zip((a,b,c), bits))
            for bits in product((False,True), repeat=3)
            if bits[2] != (bits[0] ^ bits[1])}

def chain(k):
    # x_1..x_k, z_0..z_k; z_0=z_k=0.
    z = list(range(k+1, 2*k+2))
    rows = {frozenset({-z[0]}), frozenset({-z[-1]})}
    for i in range(k):
        rows.update(xor_rows(z[i], i+1, z[i+1]))
    return rows, z

def eliminate(rows, v):
    pos = [c-{v} for c in rows if v in c]
    neg = [c-{-v} for c in rows if -v in c]
    out = {c for c in rows if v not in c and -v not in c}
    for a in pos:
        for b in neg:
            c = a | b
            if not any(-l in c for l in c):
                out.add(c)
    return out

def verify(k):
    rows, aux = chain(k)
    original = len(rows)
    assert original == 4*k+2
    for v in aux:
        rows = eliminate(rows,v)
    assert len(rows) == 2**(k-1)
    assert all(len(c)==k and {abs(l) for l in c}==set(range(1,k+1))
               for c in rows)
    # Each clause is false on exactly one odd-parity assignment.
    blocked = {tuple(-i in c for i in range(1,k+1)) for c in rows}
    assert blocked == {bits for bits in product((False,True),repeat=k)
                       if sum(bits)%2}
    return original,len(rows)

if __name__=="__main__":
    for k in range(1,13):
        print(k,*verify(k))
    print("F035_PARITY_PROJECTION_STRESS_OK k=1..12")
