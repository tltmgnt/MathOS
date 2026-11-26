# F038-TGA-SEP-001 — Exact conditioned separator messages

System MRA-X-TGA-2.0. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent bd0bf134b271e9463184b5d091e0a7b9e4a69dab. Separate bounded hypothesis following CPR-001's binary-abstraction obstruction. The MRA-X/TGA roles are applied locally, not an invocation of a separately deployed engine or independent reviewer.

## 1. Research authorization and acceptance criteria

Hypothesis: exact component messages on small interfaces, with a bounded private cutset and a fully charged streamed elimination plan, recover globally feasible keys without querying global projections or making a parity abstraction. Unlike prior density-based recovery, successful structural eligibility gives a direct witness algorithm even on dense keys. Acceptance requires exact factorization, explicit resource bound including reconstruction, the prior conditioned K5 example, and a counterexample to a width-three message assumption. Stop if an interface exceeds the storage budget or the elimination plan exceeds the exponent budget. No extension of direct compression formats. This uses standard existential variable elimination and separator factorization; no claim of novelty for those general techniques or separation from all earlier MathOS separator workers.

## 2. Exact factorization theorem

Use the inherited normalized nine latent groups, real digits [0,m), n=19m-7 Boolean variables, raw input length L=Theta(m^3), selected negative original support bits of width at most three. The normalized pin, one-hot, OR and guard extension is inherited. Fix four key groups A, five other groups V. Build the private interaction graph: two distinct private groups are adjacent when they occur together in an original support. Let C_1,...,C_j be its connected components, including isolated vertices. For each C let B_C be the subset of A appearing in a support meeting C. All supports meeting C are contained in C union B_C by construction. Remaining supports are wholly within A. A conservative graph may retain redundant all-allowed predicates without affecting soundness, though it can lose eligibility.

Let F_C be the conjunction of original supports meeting C, and define the Boolean message on B_C:

    M_C(b) = exists c in {0,...,m-1}^C : F_C(b,c)

The exact feasible-key relation is

    W(z) = F_A(z) AND product_C M_C(z restricted to B_C).

Necessity is immediate. For sufficiency choose a satisfying extension independently for each message; the private components are disjoint, their only common coordinates are fixed key digits, and every original support is covered by exactly one component or the key-only part. Combining them yields an original model. Empty boundary gives a scalar Boolean message; an isolated unconstrained vertex gives true. A false scalar rejects the whole input. This factorization is exact, unlike the previous conditioned parity envelope. It does not itself give an algorithm until message evaluation is charged.

## 3. Computable structural admission criterion

Require |B_C|<=3 for every component. For each component choose a cutset S subset C of size s<=2, fix its digits, and eliminate every remaining private variable in a fixed order while retaining all boundary variables. Construct the induced scopes symbolically: at elimination of v collect all current factors containing v, take their union U including v, replace them with a factor on U minus {v}. Isolated v has empty remaining scope. Let w be the largest remaining-scope cardinality across the order (zero for empty order). Require

    w <= 3,
    s + max(3,w+1) <= 5.

Try all fixed-many cutsets and orders and choose minimal exponent, deterministic ties. Since nine groups are fixed, all these choices are constant in m; not advice. Enumerate all 126 four-key choices if desired and use any admitted plan; if none exists, this worker is ineligible (the complete portfolio must retain an original-correct fallback). No inference of UNSAT or hardness from ineligibility.

The s=2,w<=2 clause is redundant for asymptotic eligibility under |B_C|<=3: uncondition one cutset vertex, retain it through the old order, then eliminate it last. Each old remaining scope grows by at most one, and the final remaining scope is contained in B_C. Hence there is an s=1,w<=3 plan. We keep s<=2 in the explicit enumerator to express the charged tradeoff and allow exact comparison of plans. We do not assert that the audit selects a two-vertex cutset. The condition with max(3,w+1) explicitly charges the input scan per conditioned assignment; a naive s+w bound alone would undercharge small-width cases.

For each of m^s cutset assignments restrict all component predicates. Existential elimination replaces the conjunction of factors touching v by its OR over the real digit of v, leaving untouched factors unchanged. After all private noncutset variables are eliminated, surviving factors are on B_C. Enumerate boundary tuples and OR their conjunction into an accumulating message over the cutset assignments. Inductively this is exactly M_C. No oracle, randomized step or supplied decomposition. All intermediate output factors and final messages have at most m^3 entries; original predicates and constant factors included. An intermediate bag of size four may have m^4 candidate assignments but its output has width at most three and the candidates are streamed, never materialized globally.

## 4. Complexity audit: explicit sequential batches and physical bound

Use a fixed multitape bit routine with sequential merge sorting; each record has O(log(m+2)) bits including scope/digits. Store original input, constant-many factor tables and all intermediate outputs/history as needed, each of size O(m^3 polylog(m+2)). For one cutset assignment scan original component records, restrict fixed coordinates, materialize needed allowed factors by enumerating at most m^3 tuples and sorting/merging the original forbidden records. Handle true/false constants and unconstrained variables. Cost O(m^3 polylog m) sequential bit operations, even when the remaining elimination width is smaller.

