# F038-REX-024D7H — Certified coordinate-wise polarity normalization

Parent D7G: 54d37c207088566927e18cbf6a903988c8887b31. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Exact Boolean involution and witness preservation

For an explicit binary factor instance d and a vector sigma in {0,1}^k, set y_i=x_i XOR sigma_i. Each scope is unchanged; its allowed tuple set is mapped by the corresponding restricted XOR vector. For every complete assignment, every original factor accepts x iff the normalized factor accepts y. The transform is its own inverse; this gives a bijection of complete model sets, not merely equisatisfiability. The independent map checker enumerates at most eight possible tuples per factor and checks membership equality after inverse transformation. The normalization producer snapshots the vector. The independent proof checker validates the vector and reconstructs normalized tables from original allowed-row membership; signed proof axioms additionally check the raw forbidden row directly.

Complementation is not order-preserving for lexicographic witnesses. D7H uses normalized representations only to seek contradictions. If inference fails, the original uncomplemented residual and identity witness map pass to D7D fallback. The existing least-witness physical convention is therefore preserved. No claim of lexicographic equivalence under arbitrary XOR is made.

## Deterministic polarity discovery

Every exact binary forbidden-row clause contributes votes for the opposites of its literals, treating those opposites as candidate capacity options. Select a complement for each coordinate so that the more frequently voted option becomes positive; unvoted variables remain unchanged. For nonzero tied votes try a second vector reversing all tied decisions. There are at most two proposals, not a search through 2^k orientations. The choice is a heuristic; correctness of a contradiction never depends on vote accuracy.

First run inherited D7G. If UNKNOWN, for each orientation normalize and try D7G. If still UNKNOWN, use mixed-intermediate resolution chains. Positive supported options are those appearing negated in an exact binary clause. Start at an axiom with at least one supported option and no unsupported opposite of a supported option. Resolve an unsupported auxiliary coordinate with each source axiom containing its opposite. Keep at most B=8 states per layer (configurable 1..32), deduplicate by canonical clause and used pivot coordinates, reject tautologies, reject wrong-polarity supported options, and never reuse a pivot coordinate along a path. Save only nonempty all-supported positive disjunctions. A path has at most k pivots. Select disjoint groups using short, wide and reverse source-order policies, and reuse D7F's validated partition and matching algorithm.

The new signed Hall checker independently validates the source axiom of every resolution step, the explicit complementary pivot, the exact non-tautological result, the final group, disjointness, hole coverage, and every original cross-group binary exclusion. The checker does not trust the orientation votes, search beam, group selection or graph construction. A Hall deficiency alone triggers the contradiction adapter. Inherited and normalized same-polarity proofs use the unchanged D7E checker with the verified transformation. Failed search has no SAT implication.

## Conditional family-wide invariance theorem

For the clean D7D ternary encoding of n+1 pigeons into n holes (n>=3), take ANY independent coordinate-complement vector, including auxiliaries. In the clean encoding each occupancy variable occurs in exactly n binary mutual-exclusion axioms with a consistent sign, and auxiliary variables occur only in ternary chain clauses. Therefore majority votes exactly restore the original occupancy orientation and leave auxiliary signs arbitrary. For n=3 all positive pigeon clauses are already restored. For n>=4 each original chain clause contains one or two supported positive options; its auxiliary literals are the boundary of a contiguous segment of the original chain. Every auxiliary pivot has exactly one complementary source clause, the neighboring chain clause. Resolving it expands the segment without introducing a tautology or repeating a pivot. Each start yields the full original pigeon disjunction in n-3 steps. There is no competing continuation and hence no beam pruning. Every group is recovered by disjoint selection (duplicate starts within a group are skipped). The conflict graph is exactly the n resource cliques; the Hall checker proves n+1>n. Earlier successful structural stages may return sooner. This establishes polarity invariance for this exact clean family as input, not arbitrary formulas, arbitrary additional exclusions, or every possible predecessor transformation.

## Resource accounting and sparse cardinality screen

Factor complementation and binary votes require O(k+f) abstract operations for bounded arity f factors. There are O(f) source starts per orientation, at most k+1 layers with B states and at most O(f) continuations per state, so O(B f^2 k) proposed transitions. Constructing canonical keys, copying proof paths, deduplicating and sorting yields a conservative O(B f^2 k^2 log(B f k+2)) operation bound for the additional signed exploration, plus polynomial storage O(B f k^2) coordinate/reference words for saved candidate paths and temporary states. The fixed selection and partition passes add O(B f k^2+k^3); the at-most-two normalized D7G calls retain the D7G polynomial host bound. The independent checker is polynomial in explicit input and proof size. All bounds are abstract, with polynomial bit overhead; no general polynomial SAT or end-to-end physical result follows.

