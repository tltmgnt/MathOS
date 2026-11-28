# Indexed branching, monotone conflict traversal, and quota ablation

## Confirmed indexed replay prerequisite
PR #326 head cf9fe248 run 46159517288 passed the evidence and
191/191 archived paired gate. It remains open at preparation.
48 external cases: 21/48 baseline, 36/48 candidate (13 SAT,23
UNSAT), zero paired losses; Glucose4 48/48. Indexed standalone
33/48. All eight original random UNSAT recovered, seven of eight
new random UNSAT recovered; standalone indexed at full budget
solved all sixteen. uuf50-0207 search 41887 + replay 20371 =
62258 steps, greater than the portfolio's 50000 probe quota.
This is a measured allocation obstruction, not a missing inference.
Total candidate work 1926180 vs 2934476, solver calls 2512.473
vs 2483.924 ms, certificate bytes 30553 vs 19408. Extra decisions
produce extra certificates. All credited certificates replayed.
Original uuf50 full-scan replay 983590 steps vs indexed 85491,
same search 174912; exact Python repeats earlier JS diagnosis.
No wall-time timeout or replay exhaustion. Compiled reference
remains superior in coverage and overall measured time.

## Actual exploratory AIM diagnosis
Connector-side independent JS transcription (not repository checkout)
on the four original AIM SAT inputs. The 200-variable 680-clause
aim-200-3_4-yes1-3 fails at 100k under base, binary-weighted,
polarity-weighted, activity-decay, and combined variants. Other
three solved in all tested variants. The large formula contains
37 direct same-residual opposite-literal clause pairs. Short
resolution + binary reachability produced 37 shorter clauses, zero
forced units, residual 639 clauses, 26330 counted steps; no model.
Blocked clause elimination removed zero at 13700 steps. Negative
results retained; neither mechanism proposed for routing here.

The exact frozen branching heuristic, with full search/replay of
SAT model, at diagnostic 1M budget gave the following actual
transcribed counts on large AIM:
- frozen: 421928 steps, 280 conflicts, 552 decisions;
- monotone trail cursor only: 309870 steps, same trace counts;
- score bucket only: 340586 steps, same trace counts;
- both: 228528 steps, same trace counts.
All four still UNKNOWN at 100k. No claim of recovering AIM at
the original budget; high-budget diagnostic is separate.

## Implementation
Separate opt-in copy of frozen deterministic CDCL proposer.
Unassigned variables are grouped by integer activity score;
assignment removes, backtrack restores with updated score.
Maximum nonempty score bucket is selected, minimum variable
ID breaks ties exactly as before. Activity bumps occur on assigned
conflict literals, so no live bucket change is needed until undo.
Conflict analysis resolves the latest current-level trail literal;
its implication reason introduces only earlier trail positions,
so a descending cursor need not rescan later trail positions.
Same branch, propagation and conflict rules; no restart or heuristic
change. No proof rules added. Every decision uses indexed replay
and old independent full-scan checker at unchanged audit caps.
Default indexed attempt and diagnostic APIs unchanged except optional
proposer argument. Logical-cell guard includes bucket count, not
actual process memory. Full mutable search not Lean-formalized.

## Matched design
56 pinned external cases, prior 48 plus next eight uuf50 blob IDs.
Seven arms: old indexed portfolio (50%), optimized search 50%,
frozen search 2/3, candidate optimized search 2/3, frozen and
optimized standalone at 100k, and Glucose4. Same overall 100k/5s
envelopes and existing dense ternary gate, unchanged coloring
fallback. Separate 1M/5s diagnostic search on AIM SAT and all uuf50,
independent 4M/15s replay; no diagnostic counts credited at 100k.
When both diagnostic proofs exist, require exact identical result
objects. No paired portfolio loss, known allocation gap uuf50-0207
recovered, at least one matched strict search-work reduction, and
all 191 archived preserved. Fresh instances selected without
executing them. Prior held-out 0207 is now a development case.
No new Lean theorem because no inference rule change; randomized
proof equality and exhaustive checks test implementation, not
a formal proof of equivalence. Existing tests retained.

The new branch is based on verified but unmerged #326, with a
main-target draft PR explicitly dependent on #326. Do not merge
into the prerequisite research branch. Full integrated evidence
pending CI; no modern industrial superiority or P vs NP claim.
