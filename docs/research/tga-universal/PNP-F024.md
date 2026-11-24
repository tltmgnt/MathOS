# PNP-F024 — Unrestricted SAT scope audit and exact hybrid reference

Baseline: F016 merge 11f119ad11de2f71654005abf84a556c4d3deb67. This is a
research branch, not a Millennium prize solution or canonical promotion.

## Results and scope

The existing disjoint AND-domain solver projects each pair independently to
one output bit; only affine constraints on those outputs couple the blocks.
Its classical mathematical decision problem is in P by Gaussian elimination.
F016 proves structural cost B(S) = 8S^3 + 26S^2 + 55S + 7, not machine time.
A polynomial many-one decision reduction from SAT to this nontrivial language
in P is equivalent to P = NP. It cannot be assumed as an engineering step.

The new Lean module proves closure of arbitrary GF(2) row systems under
ternary XOR, then rules out an assignment-preserving existential affine
encoding of OR3, even with arbitrary auxiliary lists. Witnesses for 100,
010, 110 combine to a witness for 000, a contradiction. This rules out
that relational encoding only, not arbitrary decision reductions. The
existing shared_projection/shared_clash theorems show independent projection
can fail when coordinates are shared.

The local nonlinear clause compiler retains two AND relations:
t = not(l1) AND not(l2), z = t AND not(l3), z = 0. Signed literals share
the original variables and their complements. For explicit n variables and
m clauses the Python compiler uses 2n+2m variables, n+m affine rows and 2m
AND gates. Sparse representation with binary indices is polynomial in
n+m; compactly renumber used variables first if an external input permits
large binary variable IDs. The Lean local equivalence does not yet certify
the full Python compiler.

## Exact hybrid solver

The experimental solver fixes the first operand of each AND gate, with k
distinct such coordinates. Every fixed branch turns each gate into z=0
or z=b. It adds the fixing equations and calls the F014 Boolean-cell affine
mirror. SAT returns original bits and checks the compiled assignment. UNSAT
returns one complete provenance vector per branch, in lexicographic order.
The independent checker reconstructs branch matrices and checks each weighted
row sum is 0=1; it checks the original CNF directly for SAT. Truncated or
altered dual vectors fail verification. No assumption of polynomial UNSAT
certificate size is made.

This exact search enumerates up to 2^k branches and stores their duals.
The F014 structural cost per branch is polynomial in the materialized
dimensions, but the total is potentially exponential. The Python mirror
also uses recursion and is not a machine refinement or a universal host
execution theorem. A supplied or constructible logarithmic backdoor is
sufficient for polynomial branch count, not guaranteed for unrestricted SAT.

## Acceptance

Run python -m unittest discover -s tests -p 'test_tga_proctor_unrestricted_scope.py' -v
and python -m mathos.research.tga_proctor_unrestricted_scope_audit --output-dir
artifacts/pnp-unrestricted-scope (one command line).
The audit requires Lean 4.14.0 and eight declarations with no axioms.
It checks 256 relations (52 affine including empty), 64 signed clause
assignments with exhaustive auxiliary witnesses, and 26 small formulas
against brute force and certificate checks. Actual report.json determines
acceptance; the expected counts are not a claim of executed CI.

## Integrated research dependency register

All recent machine and scope design outputs are consolidated below. F017–F022
are design/proof obligations, not completed kernel modules on this branch.

| Milestone | Concrete deliverable / acceptance gate | Status |
|---|---|---|
| F017 finite control | Fixed alphabet, fixed tape count, local deterministic transitions, actual counted traces, halt/reject distinction | Open |
| F018 serialization | D/R/semicolon/E grammar, width checks via unary counter, roundtrip, malformed rejection, S <= N <= 2S | Open except size algebra |
| F019 arithmetic | XOR/AND/copy/dot tables, prefix invariants, aligned n+1 scans, explicit seek/rewind | Open machine refinement |
| F020 elimination | Fixed-width zero prefix, immutable first pivot, partial row micro-invariant, full provenance and solution projection | Open machine refinement |
| F021 reconstruction | Reverse saved pivots, free variables zero, original domain lift, exact SAT/UNSAT wire | Open machine refinement |
| F022-A space | Bound visited regions, reuse scratch and pivot, triangular history, bounded counters; quadratic target | Open |
| F022-B time | Total halting, logical schedule O(N^3), per-operation overhead O(N^2), trace composition; conservative O(N^5) target | Open |
| F023 review | Independent reproducibility, formal axiom and machine trace audit | Open |
| F024 scope | Affine closure, direct encoding obstruction, local clause compiler, exact hybrid reference and negative controls | Candidate, CI gate |
| F025–F027 | Global consistency, factor graphs, bounded separators/treewidth, nonlinear backdoors; charge decomposition construction | Open |
| F028 | New unrestricted polynomial decision reduction or new general polynomial SAT algorithm (or separate P != NP route) | Fundamental open problem |
| F029 | Independent mathematical scope and complexity review | Open |

The serialized input design is D (bit bit)* ; records, then R records of n
coefficients and an RHS bit followed by ;, ending E. N = 1+2n+2r+2q+r(n+1).
No parser is implemented here. The proposed quadratic space and quintic time
targets require explicit transition-level region preservation and trace cost
bounds; no analytical allocation envelope alone certifies them.

## Full-prize gate

To claim P = NP, supply a uniform polynomial-time algorithm for all SAT inputs
with two-sided correctness and a polynomial bit/transition bound, or a
verified polynomial reduction into a known tractable language. For P != NP,
supply a general separation proof, not a lower bound on this particular
solver, projection method, expansion, or branch strategy. Finite regression
tests, formal scope obstructions, and parameterized tractability cannot
substitute for either breakthrough. No independent review, general SAT time
theorem, or prize resolution is claimed.
