# F038-REX-024D7S — Certified bounded cutting-plane rounding

Parent D7R: 6153458d8de5c7377e61267949c8d92b90e98c6e. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Integer rounding and proof soundness

Use D7R checked local supports a*x<=b. Nonnegative integer sums of valid inequalities remain valid. If a positive integer g divides every left coefficient, then (a/g)*x is an integer on Boolean assignments; hence (a/g)*x<=floor(b/g). Negative RHS must round toward negative infinity, not toward zero. For a terminal row A*x<=B, the box minimum L=sum min(0,A_i) is a lower bound on every assignment, and L>B certifies UNSAT. This is a restricted Chvatal-Gomory cutting-plane proof system with exact integer arithmetic.

A certificate is an ordered DAG of source, sum and divide nodes. A source refers to an original local relation and checked inequality. A sum lists nonempty earlier parent indices (repeated parents encode positive integer multiplicities). A divide lists one earlier parent and a positive decimal integer divisor >1. The independent checker validates source rows by D7R's allowed-table evaluator, checks strictly earlier dependencies, reconstructs every coefficient and RHS using BigInt, checks exact divisibility, computes floor independently of the producer, and recomputes the terminal box minimum and strict contradiction. Every proof node is sound by induction. No trust in producer grouping, bounds, metrics or inference order is required. The verifier supports nested sums and divisions even though the automatic discovery policy is more restricted.

## Bounded discovery

For each factor, enumerate inherited supports and select at most one full-scope +/-1 normal with greatest positive gap between box maximum and RHS, breaking ties by source enumeration order. Empty relations give immediate 0<=-1. Group selected supports globally by arity, allowed-row count and gap. Sum each group's rows, divide by the gcd of all nonzero coefficients if >1, and test the box minimum. Look for exact opposite normalized coefficient vectors with incompatible RHS using a canonical signed map; sum the opposing rows to certify contradiction. No unrestricted combinations, subfamily search, or iterative cut generation. Grouping is global rather than component-local; unrelated factors can obscure useful cuts. Ties need not be invariant under arbitrary complements outside the specified family.

Default 4096 proof-node cap, configurable 0..100000; if a needed node does not fit, report budget, not saturation. Without a proof report UNKNOWN (portfolio-exhausted or budget). Checked contradictions reduce to the existing empty unary factor. The optional fallback receives the exact original residual; actual inherited D7R delegation and identity fallback were tested. No inherited module modified.

For k coordinates and f bounded-arity factors, local scan O(f) (at most 98 supports per ternary factor); selected sources <=f. The number of group keys is bounded by a constant because arity, allowed-row count and positive integer gap are bounded. Group sum work O(f), gcd and canonical ordering O(k log(k+1)) per group with polynomial bit overhead. Producer stores O(f+k) words and creates at most f+2G+1 nodes for G groups, subject to the node cap. Coefficients and RHS magnitudes O(f) before and after division; the generated proof has O(f+k) abstract words. For arbitrary explicit proof DAGs the checker is polynomial in input/proof size: at most k nonzero entries per row and polynomial integer bit growth (sum magnitudes grow by at most the number of listed parent references per node, and division does not increase absolute magnitudes except floor rounding toward -infinity). This is not a complete LP or integer programming solver and does not bound the inherited fallback or physical execution.

## Prior D7R integrality obstruction eliminated

For k cyclic coordinates, the two families of k factors each require at least one on {i,i+1,i+3} and at most one on {i,i+4,i+9}, modulo k. For the tested sizes every coordinate occurs three times in each family. Their allowed-row counts are seven and four respectively. The chosen support for the first family is -sum<=-1 (the only full-scope sign vector excluding the forbidden vertex); the second chooses sum<=1 (unique greatest positive gap). Under arbitrary independent coordinate complements the normals and RHS translate, the box gap is invariant, and each family stays in its original group. Summing and dividing by three yields incompatible integer bounds if k is not divisible by three; under complementation the same signed aggregate uses the corresponding integer shift. For k=31 this is sum x>=11 and sum x<=10. Adding gives 0<=-1. The specified family admits the automatic proof when scopes are distinct, k is not divisible by three, and the proof fits the node cap. No complete assignment enumeration for the large decisions.

