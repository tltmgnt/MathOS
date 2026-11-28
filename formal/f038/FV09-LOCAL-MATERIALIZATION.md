# FV-09 — Certified bounded local residual materialization

Status: implementation committed; executable replay PASS; new Lean compilation and axiom gate PENDING.
Prior FV-08 proof checkpoint d9b3eca07b06379b41ebb4e2c33b02b30662bda6 passed Proctor run 52.
PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Mathematical interface

LocalMaterialization.lean checks one residual factor per input factor, with a proposed list of free-coordinate support and a maximum list length cap. The coverage gate includes every variable in each referenced affine form and every residual scope coordinate. The checker enumerates assignments on that support, with other coordinates fixed false. Its intended proof establishes that every full assignment agrees on the checked support with some enumerated assignment; parity and table evaluations therefore agree. Even duplicate support coordinates are safe (but consume the cap).

For a support of list length s, localAssignments_count states that the enumeration contains exactly 2^s entries. The checked cap implies at most 2^cap rows per factor. This is a row-count bound, not a total bit-complexity result. A one-to-one aligned list of f factors has at most f*2^cap local checks by summing these per-factor bounds; no global 2^m enumeration is required in this local checker. Wide affine forms may require a large cap or yield rejection. A bounded cap is not a proof of unrestricted solver completeness.

localCheck_exact states pointwise equivalence between the residual and the affine pullback. local_reduction_exact composes that equivalence with FV-03 relational replay and checked affine reconstruction. localHall checks those gates and the existing Hall packet before returning UNSAT; failures return UNKNOWN. It is an alternate reduced-Hall reference gate, not yet the production release implementation. The previous global enumeration reference is retained. Fifteen anonymous regression examples and two named fixtures are included; the full inventory extends by 14 named theorem scripts (12 kernel + 2 fixture), to 111.

## Executed concrete replay

Loaded the exact committed JavaScript modules for D7B rank reduction, affine closure and dense certificate verification, and the new local replay and audit. The independent local replay evaluates every source factor including those marked affine by the producer, checks omitted tautologies, duplicate-scope intersections, and the dummy zero-free coordinate. It rejects unsupported outcomes and caps above 16. The audit also checks the existing affine certificate verifier and exhaustively checks model images on small accepted inputs.

| Check | Result |
|---|---:|
| Small input instances | 128 |
| Accepted narrow results and exhaustive image comparisons | 106 |
| Unsupported results rejected | 22 |
| Small local row evaluations | 1264 |
| Deliberate corruption / cutoff rejections | 5 |
| Large sparse fixture source/free coordinates | 64 / 62 |
| Large local evaluations / maximum support | 14 / 2 |
| Zero-free padding | PASS |
| Actual wide fallback rejected | PASS |

This is actual finite execution evidence, not a proof of JavaScript semantics. For the large sparse fixture the audit checks local equivalence without a full model-image enumeration.

## Outstanding obligations

- Obtain successful compilation and actual axiom audit of the 111 named theorems and all fixtures.
- Mechanize concrete D7B source/operation log translation, omission of tautologies, duplicate-scope intersection, zero-free dummy-coordinate semantics and contradiction/fallback paths. The Lean one-to-one interface does not yet verify these concrete output transformations.
- Mechanize D7A relational logs, input decoding, graph operations, physical compiler/selector, exact clock formula and total bit complexity.
- Obtain independent human mathematical review. No proof of P vs NP or production promotion.

Reproduce: node mathos/research/f038_rex_fv09_audit.js; run the formal Proctor workflow for the exact branch checkpoint.
