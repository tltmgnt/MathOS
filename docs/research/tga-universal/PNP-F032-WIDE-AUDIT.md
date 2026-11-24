# PNP-F032 — Wide hybrid and pigeonhole proof-system boundary

PNP_RESOLUTION_STATUS = OPEN. PR #154 merged into the parity research
branch at d17d0355ead1615df5e2540d607fc8aea00a65ce. CI run 45448754463
job 138639690923 passed six hybrid tests: 1400 formulas, 4200 runs,
728 SAT, 3060 UNSAT and 412 UNKNOWN; 3048 direct XOR, 4 BVE XOR,
736 projected search, 412 no route. The original fallback was tested
separately. All six direct/hidden graph comparisons passed; width-four
shared selectors remained UNKNOWN. Artifact 14947206182.
https://github.com/tltmgnt/MathOS/actions/runs/45448754463/job/138639690923

## Opt-in width-independent search

Preserve the existing width-three default and add explicit
allow_wide=True to the hybrid and wide=True to dynamic search,
its verifier and the resolution extractor/checker. Validate signed
IDs without allocating by declared n, normalize literal sets and
deduplicate non-tautological rows retaining original indices.
Reuse F025 partition (only variable/row-index groups), F030
unit/pure simplification and F029 pair-based Horn recognition.
The latter considers all pairs within each clause, not just triples.
The previous certificate language (unit/pure, conflict, binary
split, UNSAT subset) is width-independent; the previous resolution
conversion argument also applies to arbitrary finite clause widths.
The wide SAT witness is checked on every original clause; projected
SAT is lifted using the unchanged BVE log. With a nonbinding finite
node budget the wide variant decides every finite CNF, but no
polynomial universal budget is claimed. Branch fixes a variable,
component child has fewer active variables. The proof conversion
requires at most m+V(mr+1) lines, regardless of initial width.
New controls check direct wide proof replay, malformed proofs, sparse
IDs, 1000 brute-force cases (raw widths through nine), and the
previous shared-selector family at q=4,8,16 (odd and even).

## An asymptotic obstruction to the actual hybrid policy

Use standard unary PHP with h+1 pigeons and h holes, h>=2.
For every pigeon i add the positive clause OR_j x_ij. For every
distinct pair i,k and hole j add (NOT x_ij OR NOT x_kj). No
at-most-one-hole-per-pigeon clauses are needed. There are
r=h(h+1) variables and m=(h+1)+h*binom(h+1,2) clauses.
Each support occurs only once; every support has at least two
variables. Thus no full parity block is detected (even for h=2);
each variable has one positive and h negative occurrences, so
the initial opposite-degree-two schedule is empty. There are no
tautologies or duplicate clauses. BVE performs zero pair tests
and the projection is identity. For this policy the only possible
UNSAT route is the resolution-simulable dynamic stage.
Haken's exponential lower bound for ordinary resolution on these
PHP formulas implies 2^Omega(h) dynamic visits after dividing by
the polynomial conversion overhead. Input bit length is
O(h^3 log(h+1)), so this is superpolynomial in explicit input length.
This argument does not assert a lower bound on arbitrary hybrid
policies, arbitrary GF(2) inference, other proof systems or SAT.
For this particular family matching algorithms or counting can
identify the contradiction efficiently. We have not implemented
them here. Default width-three policy merely returns UNKNOWN
for h>3; the bound applies to the opt-in wide policy on completed
refutations (smaller budgets return UNKNOWN).

Primary source: A. Haken, The intractability of resolution,
Theoretical Computer Science 39 (1985), 297–308,
https://doi.org/10.1016/0304-3975(85)90144-6.
The lower bound is established literature; the bridge to this
specific solver is a local paper argument, not an independent
review or a new resolution lower bound.

## Evidence contract

Record finite PHP h=2..7; h<=5 uses 100000 visits, h=6,7 use
1000. UNKNOWN at finite budget is allowed, not evidence of
asymptotic hardness. Extract and check actual ordinary resolution
proofs from completed PHP refutations. Also test satisfiable
equal-size PHP, and the old width-four limit. New CI must report
actual outcomes. Existing pinned Lean checks unchanged.
Wide-mode input, proof extraction, routing, and total bit-machine
refinement are not Lean-verified. No independent review or
original scratch port. Main untouched. No P vs NP promotion.
