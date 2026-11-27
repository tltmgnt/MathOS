# F038-REX-024D6B — Prefix-ordered complete search and functional-root certificates

Parent 12a374e92da322c64f7c5c0158f9bda6e196dc39. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Prior verification

D6A exact-head [Proctor 46013057642](https://github.com/tltmgnt/MathOS/actions/runs/46013057642) completed all fifteen jobs successfully (audit, twelve physical replay jobs and two native descriptor jobs). The unrelated TOPO workflow was still running at initial inspection.

## Physical scope reordering

Keep the D6A complete conflict-prefix controller, 20 tapes, original D5S normalization and packed mask deposition. Reorder only the producer's loading schedule: pin/unary fields unchanged, higher-arity blocks ordered by maximum group index, then arity, then lexicographic scope. All blocks remain at their original physical storage indices. The worker's scope records and independent stream construction use this same order. Both GAC and candidate validation traverse this new order; bounded GAC may retain different domains than D6A, but sound deletions preserve every satisfying assignment. Full GAC is still monotone until stable. No external ordering hint or host-provided solution is used. This is a fixed natural variable order, not dynamic optimal variable selection or graph-component decomposition.

On failed candidate, the first violated factor has the smallest maximum coordinate among violated factors. The inherited D6A skip is sound; all candidates in the failed prefix block violate that factor. Moreover, all earlier proper prefixes satisfy every factor fully contained in them. Thus each failed candidate corresponds to an inconsistent child of a consistent prefix, and no failed prefix is visited twice. More precisely the sequence of complete candidate visits equals depth-first enumeration of prefixes that stops expanding at the first inconsistent prefix, extends that prefix with minimum surviving suffix values for the physical trial, and stops on the first valid complete assignment. This is established by induction on lexicographic successor blocks, under the genuine normalized-stream and correct producer/lowering premises. Neither arbitrary malformed-stream behavior nor unrestricted SAT completeness is claimed.

## Functional-root theorem

For each group j, call it determined if there exists a relation with maximum coordinate j such that, fixing the earlier coordinates of its scope, at most one rank of group j is allowed. A singleton/empty unary mask can be such a certificate. All other groups are called roots; let r count them. Extra constraints can only reduce feasible prefixes. If P_j denotes the number of consistent prefixes of length j, P_0=1 and P_j<=m^(number of roots among first j groups): a determined coordinate extends each consistent preceding prefix in at most one way, a root in at most m ways. Domains reduced by GAC cannot increase this count. Therefore the complete search visits at most

    C <= 1 + sum_{j=0}^8 m P_j <= 1 + 9 m^(r+1),

and always C<=m^9. The host certificate checks functional uniqueness directly in each relation. It does not change the physical machine or provide a bound for instances without the structural property. This generalizes the D6A special equality-star counting argument to any set of forward-functional factors in the natural coordinate order, with arbitrary additional restrictions. The number of roots is a sufficient certificate, not necessarily minimal under variable permutations.

Two infinite structural examples: one-root equality chain expressed through ternary masks with a late binary diagonal exclusion; two-root recurrence z_j=(z_(j-2)+z_(j-1)) mod m for j=2..8, with a separate ternary relation on (0,1,8) forbidding the recurrence-consistent tuple for every root pair except (m-1,m-1), or all such tuples in UNSAT variant. Since z_8=(13 z_0+21 z_1) mod m, exactly one global assignment survives in each SAT variant and none in UNSAT. The host oracle verifies both classes for m=2,3,4.

## Conditional physical resource accounting

Use inherited S<=L/16, L>=4096 m^3, N<=S+35m+1479<=2S. Same macro allowance as D6A: T<=131072 S(C+(full?m:1)), W<=(20N+12)T+6; producer 4P+32L, bridge 128S^2, projection 256S^2. For r=1 or 2 use C=1+9m^(r+1). Conservative total <=2^21 m^(r+1)L^2. Hence:
- at most one root: total <=8192 L^(8/3), conditional;
- at most two roots: total <=512 L^3, conditional;
- arbitrary normalized input: use C=m^9 and retain O(L^5) conditional ceiling.

For the root bounds, S>=1936 gives (20N+12)<=41S, C+m<=10m^(r+1) for m>=2 and r>=1; the worker contribution is <=41*131072*10 S^2 m^(r+1)+6, and the inherited producer/bridge/projection allowances fit the stated total. Conversion from m to L uses L>=4096m^3. Zero-root cases are included in the at-most-one-root class. These are source-level conditional resource derivations with finite arithmetic audit, not a machine-checked macro theorem, actual cubic admission, or a universal polynomial-time SAT result. No descriptor/admission threshold changes are made.

## Executed evidence

337 fixtures, 674 logical executions: 584 valid original witnesses, 90 exact UNSAT refusals. All matched the independent exact prefix-pruning host search. Independent ordered propagation and prefix DFS oracle matched 3664 actual candidate visits and 3080 failed scope records. 12 actual compiled producer replays independently matched the reordered stream. Twelve one/two-root fixtures have independently checked structural certificates. 20034 arithmetic evaluations per envelope (general, one-root, two-root), including large BigInt boundary cases. Of 576 paired accepted worker-clock comparisons against D6A, 528 improve, 48 regress, zero ties; eight further SAT runs have no D6A clock comparison. No correctness discrepancies found.

| Structural example | m | D6B SAT trials | D6B UNSAT trials | General Cartesian size |
|---|---:|---:|---:|---:|
| one root |2|18|18|512|
| one root |3|51|51|19683|
| one root |4|100|100|262144|
| two roots |2|29|32|512|
| two roots |3|128|135|19683|
| two roots |4|345|352|262144|

| worker fixture (alternating pins) | D6A clock | D6B clock |
|---|---:|---:|
| one-root m2 SAT |1318175920|809814344|
| two-root m2 SAT |1936329264|1258058776|
| original equality-star SAT |351921756|421919292|
| radius-three-last |242350926|300262472|

These are exact worker-clock accounting, not original-selector total clocks. The new order improves many fixtures but can delay a useful early failure or raise scan costs: it is not uniformly faster, including a regression on the old equality-star SAT instance. D6A remains a separate valid baseline.

## Actual original-format physical execution

Pins [0,0]. Both bounded and full modes ran original transition tables, exact quotient and one-transition-short cutoffs for both one-root m2 cases.

| case | physical t | head | span | witness |
|---|---:|---:|---:|---|
| SAT |847328722|46256|47092|0101010101010101011111111110000|
| UNSAT |834053928|38347|46937|blank|

SAT bridgeAt=35872799, workerAt=37019434, outputAt=846833460; worker 809814026, 78136 primitives, N=1977. Original clause validation and independent exact lex witness passed. UNSAT bridgeAt=35951305, workerAt=37097940, blankAt=834053927. Both modes reproduced exact clocks and terminal layout; cutoffs 847328721 and 834053927 TIMEOUT without witness. The combined two-root SAT original/quotient/cutoff interactive replay timed out at the tool level; no actual halt or cutoff claimed. Two-root logical audits and source-clock accounting passed. New workflow registers twelve original physical jobs (including both two-root cases), two independent native jobs with pinned one-root SAT/UNSAT fixtures, and audit/governance. Current-head CI unconfirmed.

## Descriptor accounting

No state-count or bit-length increase compared with D6A. Descriptor contents differ (scope order changes), despite identical lengths. Producer 287874, bridge 279, projector 74, blank halt 1; worker 2366458/2364178.

| mode | IR | original states | quotient states | bits | transition checks |
|---|---:|---:|---:|---:|---:|
| bounded |7500|2654686|1953203|148443432|7964058|
| full |7499|2652406|1951480|148312484|7957218|

Both quotients below 2^21; four-bit lowering unchanged. Online forbidden-only deposition, global structural decomposition and complete unrestricted reduction remain outstanding.

Next D6C: investigate physical forward-functional extension without scanning every failed child; build structural certificate admission and independent component decomposition or ordering analysis, verify D6B CI and preserve general completeness. Main and PR #248 untouched.
