# F038-REX-024D7G — Certified alternative disjunction derivations

Parent D7F: 67e9d4b1e5220e989b176c151882ec5d571729ab. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4; Omega obligations 0/6.

## Exact inference and certificate interface

For a common polarity, start from a nonempty original clause C of that polarity. If p belongs to C and an original axiom B contains exactly one opposite-polarity literal -p, the resolvent R=(C without p) union (B without -p) is an implied clause of the same polarity. Retain its full ordered source-axiom chain. The D7E independent checker already verifies these steps, the exact final disjunction, group disjointness, capacity exclusions and Hall deficiency. No new axiom or unverified weakening is used.

D7G exposes an optional group-proposal callback in the inherited Hall and D7F partition interfaces, leaving the default path unchanged. A group proposal must be nonempty, of the current polarity, and disjoint from all other proposed groups; the independent checker still verifies its proof if a Hall contradiction is produced. First run the original D7F policy. Only if it returns UNKNOWN, use the alternative extraction portfolio. No result from a successful matching is treated as an original SAT witness.

## Bounded alternative exploration

For each polarity and source start, track a canonical signed option set, proof, and set of used pivots. Expand the first eligible unused pivot through every original continuation, not just unique ones. A path has at most k pivots. Per layer, deduplicate by option set plus used-pivot set, rank by fewest literals without explicit binary conflict support, then shorter option set, higher support weight, shorter proof and a lexical tie break; retain at most B states. B defaults to 8, with valid range 1..32. Save a candidate when all options have explicit conflict support, no unused continuation exists, or the depth cap is reached. Deduplicate saved clauses by option set, retaining a shortest encountered proof. These are search heuristics, not assumptions about the semantics of an unsupported literal. A beam-pruned path may contain the only useful certificate.

For two certified same-polarity clauses S and T with S a strict subset of T, S implies T. Among saved candidates from the same start, remove supersets from the minimal portfolio using literal-set inclusion; the sort places strict subsets before supersets since unsupported-literal count cannot increase under taking a subset. Keep the entire saved candidate set for a separate wide portfolio. Dominance does not justify claiming that a smaller group always yields better global matching or clique extraction. Keeping both alternatives is an intentional heuristic safeguard, not completeness.

Try four group-selection policies: minimal candidates in source order, widest supported candidates in source order (including dominated candidates), minimal candidates in reverse source order, and minimal candidates with best-supported/shorter starts first. In each pass select the first disjoint candidate per start; skip if none exists. Run the D7F partition portfolio for the selected groups. Cache exploration by polarity across policies. If no Hall certificate results, run unchanged D7D cardinality, indexed resolution, and budgeted tree inference. If all return UNKNOWN, retain the identical residual and witness map. The unchanged Hall checker is independent of the beam, support rankings, dominance and group-selection algorithms.

## Polynomial resource bound

Let k be the explicit coordinate count, f the number of factors, and B the beam limit. At most 8f original forbidden-row clauses exist. For each of O(f) starts per polarity, at most k+1 layers of at most B states expand through at most O(f) continuations each. Thus O(B f^2 k) proposed transitions in total. Constructing a state and its canonical key costs O(k log(k+1)) abstract operations, with sorting of up to O(Bf) states per layer and comparisons of O(k) coordinate words. There are at most B(k+1) saved states per start; naive pairwise subset comparisons cost O(k^2) each. A conservative operation bound, including fixed selection passes and inherited D7F, is O(B f^2 k^2 log(B f k+2) + B^2 f k^4 + f k^2 log(k+1) + k^3), with polynomial key/word bit costs. The explicit cache uses O(B f k^2) coordinate/reference words, plus transient candidate states and the inherited graph. The default bounded-width beam and constant policy portfolio do not enumerate arbitrary disjunction derivations. These bounds cover host structural inference, not unrestricted D7D fallback, full SAT, or on-tape execution. Metrics count specified search events, not total runtime.

## Executed oracle, ambiguity and dominance evidence

1788 exhaustive small-instance oracle comparisons: 2812 satisfying models, 904 SAT, 884 UNSAT. On this identical corpus D7F yielded 224 Hall certificates and D7G yielded 762, 538 additional. Every positive Hall result independently checked; no false Hall refutation observed. All 276 local relation types and all 343 clean labeled three-group/three-hole graphs with nonempty neighborhoods were included. Ambiguity/noise corpus: 512 three-group/two-hole UNSAT cases (all 64 cross-resource edge patterns times all 8 subsets of groups with ambiguous auxiliary encoding), every one refuted; 16 additional two-group cases with possible SAT or UNSAT. Both polarities tested, 32 coordinate/factor/scope relabelings of the prior large obstruction verified, four damaged certificates rejected. The inherited D7F audit was re-executed and reproduced its previous output including its intentional D7F UNKNOWN barrier.

