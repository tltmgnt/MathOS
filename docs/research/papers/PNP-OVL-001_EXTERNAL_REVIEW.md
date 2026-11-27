# Independent review packet — PNP-OVL-001

Review requested in principle only; no reviewer contacted and no review completed.
Provide the exact commit, PNP-OVL-001.md, prior-art note, Python test log, Lean log and any counterexamples to a researcher in Boolean CSP or complexity theory.

Reviewer response (to be filled by reviewer):
- Identity/affiliation and consent to attribution:
- Commit and exact theorem statements reviewed:
- Correctness of Theorems A/B/C (each separately):
- Missing assumptions, counterexamples or complexity accounting issues:
- Prior-art citations and novelty determination (each theorem):
- Reproducibility commands and observed results:
- Publication significance and requested revisions:
- Date and independent review disposition:

Do not equate CI, AI review or self-review with independent expert acceptance. If prior art subsumes the results, retain the artifact as exposition/formalization and open a new, stronger research question. No P versus NP promotion is permitted by this packet.

Additional review: assess Theorem D separately, including rank-nullity, exact feasible-pattern count, bit-cost accounting, comparison with affine backdoor algorithms, and the structured 21-component control. Do not interpret this as an evaluation of the 21-bit state identifier.

Theorem E review: check quotient-space kernel proof, Vertex Cover reduction, exact depth budget, end-to-end optimizer accounting, and distinction between predicted pattern counts and measured visited leaves. Compare with submodular vertex cover and matroid-rank minimization before any priority claim. Full formalization remains open.

Theorem F review: check graph rank-to-cover conversion including singleton components, iterative-deepening node bound, quotient-basis independence for the parity-gap family, and the distinction between 3^delta* optimization and 2^delta* split enumeration. Compare with subspace-transversal and XNF SAT literature; assess actual novelty independently.

Theorem G review: independently inspect the exact lower-bound tree and basis-span argument; validate complete lexicographic branch coverage, reconstruct all affine slices from original inputs, check dual row sums, and review proof length/space accounting. Run mutation tests and assess whether the proof format adds anything beyond existing certifying optimization and XOR proof logging. Software checker independence does not constitute independent expert review.

Theorem H review: check exact reachable-set retirement, residual optimum decrease, sum of optimizer costs, independent augmented-rank checks, and complete preorder coverage. The chain is a standard propagation-friendly example; assess only separation against G's explicitly full-leaf format, not all static solvers. No new novelty assessment or reviewer contact in this cycle.
