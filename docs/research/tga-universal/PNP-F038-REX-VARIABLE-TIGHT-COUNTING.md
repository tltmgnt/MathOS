# F038-REX-024D7M — Certified tight counting, parity quotient and composition

Parent D7L: 14dfb00b6da7ab5806de9552e11f550d0bccb1ab. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Tight-bound theorem

Use the D7L selected original factor indices and Boolean orientation sigma. In the normalized coordinates y=x XOR sigma, each selected factor implies NAE. Write m for the selected factor count, v for the number of coordinates in their union, w_ij for pair multiplicities (including zero), e_ij=[y_i=y_j], and b(v)=binom(floor(v/2),2)+binom(ceil(v/2),2). Every model satisfies sum w_ij e_ij=m. For positive integer t, D(t)=sum max(0,t-w_ij). The D7L inequality is sum w_ij e_ij >= t*b(v)-D(t).

If the bound equals m, the following exact slack decomposition is zero:
    m-(t*b(v)-D(t))
      = t*(sum e_ij-b(v))
        + sum_{w<t} (t-w)*(1-e_ij)
        + sum_{w>t} (w-t)*e_ij.
All terms are nonnegative integers. Therefore every model has a balanced coloring on the selected coordinate union; every pair with w<t has equal normalized bits and every pair with w>t has unequal normalized bits. In original coordinates the pair equation is x_i XOR x_j = sigma_i XOR sigma_j XOR [w_ij>t]. Pairs at w=t are not constrained by this pairwise slack rule. A strict positive lower-bound margin instead gives D7L contradiction. The proof also holds for unsatisfiable selected subsystems (vacuous consequences). The implementation extracts pair equations only; the balanced-cardinality consequence is recorded here but not compiled into a higher-arity equation.

## Candidate discovery

Use D7L unsigned and greedy compatible signed orientation proposals. For each incidence-connected component and every coordinate's closed neighborhood in the pair-incidence graph, consider the induced selected triple subsystem. Deduplicate by selected indices and full orientation vector. Evaluate D7L's best positive weight breakpoint. When the maximum bound is tight, emit all nonthreshold pair equations if at least one exists; when strict, emit a D7L certificate. This is a deterministic portfolio of at most 4k candidates per round, not exhaustive subsystem selection. We use one maximizing threshold (ties use the first), not all tight thresholds, and do not claim completeness of the sign heuristic. This neighborhood portfolio differs from the D7L peeling search; if the new closure is unresolved, the unchanged original input goes to D7L and its inherited fallback so previous coverage is not discarded.

## Exact quotient and independent checking

Apply each stratum's equations together. Parity union of components checks cycles; an inconsistent cycle is a contradiction. Otherwise each coordinate x_i is represented as z_r XOR p_i, with each component's least original coordinate the representative and representatives ordered increasingly. Substitute into every factor, collapsing repeated representative coordinates, retain exactly the compatible rows and omit tautological factors. Empty allowed tables certify contradiction. A nonconflicting quotient is a bijection of model sets: restriction to representative values is inverse to expansion; the equations hold on every original model and the substituted tables test all original factors exactly. Lexicographic order is preserved: the first coordinate at which expanded assignments differ is the least representative of the first differing representative bit, whose parity is zero. Composition preserves the order as well.

The verifier checks each selected index, complementary forbidden rows, multiplicity, balanced lower bound, tight equality and the complete claimed pair list independently. It reconstructs each quotient using graph BFS (rather than union-find) and enumerating all local quotient tuples (rather than filtering original allowed rows). A strict counting proof is checked against the independently reconstructed final view. Parity-cycle or empty-factor contradictions must occur at the final listed stratum and match its claimed terminal kind. Thus the verifier does not trust producer candidate selection, quotient construction, metrics, or round limit. A separate explicit inconsistent-parity certificate from two signed gadgets was verified, without claiming that the global greedy discovery necessarily finds that particular batch.

Each nonempty consistent stratum merges at least two coordinates. At most k-1 such strata are possible for k>=1, with at most one terminal conflict stratum. Default round cap eight; a cap is not saturation. The implementation maps a verified contradiction to the inherited constant empty unary factor. On unresolved closure, it intentionally retains the original representation and invokes inherited D7L/D7K/D7D. The exact quotient is separately exposed for experiments, including SAT witness replay, but is not passed to the SAT fallback in this adapter.

## Conservative polynomial resource bounds

For k explicit coordinates and f bounded-arity factors, each of O(k) candidate subsystems can be collected, counted, sorted and checked for O(f log(f+1)+k^2+k) abstract operations. Up to O(k^3) pair equations may be emitted per round; the simple least-root union implementation has worst-case O(k) find depth, giving a conservative O(k f log(f+1)+k^4+k) per-round bound. Factors never increase in number under quotienting. At most k nonempty strata plus a final test yield O((k+1)*(k f log(f+1)+k^4+k)) abstract operations, or fewer under the configured round cap. The explicit certificate uses polynomial space: O(k(f+k^2)) words per stratum for source lists, orientations and equations, O(k^2(f+k^2)) overall. Checker costs are polynomial in input and proof size, with exact integer bit overhead. These are host-stage bounds, not general polynomial SAT decision or end-to-end physical accounting.

## Executed oracle and composition evidence

