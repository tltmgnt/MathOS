# F038-TGA-SEP-002 — Boundary-sliced exact separator recovery and status routes

System MRA-X-TGA-2.0. PNP_RESOLUTION_STATUS = OPEN. PROMOTION = NONE.
Parent 6740c15fd01f3e7aa62fd8ab493bb40ade1c2580. Separately scoped bounded hypothesis after SEP-001's four-key arity obstruction. Apply the requested MRA-X/TGA roles locally; no separately deployed engine or independent reviewer. Main and existing global P vs NP graph unchanged.

## 1. Research authorization

Hypothesis: an exact high-arity boundary message can be consumed one boundary slice at a time, preserving original feasibility and witness recovery while avoiding full four-coordinate message storage. This is a different evaluation schedule, not a new lossless representation or a promise of short algebraic formulae. Acceptance: exactness, charged preparation and reconstruction, strict structural separation from SEP-001 even when it tries ALL four-key partitions, a counterexample to general admission, finite regression and explicit local/global status routes. Stop if the full slice loop consumes exponent nine or no scope plan qualifies. Standard conditioning and variable elimination are established methods; no claim of mathematical priority for them, or of separation from all MathOS or external algorithms.

## 2. Exact sliced factorization

Use the inherited nine-group normalized selector family, n=19m-7 Boolean variables, real digits 0..m-1, L=Theta(m^3), original selected negative cross supports of arity <=3, inherited pin/one-hot/OR/guard extension. Fix four key groups A and five private groups V. Use the SEP-001 private graph components C and boundary B_C subset A; all original supports either lie entirely in A or meet exactly one private component. Let M_C be its exact existential message, F_A the conjunction of key-only predicates.

Retain every component that already passes the SEP-001 planner as a STATIC component. Construct and keep its exact message of width <=3, using its own admitted cutset/elimination plan and charging its computation once. This is valid even if its boundary includes a key coordinate later sliced: the cache is evaluated at the actual full key, never existentially dropped. The other components are DYNAMIC.

Choose a common key slice Q subset A with q=|Q|<=2. If q=0 require all components static. For each real assignment u of Q, restrict every dynamic component's original predicates on Q to u and compute its exact message M_C^u on B_C minus Q. It equals M_C at the actual specified Q values on that boundary, even if some Q coordinates are absent. Private components are kept unchanged (they may split after restriction, but this is not needed). For that same slice, evaluate for all residual key tuples z on A minus Q:

    W_u(z) = F_A(u,z)
             AND all static M_C((u,z)|B_C)
             AND all dynamic M_C^u(z| (B_C minus Q)).

This is exact original-key feasibility: every accepted conjunction supplies a private extension independently in each disjoint component; their union with the fixed full key satisfies all original supports. Conversely every original model is represented in its unique slice. Sum counts over slices (disjoint full keys), remember one successful full key, discard dynamic messages after each slice. Exact count may be zero; that implies UNSAT only for an admitted, executed complete route. Do not store the full key set. At a successful key regenerate the dynamic messages of its slice and reconstruct one actual private extension per component by SEP-001 reverse existential elimination. Static messages can be retained, and the successful static private extensions regenerated independently. All original constraints checked and actual normalized witness reconstructed; no witness supplied externally.

## 3. Structural admission and planner reduction

A static component uses original SEP-001 conditions |B_C|<=3, cutset size s<=2, outgoing width w<=3, s+max(3,w+1)<=5. A dynamic component after removing Q from scopes must have |B_C minus Q|<=3 and admit a private cutset of size s<=2 and an elimination order with outgoing width w<=3 satisfying

    q+s+max(3,w+1)<=5.

Both criteria are computable symbolically from scopes; try all four-key choices, Q and local cutsets/orders (fixed finite number independent of m). Ineligible is a structural rejection, not UNSAT. The overall algorithm needs an original-correct fallback on ineligible inputs, for which this cost theorem gives no guarantee.

There is a useful simplification. Every eligible plan with any dynamic components can be replaced by a SINGLE common sliced key a in A and zero private cutset for every dynamic component, with outgoing width <=3. Proof:
- If q=1,s=0 this is already true.
- If q=1,s=1 the cost condition forces w<=2. Uncondition the one private cutset vertex, retain it throughout the old order and eliminate it last. Every old outgoing scope grows by at most one; its final scope is contained in B_C minus Q, of width <=3. The new w<=3.
- If q=2 the condition forces s=0,w<=2. Unfix either of the two common sliced key coordinates, retain it throughout each old order. Every outgoing scope grows by at most one; each new boundary has size <=3. The same retained single slice coordinate works simultaneously across all dynamic components.
- No q>=1,s>=2 case satisfies the condition. Static components remain exactly as before.

