# F038-REX-024D7Q — Certified local integer-affine hull extraction

Parent D7P: e76f00630a38ea0bc9fac8efd551a2397c60d712. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Local completeness theorem

For a nonempty Boolean relation of arity n<=3, choose an allowed row z0. The integer differences z-z0 form a matrix D. An affine equation c*x=b holds on all allowed rows exactly when D*c=0 and b=c*z0. The rational nullspace has dimension n-rank(D). It admits a rational basis of primitive integer vectors with coefficients in [-2,2]: if rank zero take coordinate vectors; if rank one use a nonzero difference entry +/-1 as pivot and one free coordinate at a time; if rank two in dimension three take the cross product of two independent difference rows, whose entries are minors bounded by 2, and divide their gcd. Rank n has no nonzero nullspace. Every nonzero primitive vector in this range has a coefficient of magnitude one. Thus enumerating at most 5^3 coefficient tuples, retaining first-nonzero-positive primitive vectors that satisfy D*c=0 and increase rational rank, recovers a complete rational basis. The producer uses fraction-free elimination at bounded local dimension and asserts basis dimension. Empty relations instead yield the vacuous contradiction 0=1. No claim of an integer lattice basis or completeness of its reduction modulo every prime.

The implementation sorts original coordinate indices and permutes coefficients, drops zero coefficients, normalizes sign, and deduplicates by support, coefficient list and RHS, retaining earlier D7O global balance and local parity sources. New integer-local certificates refer to an original factor and a sparse integer equation. The independent checker validates coordinate membership, coefficient bounds, and exact evaluation on each original allowed tuple. It need not trust basis completeness or producer rank for soundness. The checker partitions old and new source blocks, remaps old source indices and delegates their validation to D7P. Original global source indices are preserved in the actual modular combination. Assumption discharge uses the existing D7P independent residue verifier; the new checker independently reconstructs augmented tables and delegates nested contradiction verification to D7I. Strict-count proofs still use the inherited verifier.

A wrapper supplies the expanded source table to the unchanged conditional modular engine and preserves its caps (4096 probes,200000000 charged matrix-size units), prime portfolio and structural/fallback callbacks. On UNKNOWN the original residual is passed unchanged to the supplied fallback or returned with identity expansion. Checked contradictions reduce to the existing empty unary factor. No inherited module modified.

## Resource scope

Local arity bounded by three makes the exhaustive coefficient portfolio, exact rank and table validation constant-sized per factor (at most 125 candidates, eight allowed rows). The added source construction costs O(f) abstract operations and O(f) rows/words for f factors, excluding key handling and inherited discovery. At most three independent equations per nonempty factor (one contradiction for empty). Integer coefficients and RHS are small exact integers, with no unbounded elimination growth in local dimension. The rational basis spans every valid rational affine equality for the local relation, but it does not characterize all Boolean models in general. D7P's polynomial fixed-prime probing and proof-size bounds apply with the expanded row count; global source discovery and nested checking remain separate. The charged size proxy excludes those costs and physical execution. General SAT and integer programming remain open.

## Executed oracle

All 276 unary/binary/ternary Boolean relation tables (including three empty relations and reversed scopes): 167 basis/contradiction rows,157 nonempty full-dimensional tables. Independent determinant-minor rank oracle verifies basis dimension, independence, and every allowed tuple. Eight exact-one coordinate complement masks each produce three certified forbidden pair assignments. Overall 415 exhaustive comparisons:306 SAT,109 UNSAT,1286 satisfying model occurrences,310 exact augmented model-set comparisons,515 discharged records,104 direct modular contradictions,one strict count,two nested binary contradictions,308 UNKNOWN. No observed false refutations. Six tampered proof cases rejected. The previous conditional modular fixture still yields 172 independently checked exclusions and the nested contradiction. Zero probe cap and exact fallback identity passed.

