# F035 — Tagged finite SAT/UNSAT witness interface

PNP_RESOLUTION_STATUS = OPEN.

Integrates the verified total 2-CNF solver (97c4401c) and finite model
module (9c3fa6e0). Tag 0 introduces an assignment literal list; tag 1
introduces the existing bound proof envelope. The checker uses the
independently supplied expected formula and validates the decoded
witness; malformed tags and trailing tokens are rejected. Invalid or
unsupported solver inputs have no witness. On valid width-two inputs
the candidate producer is total, and accepted SAT and UNSAT tags are
mutually exclusive for any formula. The checker soundness statements
are not restricted to width two.

The token roundtrip is unconditional. The byte roundtrip is conditional
on successful tokenization; the universal decimal encoder is pending
on an independent branch. The fixture encoder uses decimal strings.
The producer uses no exhaustive assignment-search fallback. This is
not an encoded runtime bound and not an unrestricted SAT algorithm.

Ten public theorem candidates; 1034 fixture cases (1024 formula
subsets/reversals, two sparse, two empty, six rejection).
Exact-head strict replay required.
