"""ResearchOS TECT-X: reproducible finite checks for a rank>=3 elliptic family.

The *mathematical* proof uses these exact mod-3, mod-11, mod-23
computations plus the general facts about good reduction, Mordell-Weil,
and the duplication formula. This program does NOT compute or bound the
2-Selmer group, and is NOT a BSD certificate.
"""
from fractions import Fraction

PRIMES = (3, 11, 23)
MODULUS = 3 * 11 * 23  # 759


def ab(n):
    d = 27 - n * n
    assert d != 0
    a = Fraction(n * n + 27, d)
    b = Fraction(6 * n, d)
    assert a * a - 3 * b * b == 1
    return a, b


def red(r, p):
    r = Fraction(r)
    assert r.denominator % p != 0, (r, p)
    return (r.numerator * pow(r.denominator, -1, p)) % p


def add(pnt, qnt, p, a_coefficient):
    if pnt is None:
        return qnt
    if qnt is None:
        return pnt
    x1, y1 = pnt
    x2, y2 = qnt
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if pnt == qnt:
        slope = ((3 * x1 * x1 + a_coefficient) * pow(2 * y1, -1, p)) % p
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, p)) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def oncurve(pt, a, b, p):
    if pt is None:
        return True
    x, y = pt
    return (y * y - (x ** 3 - a * a * x + b * b)) % p == 0


def verify():
    assert MODULUS == 759
    # Every n=5+759k is congruent to 5 at all three primes.
    a0, b0 = ab(5)
    assert (a0, b0) == (26, 15)
    for k in range(4):
        a, b = ab(5 + MODULUS * k)
        for p in PRIMES:
            assert (red(a, p), red(b, p)) == (26 % p, 15 % p)

    # p=11: the 2-division cubic has no root, hence no rational 2-torsion.
    p = 11
    assert [x for x in range(p) if (x ** 3 - 26 ** 2 * x + 15 ** 2) % p == 0] == []

    # p=3: E(F_3) has four points, all of order 2.
    p = 3
    a, b = 26 % p, 15 % p
    points = [None] + [(x, y) for x in range(p) for y in range(p)
                       if oncurve((x, y), a, b, p)]
    assert set(points) == {None, (0, 0), (1, 0), (2, 0)}
    P = (0, b)
    Q = (a, b)
    R = (-1 % p, 2 * b % p)
    assert P == (0, 0) and Q == R == (2, 0)
    assert all(add(pt, pt, p, -(a * a) % p) is None for pt in points)

    # p=23: Q+R=(2,10), with (x-4)=-2 a nonsquare.
    p = 23
    a, b = 26 % p, 15 % p
    Q, R = (a, b), (-1 % p, 2 * b % p)
    assert oncurve(Q, a, b, p) and oncurve(R, a, b, p)
    S = add(Q, R, p, -(a * a) % p)
    assert S == (2, 10)
    assert oncurve(S, a, b, p)
    assert all((r ** 3 - a * a * r + b * b) % p != 0 for r in range(p) if r != 4)
    assert (4 ** 3 - a * a * 4 + b * b) % p == 0
    assert pow((-2) % p, (p - 1) // 2, p) == p - 1

    # Stronger finite check: S is not a double of any F_23 point.
    points23 = [None] + [(x, y) for x in range(p) for y in range(p)
                         if oncurve((x, y), a, b, p)]
    assert len(points23) == 20
    double_points = {add(T, T, p, -(a * a) % p) for T in points23}
    assert S not in double_points

    print('PASS: n=5+759k gives 3 independent point classes modulo 2.')
    print('PASS: the 2-division cubic has no rational root (p=11).')
    print('PASS: reductions at p=3 and p=23 certify rank >= 3.')
    print('NOT CHECKED: any global 2-Selmer upper bound or analytic rank.')


if __name__ == '__main__':
    verify()