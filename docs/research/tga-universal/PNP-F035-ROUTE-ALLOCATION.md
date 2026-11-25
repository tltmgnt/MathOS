# F035 — Amortized route-list construction

PNP_RESOLUTION_STATUS = OPEN.

Based on the verified aggregate comparison branch accc1c4d.
Charge a successful relaxation with old path length k by k+2:
k+1 path-list cells and one new table cell. Failed relaxations
have zero charge in this model. The seed is not charged. This
counts a conservative immutable-list construction schedule,
not actual native allocations, temporary pairs, lookups or time.

The candidate telescoping inequality is
charge + (cap+1)*initialRows <= (cap+1)*finalRows,
under the existing short-path and missing-destination invariants.
With E arcs, the single-query charge is at most (E+2)*(E+1).
This is quadratic rather than multiplying the worst append cost
by every sweep and relaxation. Five public theorem candidates,
3073 executable controls. Strict exact-head replay required.
