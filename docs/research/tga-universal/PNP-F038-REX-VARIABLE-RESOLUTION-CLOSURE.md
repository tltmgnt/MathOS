# F038-REX-024D7C — Certified bounded-width resolution and non-affine consistency

Parent: D7B Proctor configuration commit 70b55478fe9ff496855b361e006c7c8d9bc5bec3. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE. Global routes 0/4; Omega obligations 0/6.

## Exact forbidden-row encoding and proof rules
For each binary-domain factor on distinct coordinates of arity at most three, introduce one disjunctive clause per forbidden local tuple: literal x_i for forbidden bit 0 and not x_i for forbidden bit 1. The clause is false precisely on that tuple. Conjunction of all such clauses is therefore exactly the original relation, with no auxiliary variables. Duplicate clauses can be omitted.

Resolution on C containing p and D containing not p derives (C minus p) union (D minus not p). Any assignment satisfying both parents satisfies the resolvent: otherwise all remaining literals are false and the parents demand opposite pivot values. The producer discards tautologies, duplicate resolvents, and resolvents wider than a fixed cap w=3 or 4. It checks every pair in a growing queue until empty clause or saturation. An empty clause is a sound UNSAT certificate; saturation without empty clause returns UNKNOWN, never SAT. The checker independently checks every source clause against its original factor's unique forbidden row, verifies earlier parent indices, pivot polarity and exact literal membership, and requires an empty final clause. UNKNOWN leaves the input and witness map unchanged. A checked contradiction alone yields a constant one-coordinate empty relation for the inherited physical worker.

## Five-coordinate cardinality certificate
If five distinct Boolean coordinates have all ten triples constrained by factors excluding both 000 and 111, then the five coordinates cannot be assigned: at least three share one of two values. The certificate lists the five coordinates and the ten original factor indices. Independent verification checks range, distinctness, each exact triple scope and absence of both monochromatic rows. The rule works even for strict subsets of NAE. A complete dense-NAE family has such a certificate for every k>=5, and the first five-coordinate trial succeeds. A k4 dense NAE fixture has six models; it is not refuted. This is a specific polynomially detectable obstruction, not a general cardinality solver.

## Resource theorem and limitations
For fixed w, the number of distinct non-tautological clauses of width at most w is N=sum_{i=0}^w 2^i binom(k,i)=O(k^w). The queue visits at most N(N-1)/2 pairs, each with O(w^2) literal comparisons, after O(f) bounded-arity row encoding. Thus the implemented resolution stage uses O(f+k^(2w)) abstract operations, O(N) bounded-width clause/proof records, with polynomial integer/string bit costs. Width four gives O(f+k^8), not a practical universal speed guarantee. Proof checking uses O(N) bounded-width local checks, plus factor lookups and index arithmetic. The five-coordinate search indexes O(f) factors and checks at most binom(k,5) candidate cores, giving O(f+k^5) abstract operations. The implementation's clause/coordinate keys have logarithmic bit length. These are host costs.

No bound on unrestricted resolution width or proof length is asserted. The procedure is incomplete in general; unresolved cases must retain the exact prior stream and use a complete fallback. No arbitrary SAT polynomial-time claim follows. Physical raw normalization, on-tape affine and resolution preprocessing, full physical witness reconstruction, and universal physical time remain open.

## Actual finite evidence
Executed in JavaScript from the committed producer/checker code with an independent exhaustive model oracle: 925 model-set comparisons, 2398 preserved models, 652 SAT cases, 273 UNSAT cases, 273 certified refutations, 276 local relation types, 6 intentionally corrupted certificates rejected. No unresolved UNSAT on this selected corpus; not a completeness result. Dense NAE k5,6,8,10,12,16 and 32 has ten-factor certificates and zero search candidates at the decision stage (small oracle checks still enumerate; k32 is certificate-only).

On dense NAE5, width three saturates at 20 clauses / 190 pair checks, no refutation. Width four reaches empty clause with 211 nodes (including 20 axioms) and 20908 pairs. Width-three failure also follows directly because opposite-sign triples sharing one variable give width four, while sharing two or more gives a tautology. Two sparse non-affine resolution-only fixtures have no five-clique cardinality certificate:
| fixture | k | factors | width3 clauses | width4 nodes | width4 pair checks |
|---|---:|---:|---:|---:|---:|
|Fano plane|7|7|14|939|432914|
|Affine plane over GF(3)|9|12|24|2851|4028536|

Both survive preceding relational and affine preprocessing, with zero extracted equations and all coordinates free. Both are independently oracle-UNSAT and checked by width-four resolution. The nine-coordinate experiment is host-only.

## Actual inherited physical worker replay
Five selected cases, with D7A then D7B preprocessing and independent affine verification, then D7C verified adapter:
| fixture | before | after | result |
|---|---:|---:|---|
|NAE5|3815854|2092|UNSAT, cardinality|
|NAE4|95554|95554|SAT, unknown fallback|
|Fano|11556172|2092|UNSAT, resolution|
|narrow mixed|7848|7848|SAT, unknown fallback|
|wide mixed|134197|134197|SAT, unknown fallback|

Total 15609625 -> 241783 worker transitions, 15367842 eliminated. Exact original/minimized new-stream replay, ten exact clock comparisons and five one-short cutoffs passed; original least witnesses checked against exhaustive oracle. The descriptor stays at 219 logical instructions, 4934 original states, 3683 minimized states, 180471 minimized bits. Host preprocessing and certificate verification are excluded. These are five selected fixtures, not a population estimate or total-time speedup.

Dedicated D7C Proctor is configured separately with inherited D7B/D7A/D6Z/D6Y and governance gates. A remote CI pass is not asserted until observed. Main and PR #248 not modified. Next investigate a concrete residual bounded-width obstruction after all stages, use an independently checked stronger proof system or adaptive resource-bounded strategy without claiming polynomial general resolution, and pursue raw physical normalization separately.
