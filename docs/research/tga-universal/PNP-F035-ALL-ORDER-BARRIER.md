# F035 — All-order obstruction for raw factored elimination

PNP_RESOLUTION_STATUS = OPEN.

For k distinct variable IDs, include all four sign combinations of
each ordered pair of distinct IDs, and a threefold repeated positive
literal clause for each ID. This uses 4k(k-1)+k rows and O(k^2)
literal occurrences, all of width at most three as lists. It is a
trivially UNSAT formula for k>=2; this is a stress case for the exact
raw elimination architecture, not a hard SAT benchmark.

Suppose each oriented signed pair of surviving IDs has multiplicity
at least m. Eliminating any fresh ID v preserves m copies of each
surviving pair (common bucket) and produces at least m^2 additional
copies from the product of the singleton residuals of (v,u) and
(not v,w), with arbitrary signs on u,w. Thus the minimum pair
multiplicity grows by m -> m+m^2, independently of ordering.
Starting from m=1 it is at least 2^t after t eliminations.
The repeated-literal marker on each uneliminated ID remains in the
common bucket, preventing the existing width-two gate from accepting.
Consequently any distinct-variable elimination order reaching a
width-two leaf must pass through a state with at least 2^(k-2) rows
while two variables remain (or exceed its budget earlier).
The input has polynomial encoded size, so no uniform polynomial
raw residual-weight cap suffices for all these schedules.

The candidate Lean module proves the multiplicity recurrence and
arbitrary-prefix invariant under explicit initial richness, marker
and distinctness hypotheses. The concrete family is supplied by the
fixture generator; the general initial richness argument is given
above, not yet a separately verified Lean theorem. Seventeen prefix
fixtures exercise the exact implementation.

This barrier uses retained duplicate rows/literals and the width-only
leaf gate. Deduplication, early contradiction checks, resolution
preprocessing, or a different symbolic representation can defeat
the example. It is not a lower bound for normalized resolution,
all variable-elimination algorithms, or P versus NP. It falsifies
the proposed universal raw bounded-schedule hypothesis, not the
positive resolution itself. The next investigation must change the
mechanism, rather than optimize the raw ordering further.

21 public theorem candidates, strict replay required.
