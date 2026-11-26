# F038-REX-023B — Physical general width-two plan selection

Parent cad4c255f4675ed992dacd73b18d36753301e69a (REX-023A). Research branch only. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.

## Scope and inherited verification

The prior exact-head [REX-023A Proctor run](https://github.com/tltmgnt/MathOS/actions/runs/45894733832) is now confirmed successful, including its native Python original scheduler, compressed descriptor roundtrip, exact-clock witness and status gates. This closes the previously unconfirmed native large quotient replay, not any unrestricted proof route.

This cycle physically extracts the nine-vertex latent primal graph from the original normalized raw selector and selects a width-at-most-two elimination plan, with no fixed consecutive-path restriction. It is a new planner descriptor derived from B3; it is NOT a replacement for the complete B6 witness machine. Arbitrary-plan mask deposition, bag serialization, worker grammar adaptation and physical witness recovery remain open. The plan itself is not a Boolean witness.

The fixed ternary machine has 113660 nonhalting states, 340980 transition entries and 7274244 serialized bits. It starts at the original raw input, with no host-provided graph, domain, scopes, plan, or pointers. The host compiles constant finite control, decodes the table, simulates unit tape transitions, and inspects halted output. No host branching on input structure drives the machine.

## Physical graph invariant

Preserve the inherited full normalization validator and clause-address cursor. The original X groups are vertices 0..8. Each selected optional negative clause on distinct X groups contributes all unordered pairs of its support. Unary clauses contribute no edge. Each binary support adds one edge; each ternary support adds its three clique edges. All mandatory X/Y/pin/guard clauses are validated but excluded from the latent graph. Every zero selector bit and prohibited positive sign is still checked. No fixed-path scope rejection remains reachable.

To the left of the preserved selector prefix, maintain 37 blank-separated blocks read right-to-left. The first 36 blocks correspond to lexicographically ordered pairs (i,j), i<j. Each is empty if absent, or exactly one bit 1 if present. Block 36 stores the pin string in increasing original pin order. For a selected scope, finite control counts block separators and physically queries the first cell of each pair block; if already 1 it returns without writing, otherwise an inherited charged insertion shifts the farther-left block suffix and appends one. This deduplicates multiple selected rank tuples, including those across different scopes. Prefix, rank workspace and unread raw suffix are preserved.

At successful normalization, copy the 36 graph flags into a contiguous right-hand work region, then append nine active flags (all one). The original graph blocks and pins remain unchanged. All address walks in this work region have fixed finite-control distances, not runtime indices furnished by the simulator.

## Physical plan algorithm and correctness

While any vertex is active, scan vertices in increasing ID. Read the incident edges of each active vertex in increasing neighbor order. Retain up to two neighbor IDs in finite control; a third rejects that candidate. Choose the first vertex with degree <=2. Append the 12-bit record (v,a,b), each ID encoded in four bits; 9 is an absent-neighbor sentinel. If there are two neighbors, set their edge to one (fill); clear the chosen active flag and all its incident edges. Restart search at vertex zero. If no active vertex remains, append status bit 1 and halt at the blank workspace separator. If some remain but none has degree <=2, append 0 and halt there, retaining the partial plan and residual filled graph.

Invariant: eliminated vertices have no incident edges; the residual active graph equals the original graph after all recorded deletions and fill operations; each record lists exactly the chosen vertex's remaining neighbors. This follows directly by induction on the fixed write operations. The residual graph after eliminating set S can equivalently be computed by connecting two remaining vertices iff there is an original path between them whose internal vertices all belong to S. This is the independent audit oracle, which uses subset DP rather than the physical greedy algorithm.

For a graph of treewidth <=2, some vertex has degree <=2 (e.g. take a vertex unique to a leaf bag in a reduced width-two tree decomposition, or use a single bag). Deleting degree zero or one preserves the width bound. Eliminating degree two with fill is a minor operation: contracting the edge to one of its two neighbors gives exactly the graph with the vertex removed and its neighbors joined. Treewidth cannot increase under minors. Thus ANY greedy choice of degree <=2 preserves width <=2. Conversely, a complete elimination order with <=2 later neighbors gives a width-at-most-two decomposition: bag i is its eliminated vertex plus its later neighbors; if nonempty, attach its later-neighbor separator to the bag of the earliest-eliminated later neighbor. That bag contains the entire separator because fill made it a clique. The parent forest satisfies running intersection; component roots may be joined through empty separators. Every original clique of size <=3, including every original selected factor scope, is covered (use its earliest-eliminated vertex). Therefore complete plan iff latent primal graph has treewidth <=2. A stuck nonempty residual has minimum degree >=3 and certifies structural refusal under this argument. This does not compute exact minimum width: a tree may produce a width-two rather than width-one order.

Only the elimination records, original graph flags, residual graph and active flags are physically emitted. Parent indices, forest construction and checks are host audit computations, not yet physical worker grammar. The existing REX-020 worker expects full three-coordinate bags, overlap of exactly two retained parent labels, and one globally fresh child variable; arbitrary one/two-variable bags and smaller or empty separators must be handled explicitly before reuse. No assumed equivalence of these grammars.

## Physical checkpoint

At normalized halt, the head is at the original final workspace separator (blank). To its left: inherited rank workspace, preserved raw selector, original graph blocks and pins. To its right: 36 residual edge bits, 9 active flags, 0..9 elimination records (12 bits each), one status bit. A complete checkpoint has 154 bits; a refusal may have fewer. Malformed normalization instead uses inherited canonical single-zero cleanup. WIDTH_TWO_PLAN and OUTSIDE_WIDTH_TWO are observational labels for the status bit; neither is SAT or UNSAT. This is not an original witness-interface program (in particular the inherited single-zero malformed output is not a general n-bit refusal convention).

## Resource accounting

For accepted normalized dimensions L=Theta(m^3). The original validation/address traversal costs O(L log L); it moves O(log m) counters per input bit. Each selected optional clause causes at most three edge queries and at most three insertions, each costing O(L+log m+m) physical transitions. There are at most 36 first-time insertions and m pin insertions, but repeated edge queries still traverse the retained prefix; charge every query. Graph copy has 36 such traversals. After the summary, at most nine eliminations and a final search operate on a constant-sized 154-bit region, hence O(1) in m; the plan selection itself does not grow with domain size. Total O(L^2) time, O(L) visited span and O(log L) active binary counter bits. A dense chosen ternary scope contributes Theta(m^3) repeated queries after a prefix of length Omega(L), giving a matching worst-case Omega(L^2) for this implementation. All terms include physical input movement and edge deduplication; no free indexed runtime graph access. On malformed finite inputs each consumed bit induces at most a fixed number of shuttles and storage is linear, so O((L+1)^2) time and O(L+1) span. No bound for arbitrary-plan factor-table generation or a composed general width-two solver is claimed.

## Executed differential evidence

Sixteen completed principal physical runs against independently decoded scopes and subset-torso exact width-two DP; each record, residual neighborhood, lexicographic candidate choice, active flag, original graph, raw payload, pins and decomposition (where accepted) verified. All 36 edge positions covered by the complete graph. All four domain-two pin patterns, duplicate support across rank tuples, unary-only UNSAT, disconnected components, nonconsecutive pairs and triples, fill-producing cycle, high-degree star, K2,7, K4, K3,3 and subdivided K4 exercised.

| Fixture | m | Edges | Plan records | Physical transitions | Structural outcome |
|---|---:|---:|---:|---:|---|
| empty |2|0|9|8038256|accept |
| outside edge 0,8 |2|1|9|8039006|accept |
| outside triple 0,4,8 |2|3|9|8080323|accept |
| star |2|8|9|8043810|accept |
| cycle |2|9|9|8066605|accept |
| K2,7 |2|14|9|8070616|accept |
| two triangles |2|6|9|8197106|accept |
| K4 |2|6|5|8042470|refuse |
| K3,3 |2|9|3|8047021|refuse |
| subdivided K4 |2|11|5|8058850|refuse |
| complete |2|36|0|8122245|refuse |
| duplicate support |2|1|9|8040431|accept |
| unary UNSAT |2|0|9|8038256|accept |
| mixed scopes |3|9|9|35032318|accept |
| K4 |3|6|5|34090053|refuse |
| outside star |4|8|9|100724036|accept |

Total: 1245328 original input bits, 127 graph edge occurrences across fixtures, 117 physical plan records, 11 complete width-two plans, 5 structural refusals, 274731402 physical transitions. Zero disagreements. The outside edge/triple and K4/complete fixtures have explicitly verified original SAT witnesses; the unary UNSAT fixture has no model in exhaustive 2^9 enumeration despite a complete plan. This guards against conflating plan eligibility with satisfiability. The subdivided K4 eliminates five degree-two vertices, fills to K4, then refuses, rather than relying on original graph degree.

Separate sparse Map interpreter decoded the emitted table and independently replayed the outside-triple accepted checkpoint (8080323 transitions) and K4 refused checkpoint (8042470), comparing entire output and preserved blocks. Total 16122793 transitions. Combined principal and independent completions 290854195 physical transitions, excluding repeated tests, controls and smoke runs. Seven malformed controls and four budget cutoffs passed; exact outside-edge completion 8039006 transitions. All current executed tests in JS V8. Native original-codec regression and workflow are gates, not claimed executed in this cycle until confirmed.

## Governance and next task

ADVANCE physical general nine-group width-two recognition and elimination record generation. PRESERVE fixed-path B6 and its exact quotient. DECOMPOSE general factor-mask placement, physical parent/decomposition layout, handling variable bag/overlap sizes, and reconstruction to original n-bit witness. RETIRE fixed-path-only recognition as general width-two coverage, and structural rejection as UNSAT. STOP at this bounded planner stage. All four global and six overarching formal obligations remain open.

Next REX-023C: physically construct a general decomposition grammar from the elimination records; explicitly support smaller bags and separators (including disconnected components), then prove coverage and compare every emitted bag relation to independent tuple enumeration. Do not route arbitrary records into the unchanged REX-020 grammar.

Reproduce:
```sh
for suite in small larger controls; do
  node mathos/research/f038_rex_width_two_plan_audit.js "$suite"
done
node mathos/research/f038_rex_width_two_plan_replay.js
node mathos/research/f038_rex_width_two_plan.js --descriptor > /tmp/plan.desc
python -m mathos.research.f038_rex_width_two_plan_codec /tmp/plan.desc
```
