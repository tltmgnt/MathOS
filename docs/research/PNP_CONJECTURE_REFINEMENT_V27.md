# MathOS v27 — certified counterexample-guided conjecture refinement

v27 builds on the component-parity recognizer of v26. The exact
component-evenness criterion is already known from v26; this is
an executable rediscovery/control, not a claim of a new theorem.

## Grammar

Represent a family member by an ordered list of prism components
with size and odd/even charge. Generate rules from partitions:
global, equal size, index modulo two, index modulo three, and
individual component. A rule predicts SAT when all its groups
have even charge. Generate all four coarse singletons and six
two-rule conjunctions, then the component-local rule. This fixed
grammar and order explicitly favor coarse aggregation. Index-based
rules are ordering dependent; they are deliberately weak candidates,
not invariant graph properties.

Use all descriptors of length one through six over the four
(size, charge) pairs (3, even), (3, odd), (4, even), (4, odd).
There are 5460 descriptors. The oracle for search is the documented
prism-component theorem, not a SAT solver call on each descriptor.
For the first surviving rule, find the first mismatch in the order
(component count, sum of sizes, lexicographic descriptor). Materialize
that case as a CNF, generate and independently replay the v26
component-parity certificate, and remove every remaining rule
contradicted by the witness. Repeat until a rule survives the entire
finite domain or none remain. The ordered search establishes minimum
counterexample size in the bounded descriptor family, not
clause-minimality or minimality over all CNFs. Replay checks every
prior descriptor and the elimination sequence, not just the endpoint.

## Frozen larger controls

After selection, test the rule on 24 deterministic seeded descriptors
with seven to twelve components and prism sizes five through eight
(disjoint from the training alphabet), equally split between zero,
one, two and four odd components. Construct actual CNFs and independently
replay every reference certificate. Compare the original global rule
with the selected rule. These intentionally designed cases test scaling
and counterexamples, not a representative SAT benchmark or unbiased
estimate of generalization. The component rule is present in the grammar
by design. Survival of the finite search does not prove it; the v26
mathematical spanning-tree argument is the justification for that
restricted class. No universal claim or complexity barrier status changes.

## Reproduce

    python -m mathos.research.pnp_proof_simulation_frontier --checkpoint artifacts/v24.json
    python -m mathos.research.pnp_barrier_frontier --checkpoint artifacts/v25.json
    python -m mathos.research.pnp_hypothesis_obligations --simulation artifacts/v24.json --barriers artifacts/v25.json --checkpoint artifacts/v26.json
    python -m mathos.research.pnp_conjecture_frontier --simulation artifacts/v24.json --barriers artifacts/v25.json --hypotheses artifacts/v26.json --checkpoint artifacts/v27.json
    python -m mathos.research.pnp_conjecture_frontier --simulation artifacts/v24.json --barriers artifacts/v25.json --hypotheses artifacts/v26.json --audit artifacts/v27.json

The audit checks exact upstream hashes and all prior audits, fixed
grammar, finite minimality, CNF witnesses, frozen holdout predictions
and aggregate counts. No new full Lean theorem is supplied in v27.
Universal obligations and published barrier assessments remain open.
