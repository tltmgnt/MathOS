# F038-REX-024D7O — Certified modular Boolean-domain inference

Parent D7N: 41a9c1dda6675ba2a4a44e055c3da9271d00521f. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Integer-source theorem

A checked even-sized tight counting block on v=2r coordinates with local orientation sigma forces exactly r normalized bits to be one. Since y_i=x_i XOR sigma_i=(1-2*sigma_i)x_i+sigma_i for Boolean x_i, every original model satisfies the integer equation
    sum_i (1-2*sigma_i)x_i = r - sum_i sigma_i.
This is stronger than its GF(2) reduction. It also gives a valid linear equation modulo any integer. Independently checked local unary parity rows x_i=b translate directly. Checked pair rows x_i XOR x_j=b translate to x_i-x_j=0 for b=0 or x_i+x_j=1 for b=1. A checked constant false parity row translates to 0=1. General parity rows of width greater than two do NOT translate to integer sums; only even balance rows with counting provenance do. Odd-sized tight blocks do not imply a single integer cardinality equation, and only their available pair consequences are used.

D7N discovery receives an optional retainEven=true flag, preserving even tight blocks even when their GF(2) rows duplicate previous rows. Distinct integer orientations can give distinct integer equations with identical parity. The default D7N behavior is unchanged. D7O reuses the local candidate portfolio, deduplicates integer rows by support, coefficient sequence and RHS, and attaches source indices and the exact extraction rule. Strict counting certificates are accepted directly by the inherited independent block checker.

## Fixed-prime elimination and Boolean residue theorem

For each p in the fixed ordered portfolio 3,5,7,11, reduce the integer source rows modulo p. Gaussian elimination over GF(p) produces a reduced row basis and explicit modular provenance coefficients for every row. Test original and final reduced rows. For any row a*x=b mod p, the reachable Boolean residue set is computed by
    R_0={0}, R_{j+1}=R_j union {r+a_j mod p : r in R_j}.
Induction proves R_k is exactly the set of possible row sums for all independent Boolean coordinates. If b is not in R_k, no original model exists. This includes constant conflicts, unary non-Boolean residues and wider unsupported residues. A consistent row or row basis is not a SAT certificate: row-wise witnesses need not agree across rows.

The certificate contains the original proof sources, integer rows, prime, nonzero modular combination coefficients, resulting row, RHS and reachable-residue bitmask. The checker independently verifies each counting or local source, checks the allowed integer translation rule, reconstructs the modular linear combination directly, and computes reachable residues using sets instead of the producer's bitmask recurrence. It does not trust row reduction, ranks, counters or supplied residue sets. The checker accepts only the fixed prime portfolio. The adapter maps checked contradictions to the existing one-coordinate empty unary factor. On UNKNOWN, it delegates the exact original residual to a supplied inherited reducer callback, or returns the original residual and identity expansion when no callback is supplied. The inherited D7N adapter path was actually tested on contradictory three-coordinate parity equations omitted by the integer source rule. A satisfiable four-coordinate balance block retains the original residual. No claim that modular elimination by itself is complete.

## Resource accounting

Let k be explicit coordinate count, f bounded-arity factor count, r distinct extracted integer equations. The inherited local discovery remains polynomial with at most O(k+f^2) distinct candidate unions; retention of additional even blocks adds polynomial certificate storage. At most r dense rows of k coefficients and r provenance coefficients are stored per prime. At most k pivots and rk row updates, each O(k+r) fixed-field operations, give O(rk(k+r)+r(k+r)) elimination/storage initialization work and O(r(k+r)) working words. Residue tests cost O(rkp) per prime. The four primes are fixed constants; all field intermediates fit the small integer arithmetic used by the implementation. Independent checking is polynomial in explicit proof and input size, including inherited BigInt counting arithmetic. This is a bounded modular relaxation, not exact rational/integer elimination, integer programming, or general SAT decision. No full physical cost bound follows.

## Executed evidence

423 exhaustive formula comparisons: 325 SAT,98 UNSAT,1499 satisfying model occurrences; all 276 local relation types, all 16 complement masks of the four-bit balance block, mixed-source and Fano fixtures,128 seeded mixed formulas and the prior 16-coordinate obstruction. 834 extracted integer rows and 874 proof sources checked; every satisfying assignment obeyed every extracted row. 92 modular contradictions and one strict counting contradiction independently verified; 330 UNKNOWN (325 SAT and five UNSAT). No observed false refutations. The 1826 residue oracle comparisons cover every three-coefficient vector over each configured prime and all eight Boolean assignments. Seven corrupted certificates rejected. Counts refer to the new stage alone, not incremental refutations over the inherited solver.

## Previous D7N obstruction eliminated automatically