For a bag of width w+1<=4, enumerate at most m^(w+1) candidate tuples in chunks of at most m^3. For each chunk sort by each incident factor's support, merge with that factor's table to mark allowed membership, repeat for constant-many factors, then sort back by candidate or outgoing tuple. A full scan of incident tables per chunk costs O(m^3 polylog m), so total for the bag O(max(m^3,m^(w+1)) polylog m), including joins. For width four, choose chunk order with outgoing tuple as lexicographic primary key and eliminated digit last (e.g. fix the leading outgoing digit for each chunk, leaving at most m^3 rows). Group OR by outgoing tuple, output at most one Boolean per outgoing tuple; if a group straddles chunks carry a single OR bit and its tuple key. All sorting, table copies, rewinds and merging are charged in sequential bit work. No indexed access or free dense m^4 table. At the end enumerate at most m^3 boundary tuples, merge all residual factors, OR into the stored accumulating message, also O(m^3 polylog m). Only fixed many eliminations. Thus per component

    bit time O(m^(s+max(3,w+1)) polylog(m+2)),
    bit span O(m^3 polylog(m+2)).

The admitted exponent is at most five. Inherited fixed-track one-tape sweep simulation encodes a fixed finite alphabet using constant-width blocks over 0,1,2; simulated head markers are maintained on tracks, a sweep locates them and implements each fixed multitape transition, at O(span) physical moves. Therefore, CONDITIONAL on the inherited normalized parser/output and simulation composition, aggregate physical message time O(m^8 polylog m), visited span O(m^3 polylog m). The initial raw layout conversion can be charged O(L^2 polylog L) under inherited preparation. No actual compiled machine or measured transition count for this worker. The ledger does not rely on the rate-free stationary positivity tree or sparse guard density.

After retaining all messages, enumerate four-key tuples in m chunks of m^3. Join with the constant-many messages and key-only factors by sequential sorting/merge; count exact globally feasible keys, and retain the first allowed key if one exists. O(m^4 polylog m) bit work, O(m^7 polylog m) physical, O(m^3 polylog m) space. This is an explicit computation of a global projection count and a FACTORED representation, not a free global-projection oracle and not the full m^4 tuple list. If zero, no witness exists. Otherwise reconstruct one original model, not all models.

For each component, with the selected key fixed, rerun its cutset loop and elimination until residual boundary factors accept that key. Retain the incident-factor tables immediately before each elimination (fixed number, total O(m^3 polylog m) span). Reverse the elimination order, choosing the first digit satisfying all its old incident factors at the already assigned remaining neighbors. Such a digit exists by the OR message at that stage. A conservative reconstruction charge for each chosen successful cutset is m candidate scans of O(m^3 polylog m) bits per variable, hence O(m^4 polylog m) bit work, O(m^7 polylog m) physical. Rerunning all cutset attempts is within the original O(m^8 polylog m) charge; no reverse reconstruction is done for unsuccessful cutsets. Combine private witnesses with the common key, check all original constraints, and reconstruct actual normalized one-hot/OR/pin/guard bits via inherited routine. Output cost inherited O(m^4 polylog m), halt at first contiguous output bit or blank on failure. No external certificate or assignment supplied.

Result on the admitted structural class:

    T(m)=O(m^8 polylog(m+2)), S(m)=O(m^3 polylog(m+2)).

There is no density hypothesis. With L=Theta(m^3), T=o(L^3). A fixed implemented program of description length ell, once eligible, gets >=L^3/2^ell steps at stage 3 ceil(log2 L); little-o suffices eventually. This is conditional on the same actual machine being implemented and the inherited assumptions audited. No universal-stage execution, description length, or finite cutoff proved. Outside the class no such time guarantee follows. These are bounded-dimensional CSP algorithms, not polynomial-time algorithms for general growing-variable SAT.

## 5. Positive control: CPR's conditioned K5

Four residue classes modulo 4, m divisible by four. Five private vertices: every pair except (4,8) requires unequal residue, and the ternary support {0,4,8} imposes unequal residue only for source a>=2. Boundary is {0}. For a<2, the private graph K5 minus an edge is four-colorable; for a>=2 K5 is not. Every proper private subset is feasible. The prior per-edge binary parity abstraction accepts all keys, even for arbitrary binary colors by the connectivity argument in CPR-001.

Here condition on private vertex 4. Its removal leaves four private vertices forming K4 and the only remaining key attachment is from 0 to 8. Eliminate the other private vertices before 8; remaining scopes have size at most three. Thus s=1,w=3 admitted. The exact message is M(a)=1 iff a<2, recovering 2m^3 feasible keys instead of m^4. No need to guess a four-color abstraction. The audit evaluates actual digit tables and reconstructs original witnesses for both good sources. This is a strict improvement over CPR's particular parity envelope, not a separation from all earlier separator solvers or graph-coloring methods. The instance is easy; no computational hardness claim.

## 6. TECT-X: boundary arity versus private tractability

