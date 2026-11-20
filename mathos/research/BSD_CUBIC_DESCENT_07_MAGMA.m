// MathOS BSD Milestone 07 — OPTIONAL EXTERNAL Magma work order.
// NOT run by MathOS CI. This is a suggested specialist-CAS script, not a
// certificate of exact rank or an independent mathematical review.
// The local Python audit proves only a large unconditional descent bound.
// Cited API: https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html

Q := Rationals();
params := [0, 24, -24];

for u in params do
    s := u*(u+1);
    assert s mod 2 eq 0;
    E := EllipticCurve([Q|0, s div 2, 1, -((s+2) div 2), 0]);
    D := s^4 + 10*s^3 + 34*s^2 + 60*s + 37;
    assert Discriminant(E) eq D;

    printf "u=%o, D=%o\n", u, D;
    // 2-Selmer group upper bound is computed using Magma's exact descent.
    // Actual execution results must be saved and independently reviewed.
    G := TwoSelmerGroup(E);
    printf "2-Selmer group 2-rank (computed externally) = %o\n", Ngens(G);

    // RankBounds may use several algorithms, including higher descent.
    lower, upper := RankBounds(E);
    printf "Rank bounds (lower, upper) = (%o, %o)\n", lower, upper;

    // The three distinguished rational sections exist for all u, but do
    // not necessarily remain independent for every specialization.
    P := E![0, 0, 1];
    R := E![1, 0, 1];
    T := E![-1, u, 1];
    // Coercion to E above validates the curve equations.
    printf "Three explicit points on E: %o, %o, %o\n", P, R, T;

    // NOTE: no automatic promotion even when upper==3; one must separately
    // certify a rank-three lower bound and report the exact input/output.
end for;
