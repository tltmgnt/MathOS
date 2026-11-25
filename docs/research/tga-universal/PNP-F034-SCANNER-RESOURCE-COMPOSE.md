# PNP-F034 — Combined checked scanner selected resources

PNP_RESOLUTION_STATUS = OPEN.

Verified merged base 1299176e38f69084d02519343f8b392354640e70 (PR #211). Four files copied byte-identically
from verified PR #212 head f4c49cca7e13e6bd416ee8def9078823260fd16d, exact preflight 45547734886/job
138981281702/artifact 14991943281; nine zero-axiom declarations and
5917 controls. Require #212 merge and successful exact-SHA replay before PR.

Reserve accumulator zero-test visits and decimal narrowing visits
(<=1029), counter zero-test and narrowing visits (<=17) for each
visited digit-classified byte. Reserve counter zero-test visits on
LF and EOF; invalid other bytes carry zero selected structural visits.
Conservative digit reservations may include operations skipped on
rejection. The candidate structural bound is 1046*bytes.length+8.
Compose the three distinct coordinates: arithmetic gate reservation
<=5235*b, structural scanner bit visits <=1046*b+8, checked byte
prepass decrement visits <=20*b. Both scanner projections agree
with the verified bounded tokenizer. The combined resource tuple
describes independent ledgers of the same tokenizer, not a fused
runtime implementation. The prepass visits function is a non-tail
recursive specification; large-input executable cost accumulation
is not asserted. No addition of unlike units as a machine cost.
Byte classification, encoding, Nat projection, resets, output list
allocation/reversal, and other runtime costs remain outside these
coordinates. No complete scanner or bit-machine cost claim.

Ten candidate declarations and 793 controls (781 short, 8 boundary,
4 exact structural reservations). Marker F034_SCANNER_RESOURCE_COMPOSE_OK small=781 boundary=8 exact=4.
Strict Lean 4.14.0 warnings-as-errors and zero-axiom gates unchanged.
No local Lean execution. Independent review and resolution remain open.
