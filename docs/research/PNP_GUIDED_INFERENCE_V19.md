# MathOS v19 — multi-stage inference and compact proof-guided retrieval

v17 and v18 passed both computational and Lean jobs. v17 strengthened
analogy matched six constructed controls versus one exact match, with
zero fresh matches. v18 one-wave resolution gave two fresh template
transfers among five reference-UNSAT cases (24 fresh total), versus zero
raw matches. Its augmented matching work increased substantially
(28,213,336 versus 4,437,837 steps across all 32 cases). More inferred
clauses are not automatically better.

## Method

v19 introduces a bounded multi-wave resolution DAG. Wave d considers
complementary clause pairs whose maximum parent depth is d-1. A signed
occurrence index avoids enumerating all noncomplementary pairs. Earlier
proof records can be parents of later inferences. Short-first parent
ordering prioritizes smaller premises likely to help low-width template
matching; FIFO is an alternate library option. This is a heuristic,
not an optimal agenda or an explicit target-embedding planner.

Across all waves retain the existing 256-derived-clause, width-four,
20,000-pair caps; default three waves, hard maximum four. Every inferred
clause has parent/pivot/depth evidence. Partial derivations are valid
even if resources run out; the verifier reconstructs each inference and
checks depth and exact input identity. Search completeness and work
counters are not authenticated. No result is credited from a failed
search.

Next create a compact retrieval view. Process clauses in increasing
width and retain a clause only if no already retained clause is its
subclause. Every dropped clause has an explicit retained-clause witness.
The verifier checks the complete partition and every inclusion, which
proves logical equivalence. A resource-exhausted compactor falls back
to the identity view. Original inference records remain intact.
Run the existing v17 matcher on both the full and compact views of
the SAME inference DAG, with the same per-template limits. An empty
clause directly refutes the original formula; no matching is needed.

## Evaluation

    python -m mathos.research.pnp_guided_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --knowledge artifacts/pnp-v16.json --analogy artifacts/pnp-v17.json --semantic artifacts/pnp-v18.json --checkpoint artifacts/pnp-v19.json

Use the same inputs with --audit artifacts/pnp-v19.json for replay.
Generate upstream reports using their documented CLIs.

Two constructed controls separate multi-wave template transfer from
direct multi-wave refutation. The first pads each premise of a binary
contradictory template with two additional variables in all four
sign combinations. Its binary premises cannot be obtained in one
wave; three waves suffice for transfer, not the empty clause. The
second is a contradictory implication chain with an empty library,
requiring a direct multi-wave refutation. These are positive controls,
not independent evidence of broad coverage.

The fresh evaluation uses 24 seeded random CNFs with exhaustive
references, comparing v18 one-wave transfer, v19 full multi-wave
retrieval and v19 compact retrieval. The latter two share exactly the
same derivation so differences isolate the retrieval representation,
though the compact arm incurs its own compaction work. The one-wave
comparison changes indexing, parent ordering and inference depth, and
is not a controlled single-factor or equal-total-budget performance
claim. Report inference, compaction and matching work separately,
including both directions of coverage disagreement. No wall-time or
complexity improvement assumed. A stronger semantic representation
can still cause a bounded matcher to miss a previously found proof.

The audit checks all upstream artifacts, reference answers, positive
proofs, view equivalence, controls, and aggregates. Lean targets
abstract equivalence under adding consequences, dropping covered
clauses and composition. It does not certify the Python implementation
or the search heuristic. P versus NP remains unresolved.
