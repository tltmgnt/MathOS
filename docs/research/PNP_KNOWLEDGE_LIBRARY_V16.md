# MathOS v16 — certified mathematical knowledge library

v15 passed computational and Lean CI. On two historical refutations,
compact JSON proof+embedding occupied 719 bytes versus 1847 original
proof bytes; both had 26 derived steps in total. Participating axioms
were 24 versus 68 normalized source clauses. Both constructed signed
variants matched, but none of 16 fresh cases matched (five were UNSAT).
The lack of fresh matches is important: proof abstraction does not
automatically produce broad theorem coverage.

## Contract

Build a finite content-addressed library of independently checked
resolution templates. Index by active variable count and multiset of
axiom widths. For exact signed injective inclusion these are necessary
conditions, not sufficiency tests. Sort by size then digest. If an
already retained contradiction embeds into a later template's axioms,
record its exact signed mapping and omit the redundant template from
retrieval. This guarantees coverage of the omitted template under the
specified embedding relation; the bounded search need not find every
redundancy. The verifier checks all original candidates, their order,
dispositions, retained records, signatures, and coverage embeddings.
The library artifact is serializable JSON, with provenance supplied by
the upstream audited source. It is not canonical under variable
renaming or a minimum proof library.

A separate strengthening verifier accepts a supplied signed injection
and one target subclause per mapped axiom. A clause with fewer literals
entails the larger mapped clause. Every witness must be present in the
normalized target. Thus the contradictory premise is still entailed
even when exact inclusion fails. A helper finds witnesses for a
supplied mapping; automatic strengthening-embedding discovery is not
implemented.

## Run

    python -m mathos.research.pnp_knowledge_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --checkpoint artifacts/pnp-v16.json
    python -m mathos.research.pnp_knowledge_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --audit artifacts/pnp-v16.json

Generate upstream reports using their existing CLIs. Default experiment:
historical v15 templates, four synthetic templates, one deliberate
duplicate, constructed renamed positive controls, 24 fresh seeded
CNFs, two negative controls, and a supplied-map strengthening control.
Compare indexed vs linear traversal of the SAME retained library,
with identical order and per-template limits. Count attempts and
observed matcher work steps; index construction, query bookkeeping
and external replay are excluded. This is not a comparison with
fresh resolution search or wall time. Constructed controls are not
independent evidence of generalization. Fresh unmatched cases remain
unknown, even when the reference knows they are SAT.

Audit checks source, library coverage, reference decisions, skip
conditions, every credited match and summary arithmetic. Failed
searches and observed work are not proof-certified. Bounded matching
can be exponential in general, and no theorem of coverage is claimed.
Lean targets abstract premise strengthening and composition only.
All P versus NP obligations remain unresolved.
