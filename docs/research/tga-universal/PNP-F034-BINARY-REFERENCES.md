# PNP-F034 — Binary certificate reference validation

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 62e46e7bcd8d36a71f4f9002afcec1f2e751b098 (PR #221). Use merged #219
binary equality and #220 checked binary lookup. Independent of
pending padding replay. Substitute checked binary equality into
literal comparison (two extra sign gates and one AND), membership
and ordered row equality, and checked binary lookup into reference
validation. Conditional projection under explicit representability
of operands; gate bound per literal 10*w+6, per row or membership
10*w+6 times the left row length. Reference visits <=(w+1)*f.length;
literal gates <=(10*w+6)*selected row length (zero on failed lookup).
These are distinct coordinates. No encoder, padding allocation,
list traversal in row comparison, or total runtime claim. No
unconditional equivalence outside representability. Full input
width propagation and all derived checker arithmetic remain open.

Nine candidate declarations, 1337 executable control groups
(256 literal, 289 row, 272 membership, 510 references, 4 wide,
6 extra recursive and rejection controls).
Marker F034_BINARY_REFERENCES_OK literals=256 rows=289 membership=272 refs=510 wide=4 extra=6. Strict Lean 4.14.0 warnings-as-errors and
zero-axiom gates unchanged. No local Lean execution. Exact
preflight required before PR. Independent review remains open.