The scope growth argument follows by induction over the original elimination order: restored factors differ only by including the single restored variable, and each union-and-eliminate operation preserves this containment. The remaining constraints at the end of the order have scopes contained in the boundary plus the restored private vertex if applicable. No dependence on actual digit values. Conversely the simplified single-key dynamic plan with s=0,w<=3 meets the cost condition. Therefore the enlarged eligibility search has exactly the same admitted class as the old static-only case OR one sliced key with no dynamic private cutset. Static cutsets may still be nonempty. This is a planner equivalence, not a pointwise runtime dominance or a claim that two-coordinate slicing could never help under another cost model.

## 4. Fully charged conditional ledger

The SEP-001 fixed multitape bit routine scans, conditions and sort-merges original factors in O(m^3 polylog(m+2)) sequential bit operations and space. For each private elimination bag of width <=4, enumerate candidate assignments in chunks <=m^3, sort and merge against incident factor tables, existential OR by outgoing tuple across chunk boundaries; never globally store the bag. Each bag costs O(max(m^3,m^(w+1)) polylog m) sequential bit operations, with at most m^3 outgoing entries. Constant-many bags and factors, fixed record bit lengths O(log m). For static components pay at most O(m^5 polylog m) sequential across their cutsets ONCE. For dynamic components scan and restrict original predicates per slice, then per private cutset, paying O(m^3 polylog m) even if a slice leaves smaller scopes. Over all m^q slices the exact charged cost is

    O(m^(q+s+max(3,w+1)) polylog m) <= O(m^5 polylog m).

Static caches, active dynamic messages, original records, a constant number of factor histories and one batch all fit O(m^3 polylog m) total space; clear dynamic data between slices. No m^4 expanded boundary table, even across different components. Query static messages using actual full keys, with the slice coordinates attached as fixed fields. Enumerate the residual keys in chunks <=m^3; across all slices at most m^4 candidate keys. Restrict key-only factors or scan them as ordinary join tables. At most max(1,m^(4-q)/m^3) chunks per slice, each with full O(m^3 polylog m) scans of fixed-many tables and sorting/merging, for total O((m^4+m^(q+3)) polylog m) <= O(m^5 polylog m). For reduced single-key plans or the static q=0 case this is O(m^4 polylog m); the general q=2 ledger must charge m^5 rather than just m^4. Count exact keys and retain one actual full key; the production algorithm does not store the set. If count nonzero, regenerate only the successful slice, rerun the needed component cutset/old factor histories, reverse eliminate choosing a valid real digit by scans. Reruns within original total bounds; reverse reconstruction O(m^4 polylog m) sequential for fixed-many private vertices, as in SEP-001. No expansion of all witnesses.

Using the inherited fixed-track one-tape full-span sweep simulation of this fixed multitape bit algorithm, charging O(m^3 polylog m) physical moves per simulated bit transition, raw layout conversion O(L^2 polylog L) and inherited actual output O(m^4 polylog m), gives on the admitted class

    T_phys=O(m^8 polylog(m+2)),
    visited span=O(m^3 polylog(m+2)).

This is a conditional analytical resource theorem, not an executed normalized three-symbol machine. The earlier prepared mask/equality machines are limited primitives, not this solver. No density hypothesis. No logarithm-rate issue because exponent 8<9. With L=Theta(m^3), T=o(L^3); if the SAME fixed implementation with description length ell is realized, stage 3 ceil(log2 L) allocates >=L^3/2^ell transitions once eligible, and little-o eventually fits. No actual description length, integration, threshold or universal-stage execution supplied. All results confined to nine-group normalized class, not general variable-count SAT. The user-supplied MRA-X pilot metrics are not certified or updated here.

## 5. Strict positive structural separation: K4,5

Use a private graph pattern with all twenty original binary supports between two groups of vertices of sizes 4 and 5 (the full primal graph K4,5). Any additional constraints on the natural four key vertices may be present, without changing the argument. Use arbitrary selected binary forbidden relations on the twenty edges, all nonempty if comparing actual support graphs, and arbitrary width<=3 key-only constraints. No assumption of sparsity or nontrivial feasibility.