728 exhaustive small-formula comparisons, 629 SAT, 99 UNSAT, 7351 satisfying model occurrences. Includes 276 local Boolean relation types, all 128 complements of the Fano-minus-line gadget, 64 factor subsets of that gadget, all 128 complements of the weighted gadget, 128 seeded mixed formulas, and four named composition fixtures. 264 tight blocks, 920 certified pair equations, 262 nonempty strata, 260 independently reconstructed ordered model-set bijections, maximum two strata. 725 noncontradictory views preserve complete original model sets; three contradictions independently checked. No observed false refutations. Six tampered certificates rejected. Counts refer only to this new closure, not the complete inherited solver. The explicit parity-cycle certificate was checked separately (six pair references).

Local Fano-minus-line has ten models and three equality equations; quotient reduces 7 to 5 coordinates. Adding NAE(0,1,3) to the six factors creates a nonuniform weighted tight subsystem (eight models), deriving x0=x2, x0!=x3, x1=x2, x1!=x3. A split-coordinate version of two Fano gadgets has 50 models, requires two quotient strata (13 -> 11 -> 9 coordinates), and preserves ordered complete model sets. Adding NAE(7,8,2) makes that variant UNSAT, detected by a strict count on the second view. A one-round cap on the SAT variant retains 11 coordinates and reports round-limit. These tests demonstrate genuine inter-round composition, not just simultaneous union.

## Previous D7L structural obstruction eliminated

The prior two-copy, 13-coordinate formula (two Fano-minus-line blocks sharing coordinate 0, plus NAE(1,2,7)) now yields two tight blocks. Each contributes three pair equations; combining them forces all three coordinates of the final NAE equal. The independent checker reconstructs the empty factor. The signed variant also succeeds after actual relational and affine predecessor processing (all free, zero affine equations). Neither adaptive resolution nor tree inference is invoked.

|fixture|coordinates|factors|candidate tests|tight blocks|equations|predecessor processing|
|---|---:|---:|---:|---:|---:|---|
|prior|13|13|7|2|6|yes|
|signed prior|13|13|9|2|6|yes|
|five-gadget chain|31|31|16|5|15|yes|
|signed twenty-gadget chain|121|121|81|20|60|yes|
|signed hundred-gadget chain|601|601|401|100|300|raw|

Each chain shares one missing-line coordinate with the next gadget; a final NAE involves two first-block coordinates and the last block's missing-line coordinate. All five certificates independently verified factor-conflict in one stratum, without complete assignment enumeration. The 601-coordinate test is raw structural input, not a full predecessor/physical run. The adapter smoke test confirms the prior obstruction maps to one empty unary factor.

## Executed physical replay

|fixture|coordinates|stream symbols|physical transitions|status|
|---|---:|---:|---:|---|
|Fano-minus-line original|7|248|562336|SAT|
|independently reconstructed quotient|5|186|327472|SAT|
|constant contradiction stream|1|10|2092|UNSAT|

The SAT quotient experiment eliminates 234864 transitions (about 41.77 percent), preserving the least expanded witness 0,0,0,0,1,1,1. Three original/minimized agreements, three independent exact clock checks, three one-short cutoffs passed. This is a paired physical experiment on the separately exposed quotient, not incremental savings of the production adapter (which retains the original residual on UNKNOWN). Host costs excluded; descriptor unchanged (3683 states,180471 bits). Larger unreduced streams not executed. The prior D7L disconnection was not repeated for these completed replays.

## New structural limitation: balanced-block higher-order parity

Use the ten edge coordinates of K5. At each of its five vertices take the four incident edges and all four NAE triples on them. At vertex zero complement one incident coordinate consistently across that local block only. Each block forces exactly two normalized ones among four bits: if three or more are equal, their triple violates NAE. Conversely exactly two ones satisfies all four triples. This is also tight counting with t=2, v=4, b=2, m=4, all six pair weights equal to two. There is no individual pair equation: any chosen pair can be equal or unequal in some balanced local assignment.

Each four-coordinate block implies XOR of its normalized coordinates equals zero, and hence an equation in the original coordinates with right-hand side the XOR of its local signs. Every edge coordinate occurs in exactly two blocks. XOR of the five equations cancels all coordinates but gives right-hand side one, a contradiction. This derives UNSAT without searching assignments. The 1024-assignment oracle also confirms zero models.

Actual predecessor run: ten free coordinates, zero locally extracted affine equations, 20 ternary factors. D7M tests 20 candidates, emits no tight pair blocks, reaches fixed point. D7L counting UNKNOWN; D7K fixed point after 2421 charged units,141 probes,2280 inspections, zero derived short clauses. Separate inherited tree verification succeeds in 3398 charged units,127 nodes,22 leaves,21 splits,84 unit nodes. This is a structural-policy limitation, not a proof of failure of all subsystem selections or an unresolved full-pipeline instance. The local balanced-block signs are inconsistent globally, so a global orientation cannot recover all five blocks simultaneously; local orientation discovery is part of the next challenge.

## Next

D7N: independently certified balanced-cardinality consequences and higher-order affine composition. For a tight even-sized normalized subsystem v=2r, balance forces sum y_i=r and XOR y_i=r mod 2. Recover the local sign orientations separately, generate general GF(2) rows with explicit source certificates, compose them by independent elimination, and test the five-block contradiction. Investigate limits for odd-sized balance and nonlinear cardinality constraints. General SAT, unrestricted physical polynomial execution and raw-selector normalization remain open.

## Execution scope

All committed audit sections executed separately in the connector JS runtime; an adapter smoke-test argument-alignment error was fixed and the test rerun successfully. No main or PR #248 modifications. Dedicated Proctor configured; remote completion unconfirmed.
