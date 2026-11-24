# PNP-F016 — Complete structural Boolean-tape cost theorem

**MathOS | Specialist formal research | Materialized restricted disjoint AND-block input**

## Scope

F015 merged at 01e809c9b8cfc600ec9a05c1bc1efe0cbf89d251 after successful kernel and cross-language replay. F016 composes its explicit Boolean affine solver with F012's counted domain and witness traversals. The new proof-carrying result reports five structural charges and preserves the F015 SAT/UNSAT wire semantics. No integer coefficient or provenance masks are used by the solving path.

## Cost model

Let n be the number of domains, r the original coupling row count, q the total number of listed pairs (duplicates allowed), and M the augmented row count. Let s count the gate-mapping and two short-circuit membership passes; p count the prefix-pad events; g count the generated rows; v count actual witness-search pair visits. The established traversal bounds are s <= 3q, p <= n squared, g <= n and v <= q. M <= r+n.

Preprocessing charges 4s + 4p + (4n+4)g + 4n + 2r + 2. These terms charge mapping/membership, prefix pads, fixed-width fitting/row construction, domain-header and original-row assembly events respectively. Fitting and assembly are analytical per-length/header charges; they are not instruction traces. Affine charge A is the instrumented F014 charge bounded by 4M squared + 6M + n[M(4(n+M+1)+6)+4n+4]. Witness lifting charges 4v+4n on SAT and zero on UNSAT. The wire has length L <= 2n+r+1. Construction is charged 3L; counted copying is 2L. These are distinct stages. Total is their sum, not elapsed runtime.

Define B(n,r,q,m) = 12q + 4n squared + (4n+4)n + 4n + 2r + 2 + A_bound(n,m) + 4q + 4n + 5(2n+r+1). The candidate theorem bounds total by B(n,r,q,r+n).

For S = 1+n+r+2q+r(n+1), a structural input-cell/header length, each of n,r,q,r+n is at most S. Monotonicity gives total <= B(S,S,S,S), whose algebraic expansion is 8S cubed + 26S squared + 55S + 7. The formal theorem uses the factored polynomial, while the Python controls check this expansion.

## Validation

Eight new audited declarations cover preprocessing and polynomial monotonicity, proof-carrying finish and solve, wire validity, total charge and input-size bounds. Replay all 122 prior declarations and eight new declarations with the established axiom policy. Compare exact wires and all five charges plus the total with Python across the 4,181 F015 fixtures and six additional cases, including long repeated domains, zero-variable contradictions and larger free systems. Independently verify certificates against original witnesses and weighted augmented rows. Re-run F014 and F015 regression tests.

Run python -m mathos.research.tga_proctor_pnp_total_tape_cost --output-dir artifacts/pnp-total-tape-cost. Actual report.json determines acceptance.

## Limits

This is a total charge only for the specified structural list/cell model on already materialized, well-formed disjoint domains and rectangular rows. Input parsing, finite-state tape-head motion, pointer representation, recursion frames, natural-number counters, allocation, and Python language refinement remain open. The header model is not yet a serialized input parser. Output checking is separate from the solver charge. The counts do not establish runtime or unrestricted SAT complexity. No independent review, live paid AI research, literature novelty, or canonical promotion is claimed.
