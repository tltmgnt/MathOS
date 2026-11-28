# MathOS v17 — bounded reusable propositional proof library

Research branch; evidence status: implementation and experiment protocol, not a
validated positive coverage result. No claim about P vs NP, theorem novelty,
unrestricted abstraction, or asymptotic improvement.

## Why v15 missed

v15's documented experiment uses 16 fresh random pure 3-CNFs and a library
built only from selected v13 training refutations. Its matcher requires a
signed injection of an entire contradiction's explicit axioms with exact
clause widths and membership. The 4096-assignment limit and static
variable order can also prevent discovery. Compression removes redundant
records but does not canonicalize up to signed permutation, extract usable
nonempty conclusions, or allow a target's stronger clause to discharge an
axiom. A fresh SAT case cannot be matched soundly at all.

These are code-level restrictions, not established per-instance causes.
The retrospective report replays the same 15015 seed, records per-template
candidate counts, width sets and resource statuses, and compares the
clause-driven exact whole-core matcher on the original source library.
A miss after either bounded search is not evidence of nonexistence.

## Trust boundary

The library stores guards and RUP-checkable inference sequences from verified
v15 resolution dependency cones. A fragment is a conditional entailment,
not an unconditional theorem. The exact small canonical form enumerates
signed permutations up to four variables, sorts axiom sets and labelled
resolution DAG edges, and preserves the conclusion. Larger patterns use
labelled keys; no complete graph-isomorphism result is claimed.

The matcher explores signed injections by clause alignment, with optional
target-clause subsumption (target clause is a subset of mapped premise).
The width-posting index is a necessary filter only. Search limits are
heuristic. Composition adds checked fragments to the current premise set;
it never invokes a target solver to receive reuse credit. Every transfer
checks its signed injection, guards, and RUP derivation; the complete
flattened proof is independently replayed against the original CNF. RUP
means unit propagation refutes the current CNF plus negation of the
proposed clause. Only an explicit checked empty clause credits UNSAT.

Dependency cones are syntactically trimmed, not globally minimum. On small
contradiction guards, premise-deletion candidates are tested by exhaustive
countermodels. A witness causes retention; absence of a countermodel is
insufficient unless all proof additions also replay under the weaker guard.
Retained guards with actual witnesses have locally necessary premises at
that stage; replay-blocked deletions do not establish semantic minimality.

Lean statements cover semantic signed literals, subsumption, composition,
checked strengthening and empty-clause refutation. They do not establish
correctness of the Python RUP implementation, the search, or completeness.
Randomized and adversarial tests supplement, rather than replace, proofs.

## Experiment protocol

* Original training: audited v13 selected refutations (same v15 source).
* Additional training: seed 17001, 12 pure 3-CNF and 12 random 2-CNF cases.
  Independently propose proofs on those inputs, verify and compress before
  admission; freeze the resulting library and its hash.
* Discovery: seed 17002, 8 of each family; diagnostic only, no library update.
* Retrospective: original v15 seed 15015, 16 pure 3-CNF cases; not holdout.
* Held-out: seed 17003, 16 of each family. No target-derived proof templates,
  injected contradictions or renamed copies are generated. Exact normalized
  input duplicates across splits are rejected. This does not exclude signed
  isomorphs or establish independence of the underlying distributions.
  Seeds are fixed and public; this is not a blinded external benchmark.

Random 2-CNF is included as a separate easier family, never pooled to
imply progress on 3-CNF hardness. Compare both methods on the same cases
and report total and UNSAT denominators, verified counts, misses, budgets,
work and elapsed time. Reference truth is computed separately after
search. v15 uses only the old library; expanded training plus fragments
confound any overall coverage difference; the retrospective comparison
is a partial matcher ablation only. Work counters are implementation-specific,
not machine-independent operation counts; elapsed time includes verification.
Recipe bytes depend on the frozen library; report library bytes, expanded
certificate bytes and standalone template-plus-recipe bytes, rather than
claiming compression from recipe size alone. Library construction and
additional training costs are reported separately.

Run from repository root (with audited upstream artifacts):

    python -m unittest discover -s tests -p 'test_pnp_proof_library.py' -v
    python -m mathos.research.pnp_library_frontier --benchmark artifacts/pnp-v11.json --scheduler artifacts/pnp-v12.json --failures artifacts/pnp-v13.json --checkpoint artifacts/pnp-v17.json
    lean -DwarningAsError=true formal/PnpProofLibrary.lean

CI is intended to produce evidence; no numbers are asserted before
execution. The research target is at least one independently verified
held-out match; zero matches are a valid negative experiment, not a
reason to change the held-out split. Further work: blinded external
benchmarks, stronger indexing, complete canonicalization, an end-to-end
formal RUP checker, provenance per fragment and audit of negative search outcomes. The positive-claim report audit independently regenerates the library, rechecks training embeddings and credited target certificates, and checks aggregate counts. Timing and missed-search claims are not certified.
