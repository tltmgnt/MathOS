# F038-REX-024B — Exact physical width-three elimination planning

Parent 73121ab78cea0ab80a59c57a832b873ba08d0a46 (REX-024A). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

Previous exact-head [Proctor run 45900417782](https://github.com/tltmgnt/MathOS/actions/runs/45900417782) completed successfully, including both original and compressed native witness codec gates. The width-two witness program and its exact quotient are preserved. This cycle establishes the next bounded structural stage: exact width-at-most-three recognition and elimination-order construction for normalized nine-group selectors. It does NOT yet construct width-three bag relations or witnesses.

## Physical machine and checkpoint

A fixed ternary descriptor, derived from the 023B graph extractor, consumes the original raw selector, validates the same normalization, deposits 36 deduplicated graph flags and the pins, and executes a depth-first search on the graph. Every selected optional negative clause on distinct X groups contributes all pair edges of its scope; mandatory normalization clauses are excluded from the latent graph. No host graph, candidate order, branch oracle or runtime pointer is supplied. The compiler generates fixed transitions; the simulator executes unit physical transitions.

124438 nonhalting states, 373314 entries, 7964036 serialized bits. Planner entry 78720, push entry 83659, pop entry 85358 are observer metadata only.

On normalized halt, head is the original blank workspace separator. Left of it, the original selector, binary workspace, original graph blocks and pins remain intact. Right of it, a stack of blank-separated 60-bit frames is laid out in increasing depth:

* 36 graph bits in lexicographic pair order;
* 9 active flags;
* 9 tried-candidate flags;
* 4-bit chosen vertex, sentinel 9 before any choice;
* one root flag;
* one status bit (set only on successful root).

Each frame describes the residual graph BEFORE eliminating its chosen vertex. A complete accepted stack has ten frames (600 nonblank bits, plus separators): nine chosen vertices and a final empty graph frame. The nine chosen fields form the physical elimination plan. Later neighbors are available in each frame's graph, not separately emitted as bag records or parent indices. A rejected root retains only its original graph frame with status zero and the exhausted eligible-candidate bitmap. Malformed normalization still uses inherited single-zero cleanup. This structural program is not an original witness-interface program; the single-zero malformed halt can be interpreted as a candidate on n=1, so it must not be promoted to a witness generator.

## Exact physical search

At a frame, scan vertex IDs from 0 through 8. A candidate must be active, not already tried at this frame, and have at most three active neighbors (the invariant clears edges incident to inactive vertices). Degree is counted by finite control with an early exit on the fourth edge. For the first eligible candidate, set its tried bit and four-bit choice; push a new frame. Push initializes the child's 60 cells, physically copies the parent's first 45 cells using fixed-distance shuttles, then reads the parent choice and dispatches to the child fill routine. For every pair of vertices different from the chosen one, test their edges to the chosen vertex and set the pair edge if both are present. Clear the chosen active flag and its incident edges. Search again from vertex zero.

If all active candidates are exhausted, erase exactly the current child frame and return to its parent's separator. Parent graph and tried bits have not changed, so the next search attempts a different candidate. Exhaustion at root sets no success bit and halts there. An empty active set is success: retain all ancestor frames, move physically back to the root separator, set its status bit and halt. Maximum depth nine. All copying, degree tests, fill, erase and rewind actions are charged unit moves; blank frame delimiters are explicitly crossed by fixed-count walks. Observer counters count actual push/pop entry visits. An initial pop-return off-by-one defect was observed in the first K5 smoke test and corrected before the reported completed suites.

Correctness by induction on the remaining active vertex count: any complete order of width <=3 must begin with some vertex of degree <=3 in the current residual graph. Its suffix is a width <=3 order of the filled graph after that elimination. The search tries each such first choice once, recursively explores its suffix, and restores the exact parent state on failure. The empty set is the base case. Thus the physical procedure accepts iff such an order exists, and on acceptance returns the lexicographically first successful order. Standard elimination-order/tree-decomposition equivalence gives recognition of treewidth <=3 (not exact minimum treewidth). For each chosen vertex, its later-neighbor set forms a clique after fill, and its bag (owner plus later neighbors) has size <=4. Attach that bag to the earliest subsequent eliminated neighbor, or use a root for an empty separator. These derived host audit bags satisfy running intersection and cover every selected factor scope. No physical forest parent construction is claimed in 024B.

The separate oracle computes the torso after an eliminated set S directly from original paths with internal vertices in S, and uses memoized subset DP over at most 512 subsets. It does not reuse the physical stack search or physical fill operations. Every retained frame is compared to this independent oracle, including exact tried bitmap (all eligible vertices up through the winning choice, or all eligible on exhausted root), graph, active mask, choice, graph preservation and forest properties.

## Concrete counterexample to degree-three greedy selection

The following graph on IDs 0..8 has edges
```
01 02 06 13 18 25 27 36 37 38 46 58 67 78
```
The first-eligible greedy rule chooses 0,4,5 and gets stuck on six vertices 1,2,3,6,7,8, all with degree four in the filled graph. But there exists a width-three order:
```
1 2 4 5 6 0 3 7 8
```
The physical DFS tries the greedy branch, backtracks, and returns that exact order. It performs 14 pushes and five pops; its planner phase is exactly 212468 transitions at both m=2 and m=3. This is direct evidence why the proven degree-two greedy rule cannot simply be extended to arbitrary degree-three choices. No claim about every possible degree-based heuristic follows.

## Executed evidence

14 principal raw-selector executions across m=2,3,4, nine accepted plans and five structural refusals. Every case agrees with the subset-torso oracle. The complete graph refusal has an explicitly verified SAT assignment (all latent ranks one); the unary contradictory case is UNSAT by exhaustive domain-two latent enumeration despite an accepted empty-graph plan.

| Fixture | m | Transitions | Planner transitions | Pushes/pops | Outcome |
|---|---:|---:|---:|---:|---|
| empty |2|8145448|119962|9/0|plan|
| K4 |2|8153310|120768|9/0|plan|
| K3,6 |2|8196627|124677|9/0|plan|
| 3x3 grid |2|8185279|123009|9/0|plan|
| two triples |2|8300629|120349|9/0|plan|
| greedy trap |2|8277570|212468|14/5|plan|
| K5 |2|9107840|1067474|64/64|refusal|
| subdivided K5 |2|9122402|1080302|64/64|refusal|
| K4,5 |2|8069134|3088|0/0|refusal|
| complete graph |2|8123566|2704|0/0|refusal|
| unary UNSAT |2|8145448|119962|9/0|plan|
| greedy trap |3|34350431|212468|14/5|plan|
| nonconsecutive K5 |3|35189472|1088941|64/64|refusal|
| nonconsecutive K4 |4|100874759|120407|9/0|plan|

Totals 1169500 raw input bits, 262241915 principal transitions, 4516579 planner transitions, 283 pushes, 202 pops. Stack conservation pushes minus pops = 9 per accepted plan and zero per refusal. All four domain-two pin patterns, ternary clique insertion, backtracking and root exhaustion tested. Independent sparse Map interpreter parsed the original descriptor separately and replayed the full stack and preserved data for the greedy trap (8277570) and K5 (9107840), 17385410 further transitions. Combined completed total 279627325 transitions, excluding smoke tests, cutoff repeats and malformed tests. Six cutoff checks including planner entry and one step before halt, eight malformed controls. All current executed tests JS V8. Native structural codec gate is committed but not yet confirmed executed. Full domain-four planning completed, NOT domain-four width-two or width-three witness computation.

## Resource audit and next bounded task

Graph extraction inherits 023B's O(L^2) time and O(L) visited span: every optional selected scope has at most three charged edge-block queries; all 36 flags and m pins are deposited physically. The worst-case dense ternary scope causes Omega(L^2) repeated late-prefix shuttles. Search has at most sum_{d=0}^9 9!/(9-d)! nodes; each node scans at most nine candidates and uses constant-sized graph frames. The bound is constant in m only because nine groups and width bound are fixed; no polynomial claim for an unbounded number of groups follows. The physical search stack uses at most ten frames, with 600 nonblank bits plus separators. Thus normalized structural planner worst-case Theta(L^2) time, O(L) visited span, with O(log L) binary counter workspace plus fixed graph/search storage. This does not bound wider relation production or witness computation.

For width three, arity-four bags require at most O(m^4) tuples, with factors still only of arity <=3. A relation word could have N=O(m^4 log m). A direct generalization of C2's append-based serializer yields a conservative O(L*m^4+N^2) bound, subject to proving the rotation/carry invariant for four lanes. A naive extension of D1's explicit separator-key loop and per-digit full-word shuttles could cost O(m^3 N^2)=O(L^(11/3) log^2 L), which is NOT a subcubic upper bound. This estimate is not a lower bound or impossibility result. A different join/support representation or locality strategy is necessary before reusing the cubic admission argument.

Next REX-024C: physically construct width-three bag headers and factor ownership, including variable arity up to four and separator size up to three. Investigate an improved physical support-index/merge strategy and charge all movements before making any cubic-stage claim. Preserve the width-two machine and its verified native quotient. All four global routes and six overarching Omega obligations remain open.

Reproduce:
```sh
for suite in small larger controls; do
  node mathos/research/f038_rex_width_three_plan_audit.js "$suite"
done
node mathos/research/f038_rex_width_three_plan_replay.js
node mathos/research/f038_rex_width_three_plan.js --descriptor > /tmp/width3.desc
python -m mathos.research.f038_rex_width_three_plan_codec /tmp/width3.desc
```