No choice of four keys can satisfy SEP-001's boundary criterion. Indeed K4,5 is 4-vertex-connected: deleting fewer than four vertices leaves at least one vertex in each part and a connected complete bipartite graph. If any nonempty private component after removal of four key vertices had boundary size <=3, deleting just that boundary would disconnect it from a key vertex outside its boundary, contradiction. Hence every private component has boundary exactly four, for every four-key partition, so every old plan fails prior to elimination.

With the natural part of size four as A, the five private components are singleton vertices. Slice any one key. Each dynamic singleton is eliminated in a bag of width four (three remaining boundary variables plus private digit), yielding a three-coordinate message. q=1,s=0,w=3 meets the exponent budget. Join all five messages and key-only constraints in each slice. This admits the entire arbitrary binary-constraint K4,5 family just described, including SAT and UNSAT, rather than merely an easy example with a supplied witness. It is a strict enlargement of the previous admission certificate even when all 126 old partitions are tried. No claim about performance of other previous workers or general CSP solvers.

Also recovers SEP-001's hidden modular-sum example: m=q0^3 (q0 a residue size, not slice count), one hidden vertex indexes three residues and four binary constraints force four visible residues to sum to zero. The full four-key projected relation has k*=4, exact triple closure full, but a single key slice leaves a width-three exact message. The solver does not need a modular formula. Its exact count m^4/q0 and feasible witness are obtained with width<=3 stored tables. This resolves that designated representation-arity obstacle by evaluation scheduling, not by contradicting the original arity theorem.

## 6. TECT-X stopping barrier

For complete primal graph K9, every four-key choice leaves one private component of five vertices with all four boundary neighbors. With no slice it fails width; with one sliced key and no dynamic cutset, each private vertex initially has seven remaining neighbors (four other private plus three keys). No reduced plan meets width three. By Section 3's equivalence, no original expanded q<=2 plan can meet the cost and width tests either. This is a scope-based counterexample to universal admission. It does not imply intractability: take m=2 and forbid (0,0) on every binary support, so every support genuinely present and the all-ones tuple is an original model, despite ineligibility. No larger slice search authorized automatically. Generalization requires a different information/complexity invariant or an independently justified new cost model.

## 7. MathOS executed evidence

The new standalone JS audit adapts SEP-001's streamed sorted bag joins and direct reference. Initial development run failed because only the first occurrence of a hard-coded private group index test was replaced for arbitrary partitions; corrected both occurrences and reran successfully. All final assertions passed. The revised script:
- Evaluates all 126 partitions each for symbolic K4,5 and K9. Old/new admission counts: K4,5 0/21, K9 0/0. Counts are structural plan eligibility, not measured runtime or fraction of arbitrary SAT instances.
- Compares reduced one-key admission against expanded planner on all 252 graph partitions plus 24 mixed binary/ternary scope fixtures, 276 comparisons. The exact equivalence follows from Section 3, not finite extrapolation.
- Evaluates nine actual K4,5 fixtures, m=2,3,4, two SAT and one UNSAT control at each m (UNSAT controls add an impossible private unary), with key-only ternary constraints and actual streamed message outputs; reconstructs one original model for each successful instance. SAT controls deliberately permit an all-zero model; additional later-slice control forces sliced key 0=2 and reconstructs [2,0,0,0,0,0,0,0,0]. Alternative non-natural partition [0,1,2,4] is solved directly at m=2 with slice [0] and nine feasible keys.
- Tests mixed static/dynamic cache with a static component depending on sliced key 0; exact counts 16 and 81 at m=2,3. Modular hidden control at m=8,q0=2 checks all 4096 actual visible tuples against residue sum, 2048 exact keys. No full nine-tuple enumeration for this large control, which uses independent modular identity.
- Counts from final audit: 746178 candidate elimination plans (includes repeated planner invocations and rejected orders); 283 eliminations; 70619 direct bag rows; 210 message cutset assignments; 3647 streamed batches; 283155 sorted membership checks; 2519 outgoing groups spanning a batch boundary; 10253 outgoing allowed tuple occurrences; 45 component witness reconstructions. New counters: 252 partitions; 45 key slices; 6 static message constructions; 165 dynamic message constructions (forward census, not reconstruction); 5349 key checks; 2723 feasible-key occurrences; 887407 full reference tuples; 36838 original model occurrences; 9954 direct component-message comparisons; 11 selected witnesses reconstructed. The inherited unused counters in the JS n object remain zero; use extra for this cycle's actual key/full/model counts.
- K4,5 fixture exact key counts (m; mode0,1,2): 2: 8,4,0; 3: 69,53,0; 4: 209,199,0.

