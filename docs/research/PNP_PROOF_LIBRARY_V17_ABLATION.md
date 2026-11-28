# v17.1 — controlled proof reuse ablation

## Observed v17 milestone

PR #279 merged at 6d6eb6bd2efea00a225f9802b60cce8787ca759a.
The evidence and formal jobs passed in
https://github.com/tltmgnt/MathOS/actions/runs/46133376858.
The evidence job reports six passing Python tests, 8/32 verified held-out
refutations (8/10 reference UNSAT), 2/16 random 3-CNF (2/4 UNSAT),
6/16 random 2-CNF (6/6 UNSAT), and three composed held-out refutations.
The v15 baseline had zero matches, and the retrospective old-library
comparison had zero for both on the original 16 cases (5 UNSAT).
14 held-out cases hit the transfer cap. The measured v17 held-out
search/replay wall time was 2.1332 s vs 0.0080 s for v15. The byte totals
were 1572 recipe bytes, 3077 expanded bytes, 18094 standalone bytes;
the library storage is not included in recipe bytes. These are observed
CI logs, not a separately downloaded artifact replay. The improved
coverage is not attributable to a single mechanism yet.

## Next experiment

Use an audited v17 report to freeze the original and expanded libraries.
Run a factorial 2 x 2 x 2 ablation: original/expanded training library,
exact/subsumption matching, and whole-contradiction/fragment composition.
This compares eight arms on each case, not eight different case samples.
Use fixed shared per-arm cooperative search and reconstruction limits:
4 million ticks, 100k cells, 15 seconds. The existing v17 defaults remain
unchanged. Record CPU and wall time, observed work, status distribution,
proof/recipe bytes, and matched-pair gains and losses at each factor.
Independent replay is separately timed and not charged to the common
search quota. No hard process memory limit or portable operation-count
claim; cooperative accounting is incomplete.

Fresh split: seed 17103, 24 random 2-CNF and 24 random 3-CNF cases,
generated without consulting templates. Reject exact normalized duplicates
against upstream training/evaluation and v17 split inputs. This is not
signed-orbit disjointness or external blinding. Repeat the prior 32 held-out
cases only as retrospective diagnostics, not as new holdout evidence.
No tuning, fallback solver credit, or library admission occurs during
evaluation. Rotate arm order by case hash.

Independent checker uses residual CNF simplification under negated clause
assumptions, rather than the original assignment-set propagation
implementation. Every credited proof must pass this checker and an
independent exhaustive truth-table oracle for its small target. These
checks do not formalize the Python verifier. The existing v17 Lean
semantic obligations remain in force. Unknown outcomes are not SAT results.

The new experiment is pending execution. No causal performance result is
asserted yet. Library size and content both change with training expansion;
composition and subsumption effects may interact under bounded search.
P versus NP remains unresolved.
