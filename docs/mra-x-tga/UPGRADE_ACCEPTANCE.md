# MRA-X upgrade acceptance
This opt-in extension does not change the original curriculum's acceptance policy or claim 10/10 maturity.

Run from the repository root:
    python tools/mra_x_upgrade.py --output upgrade-evidence.json

## Observed results (default 12 seeds per family)
- 156 fresh synthetic instances, 468 oracle/witness checks: all passed.
- Structural order selection: 30,989 candidate enumerations vs 31,933 for min-fill and 32,028 for the previous training-selected policy.
- 132 initial incremental runs and 1,056 factor-edit updates, all matched the exhaustive oracle and fresh fixed-order optimum, witness and trace.
- 95,422 candidate enumerations on updates versus 225,166 for full recomputation; 4,037 reused buckets. Initial setup excluded from both update totals.
- Registry scheduling of all 24 modules from reversed input; missing prerequisite, cycle and duplicate controls rejected.
- Original curriculum remains 18 passing labs and six open research obligations.

## Correctness argument (not mechanized)
At fixed domains and elimination order, every bucket projection is a deterministic function of the full multiset of input factors (including forbidden tuples and multiplicity), variable and boundary ordering. Cache keys compare complete input contents and domains, not merely hashes. A hit yields the same projection and deterministic backpointer as fresh computation; a miss recomputes both. Induction along the elimination order gives the same active factors and trace as full recomputation. Constant factors are still checked at the end. This argument assumes valid finite factor tables and intact cache state; it is not a Lean proof.

Order prediction simulates only factor scopes: the reference evaluates exactly d_v times the product of remaining boundary domain sizes at each step. Since min-fill is among the four candidate orders, selecting the smallest predicted enumeration count cannot increase that metric versus min-fill for the existing dense enumeration kernel. It does not bound actual runtime, planning cost or peak memory.

## Remaining work
- Integrate the new scheduler and solver into the curriculum's default execution path after review.
- REX-402/403: real physical single-tape implementation and equivalence.
- VER-603: pinned mechanized proof and axiom audit.
- OPT-703: mechanized cache correctness, larger/adversarial workloads, runtime and memory profiling.
- RES-802: matched external solver comparisons and independent reproduction.
- RES-803: governed autonomous code proposal, persistent cross-campaign learning, resource isolation and review.
No automatic merging, external solver performance or general mathematical discovery claim.
