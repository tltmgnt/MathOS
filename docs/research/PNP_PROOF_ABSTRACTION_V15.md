# MathOS v15 — compact proofs and reusable contradiction templates

v14 passed both jobs but the hybrid regressed on total coverage: 15/24
versus 18/24 for v12, with zero learned clauses. It refuted 6/6 UNSAT
versus 4/6, but solved only 9/18 SAT versus 14/18. Do not replace the
v12 scheduler by default. The fixed phase allocation needs an ablation
study; v15 instead works on a separately testable proof representation.

## Contract

A v13 resolution proof is checked before compression. Retain ancestors
of the empty clause, hash-cons equal derived clauses, trim again, and
renumber used variables densely. Store only participating input axioms
and triples (positive parent, negative parent, pivot); reconstruct each
derived clause independently rather than storing its literals. The
source embedding translates template labels back to original input labels.
The compact checker requires backward references, correct pivot signs,
non-tautological nonduplicate resolvents, an empty root, and no unused
records. This is syntactic compression, not optimal proof minimization.

A target formula can reuse the contradiction when a signed injection of
template variables maps every template axiom to a normalized target
clause. Pulling back any target assignment would satisfy the contradictory
template, an impossibility. Extra target clauses are harmless. A bounded
matcher explores at most 4096 signed variable assignments using partial
clause checks; a supplied injection is checked directly. Failure to
find a match never proves satisfiability. No unproved lemmas are transferred
between formulas. This is a sufficient syntactic reuse condition, not
a complete recognition method or a polynomial proof-size theorem.

## Run

    python -m mathos.research.pnp_abstraction_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --checkpoint artifacts/pnp-v15.json
    python -m mathos.research.pnp_abstraction_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --audit artifacts/pnp-v15.json

The default experiment consumes audited v13 selected refutations,
checks compression and a constructed signed-renamed superformula for
each, then tests matching on 16 separately seeded small random CNFs.
Constructed variants are positive controls, not independent evidence
of broad coverage. Fresh references are exhaustive. Compare compact
JSON bytes of original proof versus compact template plus source
embedding; both require original input externally for source verification,
and compact templates carry their participating axioms explicitly.
Record axiom/step counts separately. No compression ratio is guaranteed.
No timing speedup is inferred. The audit regenerates and verifies
templates, embeddings, match outcomes, references and aggregate counts.
Lean checks only abstract resolution and reuse soundness, not Python
or the full asymptotic complexity. Universal obligations remain open.
