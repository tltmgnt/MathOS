"""Indirect storage access selector encoding and finite subfunction regression."""
from mathos.research.f038_monotone_choice import sat, restrict


def parameters(k):
    assert k >= 1
    d = 1 << k
    r = k - (k-1).bit_length()
    b = 1 << r
    return d, r, b, r+k*b+d


def template(k):
    d, r, b, n = parameters(k)
    top = n+1
    fixed = []

    def gate(a, b, is_or):
        nonlocal top
        top += 1
        c = top
        if is_or:
            fixed.extend(((a, b, -c), (-a, c), (-b, c)))
        else:
            fixed.extend(((-a, -b, c), (a, -c), (b, -c)))
        return c

    def select(vals, addr):
        assert len(vals) == 1 << len(addr)
        for s in addr:
            vals = [gate(gate(-s, vals[i], False),
                         gate(s, vals[i+1], False), True)
                    for i in range(0, len(vals), 2)]
        return vals[0]

    a = tuple(range(2, r+2))
    p = tuple(select([2+r+i*k+j for i in range(b)], a)
              for j in range(k))
    out = select(list(range(2+r+k*b, n+2)), p)
    g = 3*(k*(b-1)+d-1)
    assert top == n+g+1
    fixed.extend(((-1, out), (1, -out)))
    assert len(fixed) == 3*g+2
    slots = tuple(fixed) + tuple(c for v in range(2,n+2)
                                 for c in ((v,), (-v,)))
    assert len(slots) == len(set(slots))
    assert all(1 <= len(c) <= 3 for c in slots)
    return top, tuple(fixed), n


def instantiate(t, mask):
    _, fixed, n = t
    bits = tuple(bool(mask & (1 << i)) for i in range(n))
    pins = tuple((v if b else -v,) for v,b in enumerate(bits,2))
    flags = (True,)*len(fixed) + tuple(v for b in bits for v in (b,not b))
    return fixed+pins, flags


def reference(k, mask):
    d,r,b,_ = parameters(k)
    a = mask & (b-1)
    p = (mask >> (r+k*a)) & (d-1)
    return bool(mask & (1 << (r+k*b+p)))


def audit():
    cases = checks = zero = one = signatures = max_v = max_c = 0
    for k in range(1,4):
        d,r,b,n = parameters(k)
        t = template(k)
        top,fixed,_ = t
        _, base = instantiate(t,0)
        for i in range(n):
            _, other = instantiate(t,1<<i)
            assert tuple(j for j,(u,v) in enumerate(zip(base,other))
                         if u!=v) == (len(fixed)+2*i,len(fixed)+2*i+1)
        for mask in range(1<<n):
            f,flags = instantiate(t,mask)
            assert flags[:len(fixed)] == (True,)*len(fixed)
            assert all(flags[len(fixed)+2*i] == bool(mask & (1<<i))
                       and flags[len(fixed)+2*i+1] != bool(mask & (1<<i))
                       for i in range(n))
            want = reference(k,mask)
            z0 = sat(restrict(f,{1:False}))
            z1 = sat(restrict(f,{1:True}))
            assert (z0,z1) == (not want,want)
            cases += 1
            checks += 2
            zero += z0
            one += z1
            max_v = max(max_v,top)
            max_c = max(max_c,len(f))
        for a in range(b):
            seen = set()
            for data in range(1<<d):
                s = tuple(reference(k,a | (p << (r+k*a)) |
                                    (data << (r+k*b))) for p in range(d))
                assert s not in seen
                seen.add(s)
            assert len(seen) == 1<<d
            signatures += len(seen)
    assert (cases,checks,zero,one,signatures,max_v,max_c) == (
        33312,66624,16656,16656,552,46,107)
    print(f'F038_UNRESTRICTED_READ_OK cases={cases} branch_checks={checks} '
          f'zero={zero} one={one} signatures={signatures} '
          f'max_variables={max_v} max_clauses={max_c}')


if __name__ == '__main__':
    audit()