The host audit retains sets of feasible keys and direct reference factor arrays for comparison. This is not production memory usage, a physical transition measurement, or a compiled global solver. Small test batches m^2-1 deliberately force split groups; the actual intended production chunk limit m^3 is larger. The slice-level join uses host indexed allowed sets, not the sequential physical joins specified in the ledger. Arbitrary scope planning is tested but not exhaustive over all possible nine-variable support hypergraphs. No normalized parser/output implementation, independent review, Lean certification or actual U-stage coverage.

## 8. TGA 2.0 status routes (executed locally)

The separate SEP-002 Python status module imports the original global graph and SEP-001 report. It does NOT alter either graph. Reconstruct the prior SEP claims from its returned claim records and add SLC-01 (sliced factorization/reduced planner), SLC-02 (slice lifecycle and physical ledger) and SLC-03 (uniform admission or alternative). All remain open for independently verified evidence. Sliced restricted route depends on SEP-001 restricted evidence plus SLC-01,02; sliced uniform route adds SLC-03 and SEP-06 (same-machine stage proof). This is conservative editorial bookkeeping: counts do not measure distance or imply mathematical necessity.

Both SEP modules and the global module were copied into a temporary local package and Git blob hashes matched the repository (SEP-001 71b360ce6387bebe2e7ac40d5b061dce9c4eefe7; SEP-002 412afe0eb8de85128a9dfa745faf7f4a19064bfa; global 3eaef82e22acf88c5c2991414013e36eeb9bc6d1). Use the extracted Claim/minimal/analyze core from the original gap_analysis.py (not the full module). Executed SEP-002 and global module assertions successfully. The original copy of the global module had a harmless formatting difference; corrected and verified its hash before final rerun. This is not full-repo CI or proof certification.

Local routes (all BLOCKED):
- SEP-001 restricted: SEP-01/02/03/04 (4)
- SEP-001 uniform: SEP-01/02/03/04/05/06 (6)
- SEP-002 sliced restricted: SEP-01/02/03/04 + SLC-01/02 (6)
- SEP-002 sliced uniform: SEP-01/02/03/04/06 + SLC-01/02/03 (8)

Global mathematical resolution routes (OR between these four, AND within each):
1. Direct unrestricted deterministic polynomial SAT algorithm: direct_sat (1).
2. Universal negative lower bound: universal_lower_bound (1).
3. Same selector algorithm, universal preservation and polynomial bit cost: selector_algorithm, selector_preservation, selector_bit_cost (3).
4. Existing certificate architecture: unbounded_codec, selected_bounds, machine_cost, ordinary_complete, short_proofs, discovery, decision_bridge (7).

All four are BLOCKED. The editorial evidence gate adds independent_review to every route; it is the only common unresolved modeled evidence package. The global mathematical resolution routes themselves have no common unresolved leaf. A one-package route can be as hard as the whole open problem; counts are not comparative difficulty, probabilities, or progress scores. The sliced restricted theorem is NOT an edge closing direct_sat or selector_algorithm, nor is a failed admission a universal lower bound. Do not promote any global leaf based on this finite experiment.

## 9. Research energy disposition

ADVANCE restricted sliced separator theorem to review. PRESERVE original arity theorem, parity/clique obstructions and exact SEP-001 factorization. DECOMPOSE the physical implementation and independent review; prioritize executing an actual normalized solver on the admitted structural class rather than expanding the conditional portfolio. RETIRE the inference that four-key exact messages must be stored whole, and the claim that slicing admits every scope graph. STOP automatic slice enlargement: the current charged planner already reduces to one key, and K9 remains outside it. Future research needs a new falsifiable invariant or an actual implementation audit. Decision PRESERVE_SLICED_ROUTE_REVIEW_BEFORE_EXTENSION. No certification or promotion. P versus NP, uniform recovery, unrestricted eventual exact cubic coverage and general SAT remain OPEN. Parent exact-head CI and new exact-head CI unconfirmed (empty combined-status and PR-triggered run results do not prove no push workflow ran).
