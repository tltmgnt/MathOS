# PNP-F034 — Unified selected binary checker refinement

PNP_RESOLUTION_STATUS = OPEN.

Integration branch based on research head 03b9d7c80fb4f412df7227d2d59e09fe8da072e6
and the four independently strict-preflight-verified heads of PRs #229–232.
All four dependency trees are incorporated without modifying their files.
This branch is not a merge into the research branch or main.

Candidate composes fuel-free decoders, binary input binding, proof range,
resolution replay, and empty/capacity/XOR terminal dispatch. A decoded
projection theorem for each stage supplies the proposed unconditional
Boolean agreement on all byte pairs and inherited conditional UNSAT soundness.
Structural Nat operations and some arithmetic remain. This is not a complete
bit-machine refinement.

The separate partial ledger reserves selected binding, proof range and chain
comparison gates and chain lookup visits. It deliberately excludes all terminal
resources, parser/scanner resources, encoding, padding, allocation, Boolean
combining and other structural traversal. No whole-checker cost claim.

Eight candidate declarations, 218 control groups (196 cross-pairs, six
positive fixtures including augmented replay, capacity, XOR and wide XOR,
five negative fixtures, eleven partial ledgers). Strict Lean 4.14.0, warnings
as errors, exact marker F034_UNIFIED_BINARY_OK pairs=196 positive=6 negative=5 ledgers=11
and explicit eight zero-axiom checks. Fresh integrated replay required.
No polynomial certificate existence or P vs NP resolution claim.
