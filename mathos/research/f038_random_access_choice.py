"""F038 random-access quadratic-form projection; finite regression only."""
from mathos.research.f038_monotone_choice import sat, restrict


def template(n):
    assert n >= 1
    x = tuple(range(2, n + 2))
    y = tuple(range(n + 2, 3*n + 1))
    inputs = x + y
    top = 3*n + 1
    prev = top
    fixed = [(-prev,)]

    def new():
        nonlocal top
        top += 1
        return top

    def and_gate(a, b, c):
        fixed.extend(((-a, -b, c), (a, -c), (b, -c)))

    def xor_gate(a, b, c):
        fixed.extend(((a, b, -c), (a, -b, c),
                      (-a, b, c), (-a, -b, -c)))

    for i in range(n):
        for j in range(i):
            u, v, p = new(), new(), new()
            and_gate(x[i], x[j], u)
            and_gate(u, y[i+j], v)
            xor_gate(prev, v, p)
            prev = p
    fixed.extend(((-1, prev), (1, -prev)))
    slots = tuple(fixed) + tuple(c for v in inputs for c in ((v,), (-v,)))
    assert len(set(slots)) == len(slots)
    assert all(1 <= len(c) <= 3 for c in slots)
    return top, tuple(fixed), inputs


def instantiate(t, mask):
    _, fixed, inputs = t
    bits = tuple(bool(mask & (1 << i)) for i in range(len(inputs)))
    pins = tuple((v if b else -v,) for v, b in zip(inputs, bits))
    flags = (True,)*len(fixed) + tuple(v for b in bits for v in (b, not b))
    return fixed + pins, flags


def reference(n, mask):
    x = tuple((mask >> i) & 1 for i in range(n))
    y = tuple((mask >> (n+i)) & 1 for i in range(2*n-1))
    return sum(x[i]*x[j]*y[i+j] for i in range(n) for j in range(i)) % 2


def audit():
    cases = checks = zero = one = flips = max_v = max_c = 0
    for n in range(1, 5):
        t = template(n)
        top, fixed, inputs = t
        r = n*(n-1)//2
        assert top == 3*n+1+3*r
        for mask in range(1 << len(inputs)):
            f, flags = instantiate(t, mask)
            assert len(f) == 3*n+2+10*r
            want = bool(reference(n, mask))
            a = sat(restrict(f, {1: False}))
            b = sat(restrict(f, {1: True}))
            assert (a, b) == (not want, want)
            for i in range(len(inputs)):
                _, other = instantiate(t, mask ^ (1 << i))
                changed = tuple(j for j, (u, v) in enumerate(zip(flags, other))
                                if u != v)
                assert changed == (len(fixed)+2*i, len(fixed)+2*i+1)
                flips += len(changed)
            cases += 1
            checks += 2
            zero += a
            one += b
            max_v = max(max_v, top)
            max_c = max(max_c, len(f))
    assert (cases, checks, zero, one, flips, max_v, max_c) == (
        2340, 4680, 1568, 772, 49488, 31, 74)
    print(f'F038_RANDOM_ACCESS_CHOICE_OK cases={cases} branch_checks={checks} '
          f'zero={zero} one={one} changed_coordinates={flips} '
          f'max_variables={max_v} max_clauses={max_c}')


if __name__ == '__main__':
    audit()
