# F038-REX-009 — Exact bounded structural-width planning

MRA-X-TGA-2.0 + RE-X. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent bc31649c33dc2a140808f19a2b4e16e371e48511. Main unchanged. Bounded continuation of REX-008: reduce intermediate relation growth by selecting an exact admissible elimination order for a bounded number of variables and check its transfer to the previous prepared worker. No independent agent ensemble or formal certification is claimed.

## 1. Research hypothesis and acceptance criteria

The previous reference solver materialized the outgoing relation even when candidate scratch was capped. Hypothesis: scope structure and finite domain cardinalities suffice to compute exact per-stage candidate counts and safe outgoing bounds before evaluating predicates, and to optimize an admissible order for a fixed bounded variable set. Require independent exhaustive order oracle agreement, exact stage trace replay, a greedy failure control, an explicit structural rejection on a satisfiable input, and a prepared-worker chain that consumes preceding message outputs. Terminate after these finite checks; do not expand to unrestricted width or physical producer implementation.

## 2. Structural theorem and planner

Use the REX-008 normalized reference model, which always retains one explicit outgoing factor (even when empty, true, or nullary) after each stage. The primal graph has vertices active variables and clique edges for every factor scope. For eliminated set S, two remaining vertices are adjacent iff the original graph contains a path between them with all internal vertices in S. Initially this is ordinary adjacency. Eliminating v makes its surviving neighbors a clique, removes v, and leaves other edges. A path using v internally decomposes into paths to v and from v with interiors in S; the converse follows by concatenation (a walk can be shortened to a path). Thus by induction the filled graph is independent of the order within S. This structural result uses the unsimplified scope policy; semantic simplification could change scopes and is not included.

The current candidate bag for v is {v} union its current neighbors, and outgoing scope is those neighbors. Even a variable with no bucket has its domain enumerated. For domain cardinalities d_i define C(S,v)=product over bag d_i, U(S,v)=product over neighbors d_i, and J(S,v)=ceil(C/cap). The empty product is one; an empty domain makes C zero. C is exact for the reference candidate enumeration; U bounds explicit outgoing row count, not necessarily the actual count (and may be conservative when the eliminated domain is empty). The cap bounds candidate scratch, not message cardinality. Admission can constrain bag cardinality (one more than conventional induced width), U and C. Retained coordinates never enter S, allowing partial elimination. Original factor scopes and rows are validated before planning.

For target set E, with admissible transitions only, compute
 P(E)=0; P(S)=min_v max(C(S,v),P(S+v)).
 Missing suffixes are infeasible, not numeric infinity used as a SAT result. If P(empty) exists, let p*=P(empty). A second DP restricts every transition to C<=p* and minimizes
 A(E)=0; A(S)=min_v (C(S,v)+A(S+v)).
 Tie break by the original coordinate-index sequence. The two passes are important: a lexicographic single-best partial solution can discard a larger intermediate peak with lower total, even when that peak will be dominated by another stage. Min-max recurrence and fixed-threshold additive recurrence follow directly by splitting off the first elimination. Therefore the returned plan globally minimizes (peak candidate count,total candidate count,index sequence) among all admissible orders, not actual hardware time or a general width objective. Certificates include every bag, outgoing scope, C,U,J and aggregate maxima/sums; replay rechecks the certificate and compares each step to actual reference stage trace. Greedy comparator chooses (C,U,bag size,index) locally; it is not complete.

For t eliminable variables and n active variables, at most 2^t subsets, O(t 2^t) transitions. Graph snapshots, products and stored order tuples introduce factors polynomial in n and cardinality bit lengths; e.g. O(2^t poly(n,log max(2,d_i))) host work/space after input validation, ignoring predicate row work. The default exact search refuses t>12; nine-variable F038 planning is a fixed-size search, not a polynomial-time planner for unrestricted n. Greedy is available separately. No input/output relation enumeration is required to select the plan after validation. The planner does not claim to find semantic compressions, optimal slicing, cutsets or optimal total physical runtime.

## 3. Executed validation

The local Python solver and validation suite from REX-008 match remote blobs f0d633552d67fef7b3e29a6fc48a3f49c7c27091 and 982a68ab6ccf16d7e571231cd7941e6da11a576f; freshly rerun eight suites and six prior bridge comparisons passed. The new planner and audit files match remote blobs ee34d552d1cb444d3c7f5814ef8249b0c56d093c and 9cf0809d86c26939b31b3fa88e9f9f3064eff5e9. Local actual Python execution passed.

584 planning configurations: all 64 undirected graphs on four vertices across three cardinality vectors (including zero), each with full and constrained partial elimination, plus 100 seeded random five-variable relational instances with two configurations each. Independent explicit hyperedge replacement enumerates 23,064 orders, not using graph fill or subset DP. 538 admitted, 46 structurally rejected; exact objective and every stage certificate matched exhaustive optimum. Execute all admitted cases in the reference model, verifying 2,035 stages, 7,723 candidate rows, and final projection against direct predicate evaluation. Greedy returned a strictly worse peak/total objective in 68 cases and failed to find a plan in one admitted case. Tampered certificate and excessive exact-search limit rejected. Additional all-retained, nine-variable and star controls excluded from these counts.

