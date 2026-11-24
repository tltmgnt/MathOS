# PNP-F014 — Proof-carrying sequential Boolean-tape affine elimination

**MathOS | Specialist formal research | Explicit list/cell operation model**

## Scope

F013 passed workflow 45398382666. F014 implements a complete affine core in the coordinate order of F004, not the highest-bit dictionary strategy of B006/F009. Input is an explicit rectangular Boolean row list of m rows and n coefficients. Each tag stores exactly n current coefficient cells (decreasing with recursion), one right-hand-side bit, and exactly m provenance cells. The proof-bearing shift relation preserves the original weighted row semantics. No integer bitmasks are needed for the runtime affine operations.

## Algorithm and invariants

Initialize full unit provenance tapes: the first row has true followed by m-1 zeros, and each tail tag gets a false prefix. Scan row headers to find a nonzero first coefficient. If no pivot exists, strip the zero head of every row. Otherwise XOR the pivot with each row with a true head, using F013 xorCells on both equal-width coefficient and provenance tapes, and strip the cleared coordinate. Row replacement and projection equivalences from F002/F004 establish preservation. Recurse on dimension n-1; at zero dimension, any true RHS produces its original-row selection tape. Otherwise the empty assignment is valid. On the return path compute the pivot bit using F013 dotCells, or use false in a free coordinate. The executable result is a primal assignment or an explicit original-row dual selection. The theorem tape_output_valid proves that every output passes the F005 universally verified certificate checker.

## Explicit modeled charge

Initialization counts a first unit tape plus the prefixing pass over tail tags, charging 4m per initialization level; the bound is 4m squared plus 4m. Pivot and terminal scans charge two operations per visited row. A row update charges four structural/header operations, plus exactly four per coefficient, RHS and provenance position on a collision. At current width k+1 this is at most 4(k+1+m+1)+4. Reconstruction performs a counted dot product of k cells and four extra operations (or one free-bit/return event). All row-list transformations preserve row count. With fixed maximum width U=n, define columnBudget(U,m,m)=m(4(U+m+1)+6)+4U+4. Induction over n establishes total affine charge at most

4m^2+4m+n[m(4(n+m+1)+6)+4n+4]+2m.

The structural list model includes the enumerated header transitions, cell operations, and explicit recursion. It is not a formal finite-state tape-head simulation: list pointer access, allocation, host call frames, natural-number counters and control overhead are not individually compiled into machine steps. Initialization includes analytical per-level charges. The formal input is already rectangular and materialized. Original domain preprocessing/lifting, serialized instance parsing, and proof of equivalence to the highest-bit trace remain separate. This is a new executable proof-bearing affine implementation, not a proof of the runtime of the earlier Python program.

## Replay

Replay the 103 preceding declarations and eleven new ones under Lean 4.14.0 with the same axiom allowlist. Compare the exact result tapes and charge with a separate Python coordinate-order mirror on every ordered system with at most three variables and three rows. Check each mirror certificate against original rows and exhaustive primal enumeration. No claim of mathematical literature novelty, independent review, live AI discovery or canonical Millennium promotion.

Baseline 62e7fd4c389d85b5b666670a684b5e5dadfa18bd. Run python -m mathos.research.tga_proctor_tape_solver --output-dir artifacts/pnp-tape-solver. Actual report.json determines acceptance.
