"""ResearchOS TECT-X: exact certificate that E_5 has Mordell--Weil rank >= 4.

No Sage, Magma, external data, or unproved analytic hypothesis is required.
The proof checks reduction modulo good primes 3, 5, 23, with torsion
excluded modulo 11.  Run: python tect_x_rank4_fiber_certificate.py
"""
from math import isqrt

A, B = -676, 225
POINTS = ((0, 15), (26, 15), (-1, 30), (-18, 81))
DELTA = -16 * (4 * A**3 + 27 * B**2)


def add(P, Q, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    z, w = Q
    if x == z and (y + w) % p == 0:
        return None
    if x == z:
        assert y % p
        m = ((3*x*x + A) * pow(2*y % p, -1, p)) % p
    else:
        m = ((w-y) * pow((z-x) % p, -1, p)) % p
    u = (m*m - x - z) % p
    return (u, (m*(x-u)-y) % p)


def finite_points(p):
    return [None] + [(x, y) for x in range(p) for y in range(p)
                     if (y*y - x*x*x - A*x - B) % p == 0]


def twoE(p):
    return {add(P, P, p) for P in finite_points(p)}


def binary_combination(mask, p):
    S = None
    for i, (x, y) in enumerate(POINTS):
        if (mask >> i) & 1:
            S = add(S, (x % p, y % p), p)
    return S


def main():
    assert DELTA == 19748739664
    assert all(y*y == x*x*x + A*x + B for x, y in POINTS)
    print('E_5: y^2 = x^3 - 676*x + 225')
    print('Four rational points:', POINTS)
    print('Discriminant:', DELTA)

    # The equation x^3 - 676 x + 225 = 0 has no root modulo 11.
    assert DELTA % 11
    roots11 = [x for x in range(11) if (x**3 + A*x + B) % 11 == 0]
    assert not roots11
    print('E_5(Q)[2] = 0: 2-division cubic rootless modulo 11')

    live = set(range(1, 16))
    for p, expected in ((3, {6, 9, 15}), (5, {6}), (23, set())):
        assert DELTA % p  # good reduction; group homomorphism exists
        doubles = twoE(p)
        order = len(finite_points(p))
        live = {mask for mask in live if binary_combination(mask, p) in doubles}
        assert live == expected, (p, live, expected)
        print(f'p={p}: #E(F_p)={order}, [E(F_p):2E(F_p)]={order//len(doubles)}, '
              f'candidate relation masks remaining={sorted(live)}')

    # More human-readable final obstruction at p=23:
    qr = binary_combination(6, 23)
    assert qr == (2, 10)
    assert 4**3 + A*4 + B == 0 or (4**3 + A*4 + B) % 23 == 0
    nonzero_squares = {x*x % 23 for x in range(1, 23)}
    assert (qr[0] - 4) % 23 not in nonzero_squares
    print('p=23: Q+R=(2,10); x(Q+R)-4=-2 is a nonsquare in F_23.')
    print('CERTIFIED: four classes independent in E_5(Q)/2E_5(Q),')
    print('therefore rank(E_5(Q)) >= 4 and dim_F2 Sel_2(E_5/Q) >= 4.')


if __name__ == '__main__':
    main()