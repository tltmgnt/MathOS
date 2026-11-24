# PNP-F034 — Structural resource accounting for the typed checker

PNP_RESOLUTION_STATUS = OPEN. PR #172 merged at
b0296955bcaae1f51934648411e9849166931eff. Initial run 45493045173
job 138796141550 failed:
artifacts/pnp-f030/f034-dimacs-lexical-combined.lean:2623:8: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
artifacts/pnp-f030/f034-dimacs-lexical-combined.lean:2631:8: error: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
Process completed with exit code 1.
Repository correction 3bd648a240539d96cee2c0a842ca36dd135c60b5
used explicit Boolean equalities for whitespace cases. Final run
45493765307 job 138798691753 passed all 17 new zero-axiom
declarations and 73 DIMACS file-pair controls (56 parses, 22
certificate acceptances, 51 rejections). Artifact 14965894537.
https://github.com/tltmgnt/MathOS/actions/runs/45493045173/job/138796141550
https://github.com/tltmgnt/MathOS/actions/runs/45493765307/job/138798691753

## Precisely scoped cost model

ProctorCheckerCost defines three executable metered primitives.
Lookup charges one per visited nonempty formula cell; contains
charges one equality comparison per visited literal; shape charges
one pivot equality per examined parent literal plus its membership
comparisons. Six candidate theorems establish equality of result
projections to the existing Lean lookup, contains and shapeCheck,
and bounds by formula length, tail length, and the additive
shapeBudget (one plus tail length per parent literal).
This is a formal abstract meter, not a verified compiler or
machine-instruction model. The production checker is unchanged.

## Whole typed-certificate structural ledger

Python ledger gives conservative upper estimates of SELECTED
operations from the actual Lean definitions, not timings or
instrumented runtime counts. Let S be the number of natural tokens
in the two custom data files encoding the expected typed input and
the proof envelope. It is at most the corresponding byte length.
S includes explicit row annotations, nested list counts and steps,
including all intermediate frontiers. Let M denote maximum natural
bit width; M is reported separately. Neither S nor M is the
declared number of possible variables.

Parent/ref lookup scans at most min(index+1, current row count)
nonempty cells. Shape scans at most (parent length)*(1+tail length)
comparisons. Row equality compares at most min(two lengths)+1
list-cell pairs (not natural bit steps). Let d be demand count,
D total demand literals, G total group literals, R total conflict
reference count and L total annotated conflict literals. Distinct
checking for group size g is at most g(g-1)/2; ordered words of
width k=capacity+1 enumerate g^k leaves, including repeated
literals (k<=3). At most k*L comparisons and R reference visits
per leaf, and at most k(k-1)/2 distinctness comparisons. Internal
enumeration nodes bounded by sum(g^j,j=0..k).
Demand disjointness uses d^2 pair checks, at most D^2 label
comparisons and a conservative (d^2+dD)(d+1) index-cell bound
allowing repeated list lookup per outer literal. Coverage scans at
most D*G literal comparisons plus D times group count visits.
Capacity>2 branches fail before enumeration.
XOR support width k<=5 implies 2^k patterns, at most k*L_b
literal comparisons per pattern for annotated block length L_b.
Sparse support sum toggles at most U^2 comparisons for U total
support occurrences, since every intermediate support length is at
most U. Width>5 blocks fail before pattern enumeration.

Each listed dominant term is O((S+1)^4) in this structural model:
sum of group cubes <= G^3, L<=S, and the demand index expression
is cubic. The remaining counted terms have smaller degree, and
the number of categories is constant. The test suite checks a
loose 256*(S+1)^4 envelope for the SUM OF LEDGER TERMS only.
Simple traversal proxy S is not an instrumented or proven bound
on all miscellaneous operations. This is not a complete cost
semantics for the actual checker. In particular, no claim that
the ledger accounts for every closure invocation, length call,
constructor, integer operation, parser step or runtime allocation.
A natural equality/order comparison depends on representation and
M; multiplying the ledger by a bit width does not establish a
machine transition bound. No uniform runtime bound on malformed
byte input, file I/O, or compiler is asserted.

A polynomial bound on checking explicit certificates would not
bound the size of certificates needed for arbitrary UNSAT formulas,
or the work to discover them. No inference toward P vs NP follows.

## Validation

Add four Python tests, 53 previous typed fixtures and nine family
measurements (PHP holes 2,3,4,8; cubic Tseitin vertices 4,8,16,32,64).
Record JSON ledger and strict six-declaration Lean axiom gate.
All new results pending CI, no local Lean. No independent review,
machine refinement, original scratch port or main change.
Next: extend executable metering to recursive batch/chain and
reference checks, then a complete abstract cost semantics for
terminal checkers before attempting bit-machine refinement.
