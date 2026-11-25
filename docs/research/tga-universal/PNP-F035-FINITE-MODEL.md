# F035 — Finite SAT witness and token serialization

PNP_RESOLUTION_STATUS = OPEN.

Based on the verified model-extraction module d119286a. Materialize the
assignment on the occurrence list, not the numerical bound [1..n].
The finite witness has exactly one pair per occurrence; duplicates are
consistent by construction. The reader uses first-match lookup and a
false default, defining a total assignment even for arbitrary witness
lists. The checker verifies all original clauses directly. It does not
require a complete or duplicate-free list, nor use a producer digest.
Arbitrary extra witness rows are permitted because the read assignment
is still a valid semantic witness. The expected input identifier range
is validated by the byte-level checker.

General materialization and check soundness/completeness are independent
of clause width. For the verified nonempty-clause 2-CNF fragment, absence
of a conflict yields an accepted finite model. The unbounded literal-list
parser gives an unconditional token roundtrip and conditional byte
roundtrip given successful tokenization. The executable test encoder
uses decimal strings; a universal proof of encoder/tokenizer agreement
is NOT supplied. The existing UNSAT envelope codec remains unchanged.
No bit-cost theorem or unrestricted polynomial SAT discovery claim.

14 public theorem candidates, 519 controls. Strict exact-head replay
required before credit. Main untouched.
