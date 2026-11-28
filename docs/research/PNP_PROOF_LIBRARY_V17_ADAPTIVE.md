# v17.2 — adaptive proof fragment agenda

## Observed ablation (v17.1)

PR #283 merged at 08a80e560a3ddc73e436d7d72e4f9bca85c74631.
CI run https://github.com/tltmgnt/MathOS/actions/runs/46134106693 succeeded.
On 48 independent seeded cases (13 reference UNSAT), all four
whole-core arms matched zero. Original library exact composition
matched zero; original subsumption composition matched four.
Expanded exact composition matched nine (7/8 binary, 2/5 ternary UNSAT).
Expanded subsumption composition also matched nine (8/8 binary,
1/5 ternary), but gained one case and lost one relative to exact.
It hit 22 transfer limits; exact composition hit none. Aggregate
search/replay wall seconds were 3.888 exact vs 5.027 subsumption.
These are CI observations, not portable timing or proof of causality
beyond the paired experimental settings. Composition is important here;
subsumption is not monotonically better under bounded search.

## Proposed optimization

Keep the audited v17 expanded library unchanged. The adaptive agenda
prioritizes shorter conclusions, then smaller premise sets, then shorter
proofs. Dynamically select the next guard with the fewest compatible
clause witnesses; consider exact-width witnesses before stronger clauses.
Avoid transfers whose conclusion is already subsumed. Do not remove
original premises or derived clauses from the certificate. Retry a
template/mode only after the known set grows. Try exact matching first
each round; broaden to subsumption if exact matching adds nothing.
The policy can miss useful transfers: a subsumed conclusion may still
be useful to an exact matcher, an exact-first pass can consume resources
needed for subsumption, and dynamic filtering consumes work itself.
No completeness or efficiency claim.

All additions undergo the existing v17 verifier; the final signed
transfer recipe reconstructs and replays against original input under
the same cooperative budget. Each credited result also passes the
v17.1 independent residual-clause RUP checker and truth-table reference.
A separate report audit checks positive certificates, input provenance,
split identity and aggregates. Timing and negative search observations
are not authenticated. No new proof rule or solver fallback is added.

## Protocol

Four arms: existing exact composition, existing subsumption composition,
adaptive exact-only, adaptive exact-first with fallback. Same expanded
library, 4 rounds, 32 transfers, 4096 local candidate limit, 4 million
cooperative ticks, 100k cells, 15-second deadline; different search
implementations count local candidate operations differently.
Independent checking and report audit are separate from the search quota.
No hard process resource ceiling. Record paired gains/losses, status
counts, time, work and proof/recipe sizes. Compare separately by family.

Fresh 48 random CNFs (24 each binary/ternary) use seed 17203; reject
exact normalized duplicates against previous and upstream splits.
The prior 48 ablation cases (17103) are retrospective. Do not tune on
the new evaluation or admit any target-derived template. Public seeds
are not blinded and signed-orbit disjointness is not established.
This follows the v17 proof-library line without changing the separate
v18 unified or v19 guided inference research lines. Existing Lean
semantic obligations still apply; the agenda is not formally verified.
P versus NP remains unresolved. New experiment pending CI.
