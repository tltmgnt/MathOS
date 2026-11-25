# F035/F040 — Binary-square discovery and residual distinct-variable obstruction

PNP_RESOLUTION_STATUS = OPEN. Candidate only; strict exact-head Lean replay required.

Independent branch based on merged PR #242 (verified head
cd5c39f2b521289d95bbf635e3b69812100e34b1; merge
d06767910dccb30121c16665018866391312b2e3). The pending
deduplicated-discovery branch is deliberately not an ancestor.

For k >= 0, let G_k consist of the four binary clauses
(x1 or x2), (not x1 or x2), (x1 or not x2),
(not x1 or not x2), followed by (x1 or xi) for i=3,...,k+2.
All rows are binary, distinct, non-tautological; there are k+2 distinct
variables and k+4 clauses. No contradictory unit fast path can trigger,
and ordinary unit propagation has no initial unit. The four core rows
already imply UNSAT.

Conditional mathematical size analysis of the pending deduplicated
generator: on successful exhaustive construction, its build recurrence
T(0)=1, T(d+1)=2T(d)+1 gives exactly 2^(k+3)-1 batches.
The distinct-variable obstruction does not depend on duplicated
occurrences. This is an algorithm-specific count, not a formal theorem
in this branch and not a lower bound on all certificates.

The binary-square candidate finds four exact ordered rows by their
original indices. Batch 1 derives (x2) and (not x2) in parallel on
pivot x1. Batch 2 resolves those two rows on pivot x2 to the empty
clause. Exactly two batches, three inference steps, no copies of
irrelevant input rows. The bound checker validates the original input,
including its ordered rows and variable bound. A certificate with
constant inference count is not a constant-byte envelope or a
constant-time discovery claim.

The candidate scan is intentionally limited to an exact ordered
four-row pattern, not a general 2-SAT decision procedure. Rejected or
missing proposals fall back to the verified exhaustive generator and
check its proof before returning it. The API returns Option Proof,
retaining the accepted certificate rather than only a Boolean.

Eight public candidate declarations: square_shape, square_certificate,
atPair_complete, checked_sound, checked_complete, discover_accepts,
discover_complete, discover_iff. The atPair theorem covers an explicitly
supplied ordered variable pair; universal fast-path completeness of
scan for arbitrary row orderings/literal permutations is not claimed.
The combined fallback completeness is for valid typed formulas.

46 executable controls targeted: 16 binary core subsets, 4 single-variable
subsets, 2 empty cases, 1 sparse large-ID core, 21 padded cases, and
2 negative controls (changed input and bad reference).
The strict workflow checks Lean 4.14.0, warnings as errors, eight
zero-axiom declarations and the exact fixture marker. No verification
credit until a successful replay at the exact branch head.

The original input-bound checker is unchanged. No change to main;
no PR until exact-head verification. Integration with deduplicated
discovery and a general unit-propagation or implication-graph path
remain future work. Universal serialized completeness, total bit cost,
polynomial certificate size and polynomial discovery remain open.