Mixed-source fixture: a four-coordinate NAE balance block on 0..3, an exact-one factor on 4..6, equalities 0=4,1=5,2=6 and x3=0. Six-row modular contradiction over GF(3) combines one global tight balance, four inherited local unary/pair identities and one new local integer identity. Independent verification passed. The overlapping exact-one Fano control can be refuted by inherited strict counting; the audit accepts either sound terminal class instead of demanding a particular proof search order.

## Previous D7P source-language obstruction eliminated

Exact-one relation allows 100,010,001. Its integer affine hull is x_i+x_j+x_l=1 (whereas GF(2) parity alone is insufficient). In the regular cyclic family every coordinate occurs three times, and summation gives 3 sum x=k. If k is not divisible by three, the integer equations yield a contradiction modulo three. In arbitrary coordinate complements the same certificate exists with signed coefficients and appropriately shifted RHS. This is a family theorem about the available equation combination, not an assertion that the bounded implementation must discover it at every size or after arbitrary rewrites.

|coordinates/factors|complemented|predecessor processing|free affine coordinates|local integer sources|probes|row updates|charged size units|combination size|
|---:|---|---|---:|---:|---:|---:|---:|---:|
|31|no|yes|5|31|1|406|64512|31|
|127|no|yes|7|127|1|6186|4177920|127|
|127|yes|yes|7|127|1|6186|4177920|127|
|253|yes|raw|n/a|253|1|23230|32709612|253|

All four automatic certificates use one unconditional probe, one prime call (GF(3)), and independently verified full source-row combinations. No assignment enumeration for these structural decisions. Three predecessor experiments run actual relational and affine reduction, retaining the wide-fallback residual. Largest example is raw structural input. No adaptive branching used.

## Physical replay

Actual D7Q adapter on raw 31-coordinate instance: ten-symbol contradiction stream, original and minimized machines agree UNSAT in 2092 transitions; independent clock 2092; one-short timeout 2091. Descriptor unchanged:3683 states,180471 bits. No unreduced physical replay, no new paired transition savings, and host inference/checker costs excluded.

## New limitation: local inequalities without affine identities

On k=31 cyclic coordinates impose k factors on {i,i+1,i+3} allowing exactly the rows of Hamming weight >=2, and k factors on {i,i+4,i+9} allowing exactly the rows of weight <=1 (all indices modulo k). Each coordinate belongs to exactly three factors in each family. The first family implies 3 sum x >= 2k; the second implies 3 sum x <= k. These inequalities contradict each other for k>0. Every local table has four affinely independent points: the lower table contains 111 and its three single-bit deletions, the upper contains 000 and its three single-bit additions. No nontrivial integer affine identity holds locally, and neither table forbids a complementary row pair, so the global tight counting source discovery also has no eligible factors. These conclusions are invariant under coordinate complements.

Executed predecessor:31 free coordinates,zero GF(2) equations, no relational contradiction. D7Q checks all 62 local tables, finds zero integer rows, zero components and zero probes; UNKNOWN at complete configured source search regardless of probe cap. The separate inherited adaptive tree refutes in 4577 charged units,40 nodes,9 leaves,8 splits,23 units. This is a precise limitation of equality-based source extraction, not a full-pipeline barrier or general SAT lower bound.

## Next

D7R: certified local integer inequalities and nonnegative linear-combination contradictions. Extract valid supporting inequalities from bounded-arity relation tables, verify them on every allowed tuple, and seek tractable certificates (e.g. exact rational Farkas multipliers for LP infeasibility, or a restricted deterministic nonnegative combination search with explicit bounds). Target the 62-factor regular inequality contradiction; distinguish LP feasibility from Boolean feasibility and investigate inequalities requiring integrality. No assumption that arbitrary integer programming is polynomial. Raw-selector normalization, on-tape inference and complete end-to-end accounting remain open.

All four new audit sections executed separately in connector JS. An overly restrictive oracle assertion about the Fano control was corrected and rerun. Main and PR #248 untouched. Remote Proctor completion unconfirmed.
