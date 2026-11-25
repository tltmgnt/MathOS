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
