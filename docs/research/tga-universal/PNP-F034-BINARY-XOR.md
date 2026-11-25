# PNP-F034 — Binary XOR terminal refinement

PNP_RESOLUTION_STATUS = OPEN.

Candidate based on merged research head
03b9d7c80fb4f412df7227d2d59e09fe8da072e6 (PRs #227–228 merged).
Independent of pending binary chain repair. Uses verified reference
projection, literal membership, checked equality, decoded width and
intermediate support/target width closure.

Substitute checked binary reference lookup and row equality, literal
membership in signed patterns, and identifier equality in XOR support
toggle and combination. Preserve the existing structural support-size
guard, Boolean parity, and emptiness tests. Prove conditional result
projection for representable fields; successfully decoded operands and
the target-width theorem discharge these conditions for an XOR terminal
on the decoded target. Terminal soundness is conditional on acceptance
of the binary XOR check, not on arbitrary proof or certificate existence.

For support list length S and width w, toggle selected comparison
gates are bounded by (10*w+3)*S, i.e. 5123*S at w=512.
No aggregate terminal gate bound, encoder/padding/allocations, or full
machine-cost assertion. In particular the length guard remains a
structural Nat operation.

Thirteen candidate declarations, 2210 executable control groups:
120 toggles, 1600 support pairs, 480 blocks, 8 terminals, one positive
contradiction and one wide contradiction. Strict Lean 4.14.0, warnings
as errors, exact marker F034_BINARY_XOR_OK toggles=120 pairs=1600
blocks=480 terminals=8 positive=1 wide=1, and thirteen zero-axiom checks.
Fresh exact-head replay required before PR. No local Lean execution.
No completeness, polynomial certificate existence or P vs NP resolution.
