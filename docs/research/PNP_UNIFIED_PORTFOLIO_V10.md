# MathOS v10 — unified constructive and obstruction portfolio

This release consolidates certificate routes from v4–v9 rather than
introducing another isolated solver. It also corrects the v9 Lean
knownUnsat proof, which failed CI on the previous branch revision.
No proof of P versus NP is asserted.

## Run

    python -m mathos.research.pnp_general_frontier --checkpoint artifacts/pnp-v10.json
    python -m mathos.research.pnp_general_frontier --input cnf.json
    python -m unittest discover -s tests -p 'test_pnp_unified_portfolio.py' -v

Input: JSON object with n and signed integer clauses. A library caller
can use pnp_unified_portfolio.run(n, clauses, budget) and independently
verify_report(n, clauses, report, fresh_budget). The SHA-256 binds the
report to the exact validated input order and labels, not to semantic
equivalence classes. Resume restarts input.

## Transformation composition

A plan consists of one preprocessing profile and one decision route.
Default plans run every direct route on the original input, plus each
of three v4 preprocessing profiles followed by v9 recursive solving.
The library also accepts explicit combinations. Each preprocessing
artifact must be verified as equisatisfiable before its residual is
passed to a solver. The route proof is replayed on that residual, and
the complete chain can be independently checked on the original
input. Direct routes comprise v5 constant witnesses, 2-SAT, Horn,
renamable Horn and bounded cores; v6 triple parity; v7 affine,
bijunctive and conditioned mixed algebra; v8 component backdoors;
and v9 recursive AND/OR trees.

Each plan receives an equal non-borrowing share of remaining work
steps, with the same absolute deadline and logical cell cap. Earlier
plans cannot consume later plans' work shares, but time and memory
are not isolated. Exhausted plans discard partial proof artifacts.
The report does not certify elapsed time, memory, work counters, search
completeness or the heuristic quality of the chosen plans. Unknown
and exhaustion are not decisions. Any conflicting replayed decisions
or invalid internal proof triggers a diagnostic; there is no majority
vote on mathematical truth.

The report verifier checks the input fingerprint, plan list and
options, all credited transformation and decision artifacts, and
the final conclusion. It refuses unsupported universal claims.
It does not prove that a missing certificate could not have been
found. The executable frontier checks small controls against brute
force and records a separate v9 exclusive-scope obstruction, limited
to the static direct-algebra backdoor model. A depth-zero challenge
demonstrates an observed failure of one configured route on a
connected family member, not an obstruction to the full portfolio.

## Proof and complexity obligations

Lean targets abstract composition of equisatisfiable transformations,
lifting SAT and UNSAT decisions through them, soundness of the
three-valued decision lift, and impossibility of conflicting valid
decisions. These are generic logical facts, not a formal verification
of the Python implementations or the exact asymptotic cost bounds.
The v9 Lean failure is fixed using a separate Boolean negation lemma.
CI independently checks both files with an axiom-free policy.

For a fixed finite plan list, total work is bounded by the sum of
the component algorithms' costs plus replay. This does not prove
polynomial bounds when recursive depth or other parameters grow,
nor that any route covers every SAT instance. Operational budgets
do not establish a mathematical complexity bound. O10 (uniform
efficient transformation), O11 (algorithm-independent obstruction)
and O12 (exact universal formal proof) remain unresolved. The next
step is to use a fixed, reproducible benchmark and explicitly audit
proof coverage and cost across the accumulated mechanisms, not
infer universal progress from the number of supported classes.
