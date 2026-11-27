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

Theorem I review: verify the independent-product affine cover bound, connected single-row exact rank formula, fixed-order H tree recurrence, and sound subproblem proof extraction. Check that factorization is not described as novel and that none of these bounds is a general SAT lower bound. Compare both node counts and actual proof sizes; do not extrapolate runtime speedups.

Theorem J review: inspect the orthogonal-complement equivalence, uniqueness of RREF argument for interleaved columns, provenance soundness, complexity including elimination, and hidden-factor ordering proof. Distinguish canonical affine partition from nonlinear semantic factorization; compare against standard direct-sum decomposition before asserting novelty.

Theorem K review: verify signed occurrence encoding, forest full-affine-hull induction (including parallel edges at r=1), strict order separation, fixed-point termination, explicit tuple/form complexity, and checker soundness. Compare this operator to existing local consistency and parity inference literature. Do not treat the simple 2-SAT family as a SAT hardness result.

Theorem L review: check monotonicity including empty reachable sets, greatest closed subset, streaming hull early termination, rank-difference dimension, probe complexity including SAT witness extraction, full-order coNP-completeness and Sigma_2^P upper bound. Check that closed-subspace certificates justify minimum order without a polynomial-time checking claim at variable order. Compare to existing proof-width/consistency hierarchy research.

Theorem M review: check the forest lower bound for multigraphs, distinct-index path upper bound, shortest-path implementation versus global optimum, constant-treewidth family, and factor-threshold identity. Check polynomial graph cost and distinguish a coincident interval from an exact classification for all inputs. Review novelty independently.

Theorem N review: inspect block-support lower bound, affine frame completeness, deletion-minimal core proof, enumeration accounting, GF(4) scalar-invariant hull argument, and pencil derivation. Independently check order-three non-detection and order-four contradiction for the 21-block control. Do not equate small affine dimension or the 21-block count with the original 21-bit target or P vs NP resolution.
