# F038-REX-024D7D — Adaptive certified inference and a width-four obstruction

Parent D7C 4555217fef984ac5a5c770d00a09be4597d7a563. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Indexed bounded resolution and subsumption

Use the D7C exact forbidden-row clause encoding. For a parent clause of length a, a second parent of length b, and one complementary pivot, a non-tautological resolvent has width a+b-2-s, where s is the number of shared same-sign nonpivot literals. Hence a width-w eligible pair requires at least max(0,a+b-2-w) shared literals. With w=3 or 4, this threshold is at most two. Index by parent length, signed pivot, and every subset of zero, one or two nonpivot literals. Query opposite pivots with the required subset size; deduplicate candidate indices and test exact resolution. This skips no eligible pair between retained clauses.

If a retained clause subsumes a new clause, omit the new clause. If the new clause subsumes a retained clause, deactivate the latter but preserve its proof node for replay. Every removed clause remains covered by some retained subset (possibly through a chain of removals). Every accepted proof node is either an exact source clause or a sound resolvent. The inherited D7C verifier checks refutation certificates independently of indexing or subsumption.

For fixed w, there are N=sum_{i=0}^w 2^i binom(k,i) possible non-tautological clauses. Since a removed clause remains covered, it cannot be reintroduced. There are at most N accepted nodes and O(N) postings for fixed w. The conservative abstract bound including candidate sorting is O(f+N^2 log(N+1)), excluding bit-cost details; explicit clause keys and indices have polynomial bit lengths. The producer counts budget units for probes, posting visits, pair iterations, subset lookups, subsumption scans, index insertions and outer iterations. This is an abstract counter, not a measurement of total host runtime; source encoding and candidate sorting are not separately charged, and the preceding cardinality search and subsequent certificate verification are outside this counter. Budget exhaustion is UNKNOWN. The finite audit uses independent closure verification instead of relying on an unverified saturation claim.

## Independently checkable obstruction to bounded resolution

A closure witness L is a set of nonempty canonical clauses of width at most w such that (i) every original clause contains a member of L and (ii) every non-tautological resolvent of two members of L of width at most w contains a member of L. This suffices to prove that no width-w resolution refutation exists, even without proving that every member of L is derivable. Induct on any bounded-width derivation: axioms satisfy (i); if a covering parent subset omits its pivot it already covers the resolvent. Otherwise the two covering subsets resolve, with a non-tautological resolvent contained in the original resolvent and of no greater width. Apply (ii). The empty clause has no nonempty subset, contradiction. The checker independently reconstructs axioms and uses an all-pairs signed-variable merge to test closure; it does not use the producer's index, queue, or deletion logic.

Concrete obstruction: six pigeons, five holes. Let x_{i,j} indicate pigeon i uses hole j. Every pigeon has an at-least-one constraint; every pair of pigeons is forbidden from sharing a hole. No at-most-one restriction per pigeon is needed: choosing one occupied hole per pigeon would still be an injection. Split each five-literal positive clause into three ternary clauses using two fresh Boolean variables: (a or b or u), (not u or c or v), (not v or d or e). Their existential projection is precisely the original disjunction. There are 30 original variables, 12 auxiliary variables, 18 ternary clauses and 75 binary clauses. Thus 42 coordinates and 93 factors, within the existing binary arity-three interface. The pigeonhole principle proves UNSAT.

Executed predecessor integration leaves all 42 coordinates free, zero extracted equations, no relational contradiction and no five-coordinate cardinality certificate. Independently verified width-four closure witness:
- 10750 generated clause records; 10030 retained nonempty clauses.
- 39042 processed resolution pairs; 57274 posting visits; 307724 index probes; 5408364 charged work units.
- Independent checker covered 93 axioms, examined 50295435 unordered pairs and checked 38052 eligible resolvents.

This is a concrete certified failure of ALL width-four resolution refutations for the actual residual instance, not merely a timeout, and not a lower bound on arbitrary SAT algorithms. The closure witness does not itself certify satisfiability or unsatisfiability.

## Budgeted tree refutation

A tree certificate contains three node types: conflict (an exact source clause false under the current partial assignment), unit (an exact source clause with exactly one unassigned literal and all others false, followed by the forced assignment), and split (an unassigned coordinate with both Boolean branches). Induction on the tree proves no satisfying extension of the current partial assignment. The independent checker validates each referenced factor and unique forbidden tuple, replays partial assignments, checks forced values and requires both split children. The producer searches with a shortest-open-clause heuristic, counts one work unit per recursive call and per clause visited, and returns UNKNOWN on exhaustion or on encountering a model. No partial tree is accepted as a refutation. Recursion depth is at most k; the current host implementation uses recursion and is not a universal physical stack implementation. Worst-case tree size and unbudgeted search are exponential; checking a supplied tree is polynomial in its explicit size and input representation. The budget cap does not establish complete polynomial SAT decision.

The adapter tries D7C cardinality, then indexed width-four resolution, then budgeted tree inference. Default two million charged units per inference stage. If neither stage produces a verified contradiction, preserve the exact input stream and identity expansion. A certified contradiction alone maps to the inherited one-coordinate empty unary factor. For the 42-coordinate residual, default resolution budget exhausts; tree proof succeeds with 6912 nodes (474 conflict leaves, 473 splits, 5965 unit nodes), 468006 charged work units. The separate 20-million-unit saturation experiment proves the stronger bounded-width obstruction. With 1000 units per stage both stages exhaust and the exact original residual is retained.

## Executed evidence
919 complete model-set comparisons; 2398 satisfying models; 652 SAT and 267 UNSAT cases; 265 indexed resolution refutations, one tree refutation and one cardinality refutation. No unresolved UNSAT in the selected small model-oracle corpus. All 276 local relation types covered. Five corrupted closure/tree certificates rejected. The 42-variable pigeonhole case is additional, verified by certificate rather than exhaustive model enumeration.

| fixture | D7C pair checks | D7D processed resolution pairs | D7C nodes | D7D nodes |
|---|---:|---:|---:|---:|
| Dense NAE5 (resolution only) | 20908 | 379 | 211 | 124 |
| Fano plane | 432914 | 3094 | 939 | 653 |

Pair-count comparisons exclude index and subsumption work and do not establish total-time acceleration. D7D charged work for these two cases is 13448 and 156139 respectively, with different work-unit semantics from D7C pair counts.

The 42-coordinate pigeonhole contradiction stream (10 symbols) was executed through the unchanged D6Z original and minimized physical descriptors. Both agree at 2092 transitions, UNSAT with no witness; exact source clock and one-transition-short cutoff pass. No full 42-coordinate predecessor physical replay was attempted, so no measured physical transition savings are asserted for this fixture. All algebra, indexing, proof generation and checking remain host-side. The descriptor remains 3683 minimized states and 180471 bits.

## Next
Investigate structure-aware counting/matching certificates for pigeonhole and resource-bounded proof systems with new verified surviving obstructions. Separate proof-generation, verification and physical resource accounting. Direct original raw-selector physical normalization remains open. Main and PR #248 are untouched. D7D dedicated Proctor configuration is separate; remote pass not claimed until confirmed.
