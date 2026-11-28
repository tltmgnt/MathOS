# MathOS v18 — certified inference-derived premise transfer

Extend v17 syntactic analogy with a bounded semantic implication layer.
Rather than require every template premise to be present or strengthened
in the input, derive implied clauses by resolution and then search the
augmented formula. This is a restricted inference grammar, not arbitrary
semantic implication discovery.

## Contract

Normalize the original CNF and restore its original variable labels.
Examine one wave of unordered original clause pairs, retaining only
non-tautological novel resolvents of width at most four. Cap accepted
derived clauses at 256 and examined pairs at 20,000, with cooperative
work/cell/deadline limits. Every credited inference has original
positive/negative parent indices, pivot, and resolvent. No derived
clause is used as a parent in this release. Partial waves remain valid
consequence sets even on exhaustion. The verifier checks each inference,
input fingerprint, dimensions, and the presence or absence of an empty
clause; it does not verify completeness of the attempted search.

The augmented formula is logically equivalent to the input, since all
added clauses are consequences. Run v17 automatic strengthening on
the augmented formula and replay all mappings and target witnesses.
If an empty clause is present or derived, record direct refutation
separately from template transfer. No result is credited solely on
search status. An unknown result proves neither SAT nor a lower bound.

## Controlled example

For each binary axiom C of a checked contradictory four-clause
template, replace it by (C OR z) AND (C OR NOT z), with a separate new
variable z per axiom. The original target has only ternary clauses,
so no subclause can witness a binary template premise. One resolution
wave derives all four binary premises; the template checker can reuse
the contradiction without a full resolution refutation of the target.
The isolated experiment requires template transfer, not a direct empty
clause. This is a designed positive control, not evidence of general
SAT complexity improvement.

## Run

    python -m mathos.research.pnp_semantic_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --knowledge artifacts/pnp-v16.json --analogy artifacts/pnp-v17.json --checkpoint artifacts/pnp-v18.json

Use the same inputs with --audit artifacts/pnp-v18.json for replay.
Generate upstream reports using their documented CLIs.

The experiment compares raw v17 strengthening against strengthening
after one implication wave using the same retained library and
per-template matching limits, on lifted positive controls, 24 new
seeded random CNFs and direct/negative controls. The augmented arm
gets extra inference work, so this is NOT an equal-total-budget
performance comparison. Measure both kinds of work, direct refutations,
template transfers, paired coverage and fresh outcomes separately.
Extra clauses can increase matching cost or cause a bounded search to
miss an earlier match. No improvement is assumed. The audit checks
upstream provenance, every credited consequence and transfer, reference
labels and aggregates; observed search counters are not authenticated.
Lean targets abstract resolution, lifted premise implication and
consequence preservation, not the Python implementation or its costs.
P versus NP remains unresolved.
