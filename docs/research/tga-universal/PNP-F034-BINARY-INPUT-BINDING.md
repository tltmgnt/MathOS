# PNP-F034 — Binary input binding and identifier range refinement

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged research head 1c2e6c30ddeade4ae8e2405c3014a7bcdf1401a8
(PRs #224–226 merged). Independent of pending intermediate-width
repair. Reuses verified row equality, checked identifier comparisons
and decoded field-width theorems.

Ordered CNF equality preserves literal order, row order, duplicates and
length mismatch rejection. The range meter checks positive identifiers
bounded by the expected variable count. For width w and L literal
occurrences in the expected CNF, selected comparison gates are bounded
by (10*w+3)+(10*w+6)*L+(10*w+2)*L. At w=512 this is 5123+10248*L.
The three selected checks are reserved independently, even on rejection.
Boolean combining, list traversal, encoding, padding, other checker
operations and machine cost are excluded from this selected gate bound.

The proposed byte-level checker substitutes the binary binding and
original-formula range checks, retaining the original validProof and
semantic checker. It uses the fuel-free decoders and their verified
decoded-width invariants, aiming for exact Boolean agreement on all
byte pairs and the existing conditional UNSAT soundness conclusion.
No claim of binary refinement for the unchanged remainder.

Fourteen candidate declarations. Executable marker:
F034_BINARY_INPUT_BINDING_OK pairs=441 ranges=84 bindings=441 decoded=42 positive=1.
1009 control groups, including an accepted empty-clause fixture,
malformed inputs, mismatched formulas and wide operands.
Strict Lean 4.14.0 warnings-as-errors, exact marker and explicit
zero-axiom checks for all fourteen declarations. Fresh exact-head replay
required before PR; no local Lean execution. No certificate completeness,
polynomial certificate existence, or P vs NP resolution claim.