|coordinates|factors|complemented|predecessor|support scans|proof nodes|division nodes|
|---:|---:|---|---|---:|---:|---:|
|31|62|no|yes|6076|67|2|
|31|62|yes|yes|6076|67|2|
|127|254|yes|yes|24892|259|2|
|1001|2002|yes|raw|196196|2007|2|

All four independently verified with final 0<=-1 and two divisor-three nodes. Actual relational and affine predecessor processing in the first three leaves all coordinates free, zero affine equations. Largest case is raw structural input.

## Oracle and physical results

472 exhaustive formula comparisons: 331 SAT,141 UNSAT,2858 satisfying model occurrences. 276 local relation types,192 seeded mixed formulas, two 11-coordinate rounding fixtures (one complemented), a divisible-size 12-coordinate UNSAT control (not resolved just by the regular count), and the satisfiable 12-coordinate lower-family-only control (1256 models). 115 verified contradictions,357 UNKNOWN (331 SAT and 26 UNSAT),422 proof nodes,5 division nodes; zero observed false refutations. Six corruptions rejected: nondivisible divisor, zero divisor, self-dependency at division, self-dependency at sum, invalid source inequality, wrong final RHS. Signed floor tests pass. Zero-node fallback preserves exact original object; a 26-node cap on the 27-node 11-coordinate proof reports budget. The actual inherited D7R two-round proof succeeds when D7S is capped at zero. Stage-specific corpus, not new refutations relative to full pipeline.

Actual D7S adapter on raw 31-coordinate prior obstruction maps to ten-symbol stream; original/minimized agree UNSAT at 2092 transitions, independent clock 2092, one-short cutoff 2091. Descriptor unchanged:3683 states,180471 bits. No unreduced physical run, no paired savings or host cost inclusion.

## New limitation: automatic discovery of nested clique cuts

Use n disjoint groups of four coordinates, with all six binary mutual exclusions per group. For each of four layers j and cyclic group i, require at least one of x_(i,j), x_(i+1,j), x_(i+3,j). Each variable occurs three times in these 4n lower factors. Every original model would obey sum x>=ceil(4n/3), while each four-coordinate clique permits at most one true bit, so sum x<=n. Contradiction for n>0. The all-one-third vector satisfies all local convex supports. The automatic policy groups all binary exclusions together and only derives sum x<=2n, while the lower group yields sum x>=ceil(4n/3), which is not a contradiction. It reports UNKNOWN on the following actual residuals after predecessor processing (all coordinates free, zero affine rows).

A manually constructed two-level proof is independently checked by the general DAG verifier: sum the three exclusions of each triangle, divide by two and floor to obtain its sum<=1; sum all four triangle cuts within each K4, divide by three and floor to obtain sum<=1 for that clique; combine these clique cuts and the rounded lower aggregate. No claim that two rounds are necessary for every possible cutting-plane proof. The producer does not yet discover these local groups or nested cuts.

|coordinates|factors|automatic nodes|automatic bounds|fractional source checks|manual DAG nodes|manual divisions|terminal RHS|separate inherited tree nodes|
|---:|---:|---:|---|---:|---:|---:|---:|---:|
|20|50|54|7<=sum<=10|2440|103|26|-2|84|
|28|70|74|10<=sum<=14|3416|143|36|-3|84|

Separate inherited tree verification passes (1986 and 2410 charged units respectively), so this is a limitation of the automatic grouping policy, not an unresolved full-pipeline obstruction, cutting-plane rank lower bound or general computational hardness result.

## Next

D7T: automatic certified local clique cuts and nested aggregate closure. Recover explicit binary mutex triangles and four-cliques, including signed occupancy coordinates, construct the checked two-level proof without supplied groups, and compose with lower bounds. Bound candidate enumeration and proof resources; distinguish fixed-size clique discovery from arbitrary maximum clique. General SAT, raw-selector normalization, on-tape inference and full physical accounting remain open.

All five new sections executed in connector JS against committed source. Corrected verifier adapter argument alignment, a misleading initial divisible-size control label (it was UNSAT), and terminal division metrics; reran all sections successfully. Main and PR #248 untouched. Remote Proctor completion unconfirmed.
