# PNP-F034 — Boundary encoder integration

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base fa2c380e9a357a1699adf975d1dc7e0416af391d (PR #213). Four files copied byte-identically
from verified PR #214 head 3b2321ca13b29fbd57dbcdbeecf67b02f231599c, exact preflight 45549369449/job
138986579262/artifact 14993048129, five zero-axiom declarations and
567 controls. Require #214 merge and exact candidate replay before PR.

Use verified scanner meterCore with digit encoder charge and zero
counter arithmetic charge. Reserve encodeMeter 4 at every visited
digit-classified byte even when a guard rejects first; projection
to checked tokenizer unchanged. Add a fourth resource coordinate
<=21*byte length to the verified scanner resource vector.

Substitute encodeMeter 17 for a single list header (only when the
original list-limit guard passes). Prove exact result and accounting
equality to listMeter plus headerEvents, <=307. For any child satisfying
the existing amortized contract, the augmented list bound is
(64*input.length+3)+307. This does NOT establish closure of the
augmented meter under nesting; child costs remain unchanged. A
larger potential to pay for each nested header is next.

The encoder uses selected abstract Nat events and append visits,
not actual bit costs; scanner reservations can include skipped
operations. No fused execution, production substitution, allocation
or complete machine-cost claim. Nine candidate declarations,
1923 controls (781 scanner, 8 boundary, 1122 lists, 8 headers,
4 exact). Marker F034_ENCODER_INTEGRATION_OK scanner=781 boundary=8 lists=1122 headers=8 exact=4. Strict Lean 4.14.0 warning and zero-axiom
gates unchanged. No local Lean execution. Independent review and
certificate-size/discovery remain outstanding.

## Initial replay and constructive repair

PR #214 merged at 6109ccc8c72f51bdbcdcc8682f3cfd828f9fbf3e.
Exact head 32d6ae676ec1d88ca7a7f5eaa8488bd463d7b9df compiled and passed all 1923 controls,
but [45550749776 / job 138991062461](https://github.com/tltmgnt/MathOS/actions/runs/45550749776/job/138991062461), artifact 14994445247,
failed the strict axiom gate: list_account and its two dependent
proofs reported propext. Six other declarations printed no axioms.
Replace the simplifier in list_account with explicit equality rewrites
of the four guard occurrences and the encoder projection. No theorem
statements, executable code, controls, or gate requirements changed.
A fresh exact-head replay is mandatory before opening a PR.