The prior 16-coordinate,64-factor signed GF(4) plane instance has all sixteen local balance equations consistent at x_i=1/2 and GF(2) rank nine. D7O automatically discovers all sixteen integer equations and, without supplied multipliers, derives x_5=2 mod 3 using thirteen source rows. The reachable residues of x_5 are 0 and 1 only. Elimination rank 15,115 row updates,22 residue tests. A separate GF(5) run also certifies contradiction: x_5+3*x_14=2 mod 5, with reachable residues {0,1,3,4}; fourteen source references, rank 15,124 updates,22 tests. Both certificates independently checked. The globally complemented version succeeds as well.

To test representation robustness, give each occurrence of every original coordinate a fresh copy (64 coordinates,16 four-bit blocks) and link the four copies of each original coordinate by a chain of equality factors. Replace each of the 48 equality links by a path of length l with fresh intermediates. The resulting encoding has k=64+48(l-1) and f=64+48l. Each local balance block is recovered because its exact four-triple support is a candidate. Each equality factor produces an integer equality. Summing along a chain identifies its endpoints, and the original integer contradiction lies in the resulting row space. The implemented deterministic basis-row policy need not discover every unsupported row in an arbitrary representation; the following are executed results rather than a universal discovery claim.

|fixture|coordinates|factors|integer rows|prime|rank|row updates|combination size|predecessor processing|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|prior|16|64|16|3|15|115|13|yes|
|complemented prior|16|64|16|3|15|115|13|yes|
|signed split length 1|64|112|64|3|63|787|44|raw|
|signed split length 4|208|256|208|3|207|9697|143|raw|
|signed split length 16|784|832|784|3|783|161812|539|raw|

All five proofs independently verified without complete assignment enumeration for the structural decisions. Both predecessor tests retain all coordinates with zero local affine equations. Largest case includes 768 equality factors linking occurrences and fresh auxiliaries, not 784 independent original balance variables. All five terminal rows are x_5=2 mod 3 in their own coordinate numbering. No supplied multiplier vector was used.

## Physical replay

Actual modular adapter on the prior obstruction yields the ten-symbol constant contradiction stream. Original and minimized machines agree on UNSAT after 2092 transitions, independent exact clock 2092, one-short timeout 2091. Descriptor unchanged: 3683 states,180471 bits. No unreduced physical run or paired transition saving claimed; host discovery and certificate verification excluded.

## New policy limitation and verified conditional experiment

Use the same ordered sixteen GF(4) lines as D7N (four vertical lines, then slopes 0,1,2 with intercepts 0..3). Select zero-based indices [0,2,3,4,6,8,9,10,11,12,13,14] and flip local positions
    [2,3],[0,3],[],[0,1],[],[2,3],[0,3],[1,2],[0,3],[1,2],[1,2],[1,2].
All four triples of each signed four-coordinate block are imposed. The 16-coordinate,48-factor instance has zero models (all 65536 assignments checked). The all-half vector satisfies the integer balance equations over the rationals, and hence the all-inverse-two vector satisfies them over each configured odd prime. GF(2) row rank nine, consistent. Actual predecessor processing retains all coordinates with zero affine rows. D7O recovers 12 balance equations, rank 12 in every prime, but finds no unsupported original or reduced row: 24 residue tests each; row updates 70,72,72,72 for primes 3,5,7,11. This is a limitation of the configured single-basis, single-row test, not a lower bound for all modular combinations.

Separate inherited tree proof succeeds:7611 charged units,177 nodes,14 leaves,13 splits,150 units. Thus not an unresolved full-pipeline obstruction.

An exploratory conditional experiment is pinned in the audit. All 32 single-coordinate assignments fail to produce a modular refutation under the same portfolio. Of all 480 assignments to distinct coordinate pairs, 172 yield a modular conflict after appending the two unary assumptions (first successful prime:3 for 100,5 for 70,7 for 2). Each conditional proof is independently checked against the original residual augmented by those two exact unary factors. Discharging the assumptions gives 172 sound binary exclusions; an independently checked D7I implication certificate on the augmented view establishes contradiction using two four-edge paths. This is an executed experiment on one fixture, not a generic integrated conditional modular certificate or general closure implementation. No new physical result for this fixture.

## Next

D7P: implement general bounded conditional modular inference, independently verified assumption discharge, and nested implication/Hall composition. Retain only completed certificates under explicit budgets. Test the 48-factor obstruction and the limits of bounded assumptions and modular row bases. Avoid treating arbitrary assumption enumeration or integer programming as polynomial. Raw-selector normalization, on-tape inference and end-to-end resource accounting remain open.

All new audit sections executed separately in connector JS. A source-loop binding and adapter checker signature issue were fixed before execution. Main and PR #248 unchanged. Remote Proctor completion unconfirmed.