## Previous D7F obstruction eliminated

For six holes/seven pigeons, add not u or c at the first chain auxiliary u (index 42) and third occupancy variable c (index 2), creating the previous ambiguity. The original continuation not u or c or v and the new shorter continuation are both sound. The resulting shortened disjunction is a subset of the original final group. D7G derives both and selects the shorter valid group. On the actual predecessor residual (63 free coordinates, zero affine equations, 155 factors), D7F returns UNKNOWN; D7G returns a verified Hall contradiction with seven groups/six holes, 26 group axioms and 108 exclusions. Exploration: seven starts, 29 expanded states, one ambiguous expansion, 22 proposed transitions, eight saved clauses, one dominance comparison and one dominated clause; no beam drops. Neither resolution saturation nor tree inference is invoked.

| holes | modification | coordinates | factors | group policy | partition | core groups/holes | proof/exclusion axioms |
|---:|---|---:|---:|---|---|---|---|
|4|single|25|51|minimal|components|5/4|10/36|
|5|single|42|94|minimal|components|6/5|17/65|
|6|single|63|155|minimal|components|7/6|26/108|
|6|all first auxiliaries|63|161|minimal|components|4/3|8/18|
|6|all first auxiliaries + bridge|63|162|minimal|support-1|4/3|8/18|
|6|cross-group continuation|63|155|wide|components|7/6|28/126|
|8|all first auxiliaries|117|351|minimal|components|4/3|8/18|
|12|all first auxiliaries|273|1079|minimal|components|4/3|8/18|
|20|all first auxiliaries|777|4599|minimal|components|4/3|8/18|

All nine instances passed actual relational/affine predecessor checks with all coordinates free and no equations. D7F Hall UNKNOWN on every row; D7G Hall independently verified on every row, without enumeration. The 777-coordinate case adds 21 implications, yielding a four-group/three-hole core with only 26 source-axiom references; 399 expanded states, 378 transitions, 42 candidates, 21 dominance removals. These additions strengthen the original UNSAT formula, not necessarily logically redundant constraints for a satisfiable analog. The cross-group continuation row requires the wide policy; a separate run of that raw fixture with beam 1 drops one state and returns UNKNOWN from Hall. This demonstrates bounded-search incompleteness, not any intrinsic proof-system lower bound.

## Physical replay
|fixture|affine residual worker|D7G worker|
|---|---:|---:|
|small ambiguous UNSAT|2092|2092|
|small ambiguous SAT|794|794|
|63-coordinate prior barrier|not executed|2092|
|777-coordinate ambiguity|not executed|2092|

The small UNSAT case was already reduced by predecessor preprocessing and D7G fallback used resolution, not Hall. The SAT least expanded witness matched the exhaustive oracle. Four original/minimized replays, six exact clock comparisons and four one-short cutoffs passed. Two paired fixtures tie at 2886 aggregate transitions; no measured incremental transition savings this stage. The larger cases replay only the constant 10-symbol contradiction stream. Host inference and checking remain outside the physical accounting. Unchanged descriptor: 3683 minimized states, 180471 bits.

## New surviving policy obstruction — mixed literal polarity

Use the unmodified six-hole/seven-pigeon encoding (63 coordinates,154 factors), complement the first occupancy variable of every pigeon (indices 0,6,12,18,24,30,36), and transform every allowed factor tuple accordingly. This is a bijective coordinate-wise Boolean relabeling, so the original pigeonhole contradiction is preserved exactly. It is not the same transformation as a global complement. Same-polarity Hall extraction cannot reliably reconstruct the original signed option groups, because one option per group now has the opposite polarity. Actual integrated run: all 63 coordinates free, no affine equations, D7F Hall UNKNOWN, D7G Hall UNKNOWN after all four selection policies; exploration 126 starts, 294 expanded states, 168 transitions, 126 saved clauses, no beam drops. Inherited cardinality does not refute; indexed resolution exhausts 2,000,000 charged units (8392 generated records,21082 processed pairs); tree exhausts 2,000,000 units (17354 visited nodes,1017 conflicts,1027 splits,15309 unit steps). Exact residual retained. This is an executed limitation of the configured pipeline, not a lower bound on arbitrary SAT algorithms or a proof of width-four non-refutability.

## Next
Investigate coordinate-wise polarity normalization or general signed option-group certificates, independently checking exact relabeling and inverse witness reconstruction. Seek an invariant extractor for the demonstrated polarity-transformed family without assuming arbitrary signed-structure discovery is polynomial. Direct raw-selector physical normalization, on-tape inference and full resource accounting remain open. Main and PR #248 untouched. Dedicated D7G Proctor configured separately; remote success not claimed.
