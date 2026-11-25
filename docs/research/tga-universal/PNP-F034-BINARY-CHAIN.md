# PNP-F034 — Binary resolution-chain refinement

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged research head
1c2e6c30ddeade4ae8e2405c3014a7bcdf1401a8. Reuses verified checked binary
lookup, literal equality, membership and decoded field width.
Independent of the intermediate-width and input-binding PRs #227–228.
The local tails-fit lemma includes all step operand conditions, rather
than importing a pending dependency.

For width w, tail length T and selected parent row length R, reserve
(10*w+6)*(T+1)*R selected literal-comparison gates. Parent lookup
visits are bounded by (w+1)*F where F is the current frontier length.
Both parent reservations are accumulated per step, then over each
batch and the chain (using each successive frontier). A failed checked
lookup has zero shape gates. No encoder, padding, allocation, Boolean
combining, list traversal outside lookup or full machine cost claim.

Projection preserves the existing paired-replay checker, including
its weakening semantics; no new exact-resolution completeness claim.
On successful decoding of the expected and proof bytes, the existing
decoded-width theorem supplies all step and formula premises.
Accepted binary chain replay then entails its final frontier.
This is not yet a complete binary checker or an UNSAT conclusion
without terminal validation.

Seventeen candidate declarations; 4711 executable control groups.
Marker F034_BINARY_CHAIN_OK shapes=200 steps=4500 chains=8 wide=2 decoded=1.
Strict Lean 4.14.0 warnings-as-errors, exact marker and all seventeen
zero-axiom checks. Fresh exact-head replay required before PR.
No local Lean execution; no certificate existence or size guarantee.
