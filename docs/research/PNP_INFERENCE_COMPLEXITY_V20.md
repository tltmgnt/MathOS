# MathOS v20 — exact restricted inference bounds and escape certificates

v19 passed computational and Lean CI on main (46135099462). On 24
fresh cases (five UNSAT), one-wave transfer decided one, full multi-wave
and compact multi-wave each decided two. Compact matching used
13,484,927 steps versus 24,846,189 for full matching, with 1,243
versus 6,035 retained clauses across the suite. Compaction itself used
416,449 steps and multi-wave inference 878,975. These are finite
observations, not asymptotic bounds.

## Family A: exact resolution depth

For every n >= 1 define

    F_n = x1 AND (NOT x1 OR x2) AND ... AND
          (NOT x_(n-1) OR x_n) AND NOT x_n.

This formula has n+1 clauses, n variables, and 2n literal occurrences.
It is minimally UNSAT: removing clause j (indexed 0 through n) admits
the assignment x_i=true iff i<=j. Every sound refutation using only
these original axioms must use all n+1 of them. A binary resolution
DAG of root depth d (axioms depth zero, inference depth one plus maximum
parent depth) unfolds to a binary tree with at most 2^d leaves, hence
has at most 2^d distinct reachable axioms. Consequently any such
refutation needs d >= ceil(log2(n+1)).

Conversely, balance the n+1 consecutive clauses as a binary tree.
Resolve adjacent interval summaries on their boundary variable.
The summary is a binary implication for an interior interval, a
unit for an interval touching one endpoint, and the empty clause
for the full interval. There are n inference records, derived width
at most two, and depth ceil(log2(n+1)). The executable construction
and independent v13 verifier check the upper witness; the deletion
witness verifier checks minimality on each bounded family member.

Thus the lower and upper bound match for the family, not merely for
one heuristic. The mathematical argument holds for arbitrary n;
the software is capped at n=256. At most four waves cannot directly
derive the empty clause for n>=16, regardless of work quota or
ordering. Other caps can prevent success even for n<=15.

**Escape:** every F_n is 2-CNF; the existing certified 2-SAT route
decides it without a depth-limited resolution search. This is a
restricted proof-model limitation, not a SAT lower bound. The v19
template-transfer route is also outside the direct-depth claim.

## Family B: exact derived-width threshold

Let G_k contain all 2^k full-width clauses over k variables, one per
sign pattern. Each assignment falsifies one clause, so G_k is UNSAT.
A non-tautological first resolution step must resolve two clauses
whose signs differ only at the pivot. All remaining k-1 literals
survive. If the permitted derived width is less than k-1, no first
non-tautological inference is possible. The verifier checks the
complete cube and its pairs for supported k<=9.

Conversely, resolve pairs differing only on the first variable.
The resulting clauses form the full sign cube on k-1 variables.
Repeat; at most k-1 derived width suffices. The implementation checks
a v13 ascending elimination refutation and its actual maximum width.
The input itself has exponential size in k, so this is NOT an
exponential lower bound as a function of input size. It only
establishes a precise threshold for this derived-width model.

## Run and audit

    python -m mathos.research.pnp_inference_complexity --checkpoint artifacts/pnp-v20.json
    python -m mathos.research.pnp_inference_complexity --audit artifacts/pnp-v20.json

The default experiment sweeps nine chain sizes (1 to 255) and six
cube sizes (3 to 8), all four v19 depth caps on each chain, and
a width-blocked wave plus a boundary-width wave where v19 allows it.
All known refutations have independently replayed certificates.
The report distinguishes theorem-based obstruction from heuristic
unknown/exhaustion. Search work counters are implementation-specific
observations, not proof-certified or hard CPU/RSS bounds. No curve
fit or extrapolation is used to establish either mathematical bound.

Lean targets a binary tree leaf-capacity lemma and abstract necessity
of a premise with a deletion witness. The full chain/cube family
arguments, DAG unfolding and Python implementation are not formalized.
E08 evidence remains scoped to this model; the outcome registry and
all universal obligations remain unresolved. No novelty claim is made.