During integration the 189-coordinate residual exposed expensive inherited NAE quintuple enumeration. The new adapter first counts distinct eligible triple scopes (both homogeneous tuples forbidden); a five-coordinate NAE core necessarily needs ten different scopes. If fewer than ten exist, return UNKNOWN without quintuple enumeration. Otherwise invoke the original cardinality rule. This exact necessary-condition screen changes no contradiction decision and leaves predecessor code untouched. Dense NAE5 still yields a checked cardinality certificate; a clean PHP6 fixture has zero eligible triples and zero quintuple trials. Worst-case inherited cardinality still costs O(k^5). The original combined tool execution timed out; the audit was split into five sections and the sparse guard added before rerunning the affected sections.

## Executed evidence

- 2671 complete model-set bijection/involution checks, 8937 model occurrences preserved, including all 276 local Boolean relation types under every local complement mask.
- 551 small formula oracle comparisons, 609 satisfying models, 288 SAT, 263 UNSAT; D7G 117 Hall proofs, D7H 231 independently verified Hall proofs (114 additional); zero false refutations observed.
- All 4096 polarity masks of the 12-coordinate clean PHP(4,3) formula independently refuted: two inherited Hall, 4094 normalized Hall. These are certificate checks, not exhaustive assignment enumeration per mask.
- 32 deterministic mixed-polarity coordinate permutations with reversed factor and scope order on PHP(5,4), all checked.
- Five corrupted certificates/maps rejected. The dense/sparse cardinality screen tests passed.

All seven larger rows below executed actual relational and affine preprocessing, independent affine checking, and certified contradiction discovery. Every residual retains all coordinates and zero affine equations.

| holes | complement pattern | coordinates | factors | certificate | groups/holes | derivation/exclusion references |
|---:|---|---:|---:|---|---|---|
|3|occupancy|12|22|normalized|4/3|4/18|
|6|first occupancy per pigeon|63|154|normalized|7/6|28/126|
|6|mixed occupancy and auxiliary|63|154|signed|7/6|28/126|
|6|auxiliary only|63|154|signed|7/6|28/126|
|8|mixed|117|342|signed|9/8|54/288|
|12|mixed|273|1066|signed|13/12|130/936|
|20|mixed|777|4578|signed|21/20|378/4200|

The second row is the previous D7G policy obstruction, now refuted before indexed resolution or tree inference. On the 777-coordinate case signed search expanded 6804 states, proposed 6426 transitions, saved 378 candidates, and dropped zero beam states. Its 4578 axiom references are the full clean encoding. No assignment enumeration for these seven structural decisions.

## Physical replay

| fixture | affine residual worker | D7H worker |
|---|---:|---:|
|mixed small UNSAT|943295|2092|
|mixed SAT|14801|14801|
|63-coordinate previous obstruction|not executed|2092|
|777-coordinate mixed signs|not executed|2092|

Two paired fixtures: 958096 -> 16893 transitions, 941203 eliminated. Four original/minimized new-stream agreements, six exact clock checks and four one-short cutoffs passed. Mixed SAT least expanded witness matched exhaustive oracle. Larger cases replay only the ten-symbol certified contradiction stream. No incremental D7G physical savings or full unreduced large physical timings asserted. Host costs excluded; descriptor unchanged (3683 minimized states,180471 bits).

## New surviving policy obstruction — implied rather than explicit conflicts

Replace each binary exclusion (not x or not y) in the clean seven-pigeon/six-hole encoding with two binary clauses (not x or u) and (not u or not y), using a fresh auxiliary per exclusion. Existentially eliminating u recovers exactly the original exclusion, so the modified formula is UNSAT. There are 63+126=189 coordinates and 28 ternary+252 binary=280 factors. No direct original occupancy-to-occupancy exclusion remains. The auxiliary variables receive tied polarity votes, and the current extractor does not certify transitive exclusions. Actual integrated run retains 189 free coordinates and zero affine equations; both orientation proposals fail (168 anchored variables, 126 ties), D7H Hall UNKNOWN; sparse NAE screen excludes a five-coordinate core; indexed resolution exhausts 2000000 units (9956 generated records,16485 processed pairs); tree exhausts 2000000 units (12554 visited nodes,360 conflicts,377 splits,11816 unit nodes). The exact residual is retained. This is a limitation of the configured policy, not a proof of width-four non-refutability or a lower bound against arbitrary SAT algorithms.

## Next

Investigate certified implication-graph reachability and implied binary mutual exclusions, using explicit source paths and independent resolution verification. Seek structural conflict recovery for the 189-coordinate encoding, with careful bounds and new obstructions. Direct raw-selector physical normalization and end-to-end physical accounting remain open. Main and PR #248 untouched; dedicated Proctor configured separately, remote completion not claimed.
