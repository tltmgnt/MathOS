# PNP-F009 — Proof-carrying global highest-bit Gaussian elimination

## Mathematical scope
For any finite list of in-width nonnegative coefficient masks and Boolean right sides, the formal algorithm returns an in-width satisfying mask or original-row selection mask certifying contradiction. This is a classical restricted affine decision algorithm, not unrestricted SAT. The previous F008 local theorems are used directly.

## Basis and invariant
A basis has one optional slot per pivot, ordered from highest to lowest. An occupied slot contains a tagged row and proof that its highest bit is the slot index. Each tag stores a natural-number provenance mask and the exact weighted-row semantic invariant from F008. Empty basis satisfies all assignments. Insertion scans the slots downward: if the new mask has no bit at the current slot, descend without changing the slot; if its highest bit is at a vacant slot, store it; if occupied, XOR row and provenance and descend. At dimension zero the row is zero: right side false is redundant, true gives a contradiction. The result type requires either a valid original-row contradiction or a new basis with a proof that its satisfying masks are exactly those satisfying the old basis and new row. Recursion decreases the slot count, hence terminates.

## Global construction
Initialize each original row with the unit mask at its list index. The codec and unit-dot theorems establish exact provenance for that unit mask. Process the original list recursively; the feed result preserves equivalence between satisfying the final basis and satisfying the incoming basis together with all remaining rows, or returns a valid original-row contradiction. Proofs of width and provenance are erased during execution.

## Reconstruction
Recurse down to lower slots, then visit occupied pivots in increasing order. The returned assignment below a pivot is strictly less than its unit mask. The F008 backstep theorem sets the pivot when necessary, preserves every lower row, and the width bound ensures no higher bit is set. The final satisfying assignment is therefore in width. The highest_output_spec theorem proves the returned primal mask decodes to a satisfying vector, or the dual result rules out every assignment of the declared width. The unsat completeness theorem extracts a dual result whenever no satisfying vector exists.

## Implementation boundary
The dense slot traversal is a mathematical model of the dictionary-based highest-bit algorithm, skipping vacant slots and retaining the same pivot semantics. It is not an instruction-level proof of Python execution, nor a proof of dictionary costs. Regression compares actual B006 output masks and XOR counts against the F008 trace mirror on all ordered systems with up to three rows and three variables. A cross-language check compares the Lean global solver's exact primal or dual output with those mirror results. Passing finite controls is not universal implementation equivalence. A complete source-language refinement and formal polynomial bit-cost proof remain open.

## Reproduction
Base 437424d85febf6e98752457969aff8693c0fe3d1. Run python -m mathos.research.tga_proctor_gf2_global --output-dir artifacts/gf2-global with Lean 4.14.0. Replays all preceding audited theorems and the seven new definitions/theorems, preserving strict empty-axiom policy for prior proofs and explicitly allowing only propext and Quot.sound for library-backed proofs. Actual results in report.json determine acceptance. No live AI discovery, independent review or canonical Millennium promotion.
