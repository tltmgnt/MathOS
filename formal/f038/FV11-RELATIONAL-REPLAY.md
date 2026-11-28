# FV-11 — Certified relational operation-log refinement

Status: authored implementation committed; executable audit PASS; Lean compilation and expanded axiom gate PENDING.
FV-10 exact checkpoint 87f61040754c5eb0ace8af518aaa803548812d83 passed Proctor run 85 (132 named theorems).
PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE.

## Mathematical scope

RelationalReplay.lean introduces a typed targeted semijoin replay: check the two factor indices, distinct endpoints, nonempty overlap, nonempty claimed deletion and equality of the claimed row set with the computed unsupported rows. Replace only the target factor. The intended pointwise equivalence theorem preserves the entire model set for every accepted finite log. Output comparison uses the FV-10 factor-set equality checker; it permits factor order and duplicate differences, so does not assert byte-identical producer output. Exact model preservation does not require reaching a fixed point. The independent existing D7A JS checker additionally checks fixed-point closure or an empty relation, exact output order and the producer's row deletion order; these stronger procedural properties are not claimed formally verified here.

The bounded derived-factor entailment check covers both scopes and enumerates the supplied local support; an added factor must be true on every local assignment satisfying its source factor. A checked addition preserves all models. The kernel also states empty-factor UNSAT soundness and exact composition of checked closure with FV-09/FV-10 affine reconstruction and simplification.

## Executed evidence

The audit loaded the actual committed D7A closure, independent D7A certificate checker, D7B closure and FV-09/FV-10 export modules. For 128 deterministic random inputs, exhaustive assignments were checked for pointwise preservation both after actual closure and after actual derived-pair additions.

| Check (random inputs) | Result |
|---|---:|
| Instances | 128 |
| Original satisfying assignments | 793 |
| Independent row comparisons | 6170 |
| Rows deleted | 457 |
| Deletion events | 247 |
| Closure contradiction outputs | 19 |
| Derived factors | 3 |

Six corrupt log/output controls were rejected by the independent JS verifier. Five named actual fixtures cover a two-deletion chain, a two-deletion contradiction, an initially empty factor, an unchanged fixed point, and a derived pair. A sixth generated Lean source composes actual chain closure with actual D7B affine elimination to a zero-free padded residual. All six sources were generated successfully; Lean acceptance is still pending. The random comparisons are finite test evidence, not universal JS verification.

## Verification gate

The Proctor compiles RelationalReplay and its tests, the six generated sources, reruns all eight executable audit suites, and expands the strict static named theorem inventory to 143 (nine kernel and two fixture theorems added). Generated theorem dependency reports are separate in the compile log. No new theorem is claimed verified before a successful build.

## Remaining obligations

The D7A iteration combining rank/permutation quotienting, relational closure and derived-pair additions still requires a concrete quotient/round-chain proof; the local addition reference checker does not formalize the producer's permutation selection or complete fixed-point algorithm. Universal JS parsing/refinement, affine constant-conflict and wide fallback paths, physical compiler/selector/clock semantics, full resource bounds, and independent human review remain open. No production integration or main promotion.
