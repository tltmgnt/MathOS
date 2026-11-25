# F035 — Universal decimal encoder candidate

PNP_RESOLUTION_STATUS = OPEN.

This module constructs canonical decimal words without relying on the
runtime toString implementation for the proof. It follows the quotient
chain n/10, appends the remainder digit, and places LF after each word.
Structural recursion is fueled by n+1; it terminates at a single digit
and does not enumerate the numerical identifier range. The proof uses
the scanner's accumulator invariant with arbitrary suffix and accumulator.

Target: tokenize (encode tokens) = some tokens for every finite list of
natural tokens, with no digit, byte or list cutoff. The existing
unbounded expected-input and envelope token roundtrip theorems then
give unconditional byte roundtrips and preservation of accepted proof
envelopes. The original checker is unchanged.

Eleven public theorem candidates and 1137 control cases: 1000 singleton
values, 129 triples around decimal powers, two lists, two accepted
proofs including a sparse identifier and zero-bound empty clause, and
four noncanonical byte rejections. The fixture oracle uses toString;
the formal encoder does not. The implementation uses list append and
division and does not establish a bit-cost theorem, a canonical
uniqueness theorem, or a complete serialized solver. The finite SAT
model module is on a separate branch and is not a dependency.
Strict exact-head replay is required before credit.
