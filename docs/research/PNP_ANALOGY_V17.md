# MathOS v17 — automatic certified mathematical analogy

v16 evidence and Lean CI passed. Seven input templates reduced to six.
Indexed exact retrieval attempted 34 versus 177 linear matches, but
matcher work was 2,411,851 versus 2,422,852 steps (only a small reduction).
Both matched six constructed controls and zero of 24 fresh cases.
v17 tests a broader sufficient contradiction-transfer relation.

## Method

For a checked contradictory template T, seek a signed injective map
of its variables into declared target variables. For each mapped template
clause C, require a normalized target clause D with D subset C. D entails
C, so every target assignment would satisfy every template premise,
contradicting the checked refutation. One target clause may serve multiple
premises. The returned certificate contains the mapping and all target
subclause witnesses. The independent v16 verifier checks them.

Search visits frequent template variables first; target active variables
before unused declared variables. For a partial assignment, a candidate
witness cannot use a target variable already mapped outside the clause
or with opposite sign, and its unmatched literals must fit into the
unassigned template variables of that clause. These are necessary
conditions, not sufficiency tests. At a complete map, require explicit
witnesses. Unused target variables can pad an injection. Each template
gets at most 4096 attempted signed assignments and a separate cooperative
budget. A miss or exhaustion is unknown. No completeness or polynomial
search bound is asserted for unrestricted inputs.

## Run

    python -m mathos.research.pnp_analogy_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --knowledge artifacts/pnp-v16.json --checkpoint artifacts/pnp-v17.json
    python -m mathos.research.pnp_analogy_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --abstraction artifacts/pnp-v15.json --knowledge artifacts/pnp-v16.json --audit artifacts/pnp-v17.json

The same retained v16 library is used for exact indexed retrieval and
automatic strengthening. Constructed controls strictly shrink one
longest mapped axiom per template; 24 separately seeded random CNFs
and two SAT controls are included. The isolated v16 strengthening control
now needs no supplied map. Independent exhaustive references check all
decisions. Both arms receive the same per-template match limit and
cooperative budget, but their pruning and candidate costs differ.
A bounded strengthened search may miss an exact match, so both directions
of disagreement are recorded. No assumed coverage improvement.

The audit checks upstream evidence, certificate witnesses, reference
labels, row coverage and arithmetic. Failed search and observed work
counters are not proof-certified. This is finite syntactic analogy,
not arbitrary logical implication discovery or a proof that P=NP.
Lean checks abstract clause inclusion and collective premise implication,
not the Python search or its cost.
