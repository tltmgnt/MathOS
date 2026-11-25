# F035/F040 — Deduplicated discovery and checked unit fast path

PNP_RESOLUTION_STATUS = OPEN.

Based on verified executable discovery cd5c39f2b521289d95bbf635e3b69812100e34b1,
PR #242 merged; run 45640886640/job 139298868953 (15 zero-axiom declarations,
25 controls). The new candidate computes a duplicate-free variable list
by tail-first membership filtering. The two membership directions,
distinctness and identifier range are preserved. The existing exhaustive
construction applies to the resulting coverage list without changing
the accepted proof language. The checked contradictory-unit fast path
tries an explicit one-step certificate and falls back to deduplicated
exhaustive discovery if the candidate does not pass boundCheck.
Soundness and completeness of the combined decision are explicit targets.

The padded family from the exhaustive size obstruction has only one or
two distinct variables. The deduplicated generator should return 3 or 7
batches respectively, while the checked unit contradiction needs one.
These exact family counts are executable controls, not a new universal
size theorem. The general generator still has an exponential tree in
the number of distinct variables. Neither deduplication nor a verified
fast path implies a polynomial worst-case bound.

14 candidate declarations, 46 controls (25 prior formula cases and
21 padded inputs). Strict Lean 4.14.0 warnings-as-errors and explicit
zero-axiom gate. Marker F035_DEDUPLICATED_DISCOVERY_OK pairs=16 singles=4 empty=2 sparse=1 duplicates=2 padded=21.
Fresh exact-head replay required. No main changes.
