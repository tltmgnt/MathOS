# Incremental native XOR state and source-row pruning (stacked draft)

## Prerequisite gate is not yet green

PR #307 (native Gaussian CDCL) was still open at inspection.
Run 46151989241 formal job failed the existing no-axioms gate:
two simp_all proofs depended on propext. Replaced them on the
parent branch with constructive Boolean case proofs, retaining
the theorem statements and the no-axioms gate. Evidence and
new formal run not yet verified. The incremental PR is stacked
on that parent, not main. Neither is to merge before its evidence
and review. No native end-to-end results are assumed.

## Incremental invariant

Maintain an RREF basis of the implied XOR system restricted
to the processed trail prefix. Each row stores restricted mask,
restricted RHS, full mask and source-row provenance. An inverted
index maps a variable to affected pivots. Assigning a nonpivot
deletes its column in affected rows; assigning a pivot removes
that pivot row and inserts its restricted remainder, clearing the
new pivot from other rows. A zero row with odd RHS is a conflict.
The complete reduced basis exposes all forced free literals.
Reversible row changes, previous conflict and trail bit masks
restore the exact earlier state when a trail suffix is removed.
Conflicting prefixes can ignore a later suffix until rollback.
Logical cells and every indexed row change are budgeted;
this is not a process-memory or hard wall-time bound.

Native explanations use unchanged original-source XOR checks
and chronological RUP replay. Optional state factory and proof
transform hooks leave default native search unchanged. Pruning
keeps only source rows cited by some XOR event, remaps indices
in chronological order, and retains one row for a RUP-only
certificate (existing schema). It does not minimize the proof
or remove learned clauses. The resulting proof is checked by
the existing native verifier, not a new trusted verifier.

## Actual local helper experiment

Exact helper algorithm transcribed locally with a simple counted
Budget stand-in; native recomputation transcribed separately.
600 seeded random systems on 3–8 variables, 30 trail extensions
or rollbacks per system, seed 192309: all 18000 states agreed
with exhaustive reference and recomputation, including 9966
conflicts and 12078 forced literals. Every explanation checked
against independent XOR parity/support logic after serialization.
Counted steps 203754 incremental vs 302106 recompute.

Sparse independent ternary blocks, append/rollback/rebranch:
16 rows (48 vars): 2937 vs 4696 steps;
32 (96 vars): 10737 vs 18352;
64 (192 vars): 40929 vs 72544;
96 (288 vars): 90577 vs 162576.
Initialization and undo included, replay outside scan counters.
These are helper-level counts, not actual CDCL or wall-time
improvement. Repository checkout unavailable locally.
No new integrated coverage or proof compression measurement yet.

## Frozen ablation

Use identical parent 191-case manifest, no retuning or expanding
the suite. Five arms at 100000 cooperative steps/5 seconds:
native recomputation, incremental raw, incremental pruned,
native portfolio, opt-in incremental portfolio. Same 20% probe
and same fallback. Compare paired loss/gain, source row counts,
certificate bytes, elapsed time and work; independently replay
every credited result. Require no paired portfolio losses and
at least one strict paired source-row reduction. This does not
replace the parent native evidence gate or establish superiority.
No changes to previous default routing or tests. Public synthetic
suite, no blind/industrial evidence. Lean local restriction and
undo lemmas only, not full mutable-state correctness.
