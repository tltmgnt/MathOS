# v17.8 — utility-gated iterative knowledge accumulation

## Observed v17.7 result

PR #305 remains open at observation, but evidence CI passed:
https://github.com/tltmgnt/MathOS/actions/runs/46151907489.
Admission grew 30 to 54 templates. On 72 heldout cases (32 UNSAT),
both snapshots verified the same 23, with zero paired gains or losses.
Eight successful expanded recipes referenced an admitted entry.
Work increased from 7,119,705 to 11,741,174 ticks; aggregate
search/replay time increased from 4.4814 to 7.2245 s. Transfer-limit
outcomes increased from 33 to 38. Both snapshots verified zero of eight
ternary UNSAT. On discovery, expanded gained one (9 vs 8 of 14 UNSAT),
which did not replicate on holdout. The new library is useful in some
proofs but there is no heldout coverage or efficiency improvement.
These observations motivate selection, not unconditional accumulation.

## Method

Two epochs of offline training and discovery. Train on 18 independent
cases using only the current immutable library, reconstruct source
proofs, and call the existing admission checker. It proposes at most
24 additional fragments with audited lineage. Build up to four
deterministic equal-size cohorts (six candidates or fewer): first,
serialized compactness, short/low-guard goals, and nonempty low-support
consequences. Preserve incumbent entries and original order; deduplicate
identical snapshots. Always score the unchanged incumbent too.

On the epoch's distinct 18 discovery cases, require every incumbent
verified refutation to remain verified. Select a cohort only if it
adds a verified refutation or decreases total counted work without
losing coverage. Rank eligible proposals by coverage, work, size and
name. Otherwise abstain. This is a finite empirical gate, not proof of
dominance. Training epoch two starts from the accepted first snapshot,
so it may leverage earlier admitted knowledge; it need not accept
anything. Discovery labels never generate candidate proofs or enter
the library. The same discovery set is not reused in epoch two.

After both gates freeze three libraries: original base, union of both
generated pools (digest-deduplicated), and gated result. The ungated
union is a comparator over the same generated pools, not a separately
trained ungated feedback trajectory. Gated adds at most 12 fragments.
This design does not isolate library size from cohort selection or
guarantee a positive result.

## Protocol and audit

Fixed seeds 17801/17802/17803/17804 for training/discovery pairs;
17805 for the final 72 heldout cases. Each split equally stratified
by random binary, ternary and mixed widths. Exact normalized overlap
rejected against known prior and upstream splits. Public seeds, not
external blinding or signed-orbit disjointness. No final-test tuning.

Use identical per-arm cooperative search/replay caps of 4M ticks,
15 seconds, 100k cells; offline work separate, independent replay
separately timed. Positive audit checks the training certificates,
reconstructs each pool and lineage, checks discovery and heldout
certificates, checks the gate from recorded scores, and rebuilds all
snapshots and aggregates. It does not authenticate misses, timing,
or operation counters. The gate may be influenced by bounded search
or measurement; no hard CPU/memory limit or implementation-level
formalization. No new inference rule or theorem. P versus NP unresolved.

Stacked on PR #305 (not merged when this was authored); merge/rebase
that dependency before merging this follow-up. Evidence CI pending.
