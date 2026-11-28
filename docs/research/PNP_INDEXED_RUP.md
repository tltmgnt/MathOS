# Indexed RUP replay: failure-directed external UNSAT recovery

## Confirmed predecessor
PR #321 run 46157970533 succeeded: 191/191 archived, external
projected 19/40 vs coloring candidate 21/40, no paired losses.
Recovered flat125-85 (development) and flat125-52 (held-out).
Glucose4 40/40. Candidate work 2144627 vs projected 2260347;
solver call time 2809.763 vs 2389.702 ms, stored certificate bytes
19408 vs 15058. The two extra models account for new proof bytes.
Coloring only recovered 2/12 flat instances. All eight uuf50 and
one AIM SAT still unknown. No general superiority claim.

## Diagnosis on eight external uuf50 formulas
Connector-side independent JS transcription of frozen CDCL proposer
with counted budget, then two independent replay implementations
on identical chronological proofs. Actual fetched formula text, not
a local checkout or committed Python. All eight search proposals
completed within 100000; both checkers accepted all eight at a
separate high audit cap. Counts (search / scan / watched):

063 18035 / 100023 / 8620
0920 20787 / 117158 / 10494
0817 27381 / 175653 / 13670
0258 16192 / 89984 / 7705
0412 21274 / 112869 / 10233
0269 21068 / 111367 / 9932
0756 20815 / 111047 / 10585
0626 29360 / 165171 / 14252

Total search 174912, scan 983272, watched 85491. All eight
search+scan totals exceed the 100k envelope, all eight search+watched
totals below 50k. Scan costs omit the old checker's one-cell tick
per addition; watched counts include indexing and add ticks. Thus
replay is a strong causal hypothesis, not just search weakness.
Python CI must independently replicate the diagnosis.

## New mechanism
Independent persistent two-watched-literal RUP index. Each query
starts with a fresh assignment, negated candidate and original/
previously proved units. Only a checked addition enters the index.
Watch movements preserve the invariant across query resets (all
literals become unassigned). No search implication state is trusted.
The final empty addition is required, canonical non-tautological
clauses and existing size limits retained. SAT direct model replay.
The independent full-scan checker is also required in audit for
every credited result at 4M/15s; this additional check is outside
the 100k decision counter, as are existing portfolio audit passes.
This is not a new proof rule or full formalization of watch state.
Separate observed stage work and diagnostic replay caps recorded.
Repeated watcher scans, initial indexing and memory can dominate
small cases; no theorem of cost dominance.

## Protocol
New candidate probes at 50% of work/time for dense ternary
CNFs with 32–64 active variables, density 3.5–5.5, no recognized
XOR gate; otherwise unchanged coloring portfolio. Fallback gets
remaining budget. Gate chosen after observing development failures,
not claimed as blind; no tuning on eight new uuf50 cases selected
as next eight blob IDs in the pinned mirror. Original 40 retained.
Five arms: unchanged coloring portfolio, unchanged CDCL combined
budget, indexed standalone, integrated candidate, Glucose4. Same
100k MathOS and 5s wall envelope, separate audit. On 16 uuf50
cases also profile frozen search at 100k and both checkers at
4M/15s on the same proof; these are diagnostic only, not decisions
under the combined envelope. Require no paired losses and >=1
development gain, retain all 191 archived cases via separate
serialized paired audit. Report held-out misses unchanged.
Random watch-query differential tests and forged certificates;
no existing files modified or tests weakened. No modern industrial
or P vs NP claim. Actual integrated results pending CI.