For integer q>=2 let m=q^3. Use one private vertex h with m digits indexing all triples (r0,r1,r2) in Z/qZ. Four visible key digits have residues modulo q; each residue has q^2 actual digits. Four ORIGINAL BINARY supports {i,h}, i=0..3, require residue of key i to equal r_i for i<3 and -(r0+r1+r2) for i=3. The four other private vertices are isolated. All constraints are legitimate width<=3 normalized cross supports.

The exact projected key relation is

    W(z) = [sum_i (z_i mod q) = 0 mod q].

Its density is exactly 1/q ->0, but every proper coordinate projection, in particular every three-key projection, is full: choose the omitted residue to satisfy the sum and choose any actual digit of that residue. Therefore exact R_3(W)=the entire four-key domain and k*=4. More strongly no conjunction of arbitrary predicates each on at most three of those four actual key coordinates can represent W exactly, since any such predicate containing W must contain every tuple on its scope. This conclusion allows different ternary factors and any computation of them, but disallows new hidden coordinates, disjunctions, and alternative factorization languages. It is an arity obstruction, not a storage or runtime lower bound. The original private graph is trivial and original relation has arity two. The one component has boundary size four, outside the admission criterion, regardless of how cheaply its private witness can be evaluated. Retaining the original hidden vertex or algebraic sum predicate solves this easy example; the result does not imply that a general solver must materialize a four-coordinate table.

Separate admission negative control: a K5 private clique with a key adjacent to all five private vertices gives a six-clique on those six vertices. After fixing zero, one or two private vertices the first eliminated private vertex has respectively five, four or three remaining neighbors, violating w<=3 for s=0,1 or the time budget for s=2. The planner conservatively rejects this scope pattern. This is a failed certificate, not evidence that its instances are difficult.

## 7. MathOS executed evidence and limitations

The standalone JS audit uses actual allowed-factor sets and enumerated bag rows, not physical bit-sweep simulation. The revised regression also performs independent chunked sorted membership joins at every elimination, carrying an outgoing-tuple OR across chunk boundaries; its output is compared with direct bag enumeration and used in subsequent elimination and reconstruction. Ten fixtures m=2,3, five patterns each: eight eligible, two rejected scope patterns. Compare exact component messages against independent existential enumeration, all four-key projections against direct full nine-coordinate enumeration, reconstruct an original model for EVERY feasible key in each eligible fixture. Separate K5 controls m=4,8, actual digit tables; separate modular boundary q=2,3,4,5 controls using residue enumeration and exact multiplicities. Counts include forward elimination and witness reconstruction where applicable:

    2478 candidate elimination plans
    1280 elimination steps
    110505 bag rows
    29 forward cutset assignments
    135 exact message comparisons
    388 exact key comparisons
    80780 direct nine-coordinate tuples
    18809 original model occurrences
    249 reconstructed key witnesses
    379 component witness reconstructions (including K5 controls).
    10053 streamed batches
    321117 sorted-merge candidate membership comparisons
    6153 outgoing-tuple groups spanning a batch boundary
    25595 streamed outgoing allowed tuple occurrences.

K5 results [m,cutset,width,message cardinality,parity-key count,exact-key count]:
    [4,[4],3,2,256,128]
    [8,[4],3,2,4096,1024].

Boundary controls [q,m,allowed residue tuples,ternary closure residue tuples,lifted exact keys,lifted ternary closure keys]:
    [2,8,8,16,2048,4096]
    [3,27,27,81,177147,531441]
    [4,64,64,256,4194304,16777216]
    [5,125,125,625,48828125,244140625].

All assertions passed. The reference uses dense enumeration of individual small bags; the revised algorithm independently evaluates streamed chunks with capacity m^2-1 (deliberately smaller than the production m^3 cap to force split groups), exact sort/merge membership and cross-chunk OR. It verifies the semantics of that batched algorithm, not its sequential bit complexity, actual tape sorting/movement, all 126 key choices, raw normalized encoding/decoding, physical transitions, arbitrary m, or all input support patterns. Full nine-coordinate model counts refer only to eligible random fixtures, not the large clique or boundary examples. No independent mathematical review, Lean, integrated original-U solver or CI confirmation. Supplied prototype certification scores unchanged.

## 8. Research Energy Optimization and evidence gates

PRESERVE CPR hierarchy, multiplicity and obstruction. ADVANCE exact separator messages as a restricted deterministic constructive route, not a new universal claim. DECOMPOSE the remaining evidence into SEP-01 factorization and admission theorem, SEP-02 streamed bit implementation and cost, SEP-03 normalized physical integration, SEP-04 independent review, SEP-05 wider structural admission or alternative, SEP-06 same-machine exact-stage proof. RETIRE the claim that private tractability alone guarantees width-three exact messages; STOP automatic enlargement of message width (four-key boundary counterexample). A future hypothesis must explicitly handle representation cost or exploit a different invariant. Prior FAR/PCF/CPR/global gates unchanged. No automatic promotion; P vs NP OPEN. The bounded research decision is PRESERVE_EXACT_SEPARATOR_ROUTE_REVIEW_BEFORE_EXTENSION.