Greedy dead-end example: sizes a=1,b=2,c=3,d=4; scopes ab,ac,bd,cd; retain d; limits bag width<=3, outgoing bound<=8, candidate count<=16. Greedy eliminates a first (C=6), fills b-c, then both remaining possible bags bcd have C=24. Exact order b,c,a has C values 8,12,4 (peak 12,total 24) and outgoing bounds 4,4,4. The finite audit found this structural counterexample. For a separate K5 among nine variables with only (0,0) in each binary factor, all-zero assignment satisfies the original factors, but no order satisfies bag width<=4: the first eliminated clique vertex has bag width 5. Executed this rejection at m=2,3,8,32. No SAT verdict follows from rejection. The primary audit uses empty-row factors as separate scope-only controls; path is admitted and K5 rejected at the same sizes. In the path, peak=m^2, 9 chunks at cap=m^3.

## 4. Recovery of the star obstruction

For r Boolean leaves b_i, center a, allowed binary rows (0,0),(0,1),(1,0), the REX-008 center-first stage has candidate count 2^(r+1) and outgoing count 2^r. Every leaf-first step has a two-variable bag, C=4 and U=2; final center step has C=2 and U=1. Thus leaf-first total C=4r+2, and peak C=4. Any full order must process a non-isolated edge endpoint at some stage, so peak>=4. The explicit relation blow-up is eliminated for this graph by order selection, not by compression or a general polynomial SAT algorithm. Executed leaf-first plans and satisfiable result at r=2,4,8,12; exact DP also checked r<=8 (r=12 means 13 variables, above default exact limit; used greedy). Center-first figures are structural certificates, not fresh enumeration in this cycle.
 [r,center peak C,center peak U,leaf peak C,leaf peak U,leaf total C]:
 [2,8,4,4,2,10], [4,32,16,4,2,18], [8,512,256,4,2,34], [12,8192,4096,4,2,50].

## 5. Prepared-worker lifecycle experiment

Python exact plan for signed noncontiguous domains a=(-3,7), b=(2,9), c=(-5,4), factors ab={(-3,9)}, bc={(9,4)}, cap=2, bag width limit 2: a,b,c; candidate counts 4,4,2; total 10; 5 chunks. The new JS bridge consumes the plan and actual factor rows, verifies candidate scopes/counts/chunk counts, maps values to domain ranks, invokes REX-007 adapter, and inserts each actual returned message as the next factor. Recovered local minimum-witness maps are stored for reverse backtracking, not taken from arbitrary outgoing OR representatives.

Stage a: two actual physical batch calls, 25,794,081 physical and 1,945,173 logical transitions, outgoing b={9}. Stage b: two logical-only batch calls, 15,610,112 logical transitions, outgoing c={4}. Stage c: one actual physical batch call, 5,527,647 physical and 412,925 logical transitions, true nullary outgoing {()}. Combined physical total 31,321,728 transitions; 2,358,098 logical steps within those runs. Complete host backtrack produces c=4,b=9,a=-3 and original relation check passes. Python locally compared the executed JSON to its independently computed plan and all three outgoing relations; passed. Evidence JSON matches blob 23cf9a963c999cf63c23fda431d887a7fa49a262. The physical steps are simulated original three-symbol transitions, not hardware timing. The middle stage is logical only, with host generation, rank encoding, transfers, merge, and witness backtracking between invocations. No single physical tape lifecycle, universal physical equivalence or original normalized raw solver is established.

## 6. Conditional resource admission for F038

For nine fixed variables, common domain m, constant-many original factors of arity<=3, impose bag cardinality<=4, U<=m^3, C<=m^4, cap=m^3. Every admitted unsliced full order then has at most 9m chunks; the same holds for a partial order (but its final retained-key join needs separate cost accounting). Each prepared chunk has O(m^3 log(m+2)) bits under the REX-007 encoding, including complete factor rows and constant-many requests per candidate. REX-006 costs Theta(kN^2) with k=O(log(m+2)), hence O(m^6 polylog m) per chunk and O(m^7 polylog m) aggregate prepared-worker contribution for these unsliced plans. This is not a total original machine runtime: fixed physical generation/merge/relocation/history and raw parse, final witness output remain to be charged. Earlier sliced/cutset O(m^8 polylog m) ledger remains conditional and is not replaced. For normalized L=Theta(m^3), m^7 polylog m=o(L^3) only for the accounted contribution; no exact same-program stage guarantee. The planner's limits do not themselves enforce original factor arity or count; those are explicit hypotheses. No unrestricted completeness or polynomial-time SAT inference.

## 7. Status and governance

REX-009 refines evidence notes without changing claim states. Local inherited modeled completion packages: physical interface 3, integrated machine 5, restricted stage 6, restricted evidence 7, uniform evidence 8; all blocked. Global mathematical alternatives direct SAT 1, selector 3, certificate architecture 7, universal lower bound 1: 0/4 closed. Counts are authored work packages not distance or difficulty. Python status execution and exact-head CI unconfirmed; no Lean or independent review.

ADVANCE bounded exact structural planner, stage certificate checking and host-transferred prepared-worker lifecycle. PRESERVE finite relational semantics and earlier physical primitives. DECOMPOSE fixed physical producer and persistent message/history lifecycle for admitted plans; later separately authorize conditioned/sliced plan integration if useful. RETIRE greedy admission completeness and ineligibility implies UNSAT. STOP automatic expansion after the bounded task. Decision PRESERVE_WIDTH_PLANNER_PHYSICAL_LIFECYCLE_OPEN.

Reproduce:
 python -m mathos.research.validate_finite_relational_elimination
 python -m mathos.research.validate_f038_rex_width_planner | sed -n 's/^REX_WIDTH_PLANNER_OK //p' > /tmp/width.json
 node mathos/research/f038_rex_width_bridge.js /tmp/width.json > /tmp/width-bridge.json
 python -m mathos.research.validate_f038_rex_width_planner /tmp/width-bridge.json
 python -m mathos.research.tga_f038_rex_009

PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
