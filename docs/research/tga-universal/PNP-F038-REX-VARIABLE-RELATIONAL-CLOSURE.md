# F038-REX-024D7A — Certified relational closure and projected permutations

Parent D6Z dfdeca4c7eb3413b0bfbeb916dce68b05284d8a6. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Parent and scope
[D6Z Proctor 46088817691](https://github.com/tltmgnt/MathOS/actions/runs/46088817691) completed successfully at the exact parent commit. D7A adds host relational preprocessing and an independent certificate checker. The D6Z fixed binary canonical-stream physical worker and its descriptor are unchanged. No direct original raw-selector physical producer or on-tape relational preprocessing is implemented here.

## Semijoin theorem
For valid explicit factors A=(H_A,R_A), B=(H_B,R_B) with nonempty overlap I, replace R_A by {a in R_A : exists b in R_B, a|I=b|I}. A full satisfying assignment necessarily supplies such a row b, so deleting an unsupported row cannot remove a global model. The reverse implication holds since the new relation is a subset of the original. Sequential directed semijoins therefore preserve the exact global model set. An empty relation proves UNSAT. Iterate all ordered overlapping factor pairs until a sweep has no deletions. This is a fixed point under these semijoins, NOT a complete CSP decision criterion. Universal factors may be omitted by the inherited quotient before closure.

For f explicit factors of arity<=3, let R=sum |R_A|<=f*m^3. A changing sweep deletes at least one row, so <=R+1 sweeps suffice, unless an empty relation is detected earlier. The implementation constructs O(f^2) overlap pairs and uses projection sets of at most m^3 rows; O((R+1) f^2 m^3) row-projection/membership operations is a conservative bound per closure. This counts abstract set operations; explicit comparisons and index arithmetic admit polynomial bit-cost implementations. Space O(R+f^2) row/pair records, excluding optional certificate and intermediate round logs; logs contain at most R removed rows per closure. Independent replay uses direct row-to-row comparisons, with conservative O((R+1)f^2*m^6) comparison bound. No physical timing claim for either host algorithm.

At closure, a ternary factor may imply a binary permutation by its projection. Add such a projection when its binary scope is absent; it is implied by the ternary relation and hence preserves models. If a binary scope already exists, both projected sets agree at the nonempty fixed point by mutual semijoins. The inherited permutation quotient then contracts these edges, including newly tightened explicit binary factors. Iterate quotient and closure; every further outer round strictly reduces k, so at most k outer rounds. D6Z minimum-representative identity maps preserve lex order; composing reverse expansions preserves original least rank witnesses. Derived permutation relations are redundant implications, not assumptions. On certified contradiction the driver produces a constant one-coordinate empty unary relation for the binary physical worker, with no witness expansion permitted. Its constant worker time does NOT include the certificate construction or verification.

## Independent deletion certificate
A certificate lists changed ordered pairs (a,b) and exact removed rows in deterministic iteration order. Replay starts with the recorded input relations, independently searches all rows of B for agreement on shared coordinates for every A row, checks that the logged removed set is exactly the unsupported set, deletes it, and verifies the claimed final relation tables. It rejects invalid endpoints, wrong deletions, or changes after contradiction. If no empty relation remains, it independently checks support in every ordered overlapping pair. This certifies semijoin steps and the final fixed point or empty-relation contradiction, not the whole quotient implementation or the raw parser. Three deliberately corrupted deletion logs are rejected. Quotient/expansion correctness is separately supported by the D6Z theorem and exhaustive model-set tests.

## Inherited corpus and physical results
The 646 D6Z cases are independently replayed through D7A. 211510 source assignments, 5626 final reduced assignments, 3012 expanded models, 646 least-witness checks. 692 closure rounds, 148 changed pair operations, 242 certified deleted rows, 7723 independent row comparisons. 54 derived permutation factors. 178 contradictions are found without host enumeration on this corpus. For 558 binary cases the SAME D6Z descriptor is run on predecessor-reduced and D7A-reduced streams, with exact source clock/terminal encoding comparisons, original/minimized replay and one-short cutoff for new stream. Aggregate worker transitions 38981158 -> 6846537; 193 improve, 316 tie, 49 regress. The aggregate includes selected obstruction fixtures and is not a population estimate; host costs excluded. No universal performance dominance: redundant tightened constraints can lengthen the stream and slow candidate checking. Example SAT overlap chain has 4 models, 2 deleted rows and worker 48388 -> 64070 (62 ->84 stream symbols).

## Full extended audit
{
  "cases": 656,
  "sourceAssignments": 282745,
  "finalAssignments": 76663,
  "models": 3036,
  "sat": 472,
  "unsat": 184,
  "lexChecks": 656,
  "certificateRounds": 705,
  "certificateOperations": 157,
  "certifiedDeletions": 257,
  "certificateComparisons": 1415781,
  "closurePasses": 630,
  "projectionRows": 801908,
  "testedRows": 801942,
  "derivedPairs": 59,
  "contradictions": 179,
  "physicalCases": 562,
  "oldPhysical": 46154316,
  "newPhysical": 12448664,
  "improved": 195,
  "tied": 317,
  "regressed": 50,
  "exactClocks": 1124,
  "quotientReplays": 562,
  "cutoffs": 562,
  "tamperRejected": 3
}

All complete model sets and exact least rank witnesses agree. Actual physical worker runs on the new reduced streams match the original machine, minimized machine, exact source clock and one-short cutoff. No new descriptor compiled: 219 logical instructions,4934 original states,3683 quotient states,180471 minimized bits,12-bit identifiers. This descriptor does not accept the original raw selector directly. The host decoder, quotient and semijoin and witness reconstruction are excluded from transition counts.

## Named evidence
| fixture | k,m | old worker | new worker | deleted rows | result |
|---|---|---:|---:|---:|---|
|equality-barrier|4,2|2092|2092|0|UNSAT|
|equality-barrier|6,2|2092|2092|0|UNSAT|
|equality-barrier|8,2|2092|2092|0|UNSAT|
|pair-triple-barrier|4,2|327609|2092|7|UNSAT|
|pair-triple-barrier|6,2|3129327|2092|7|UNSAT|
|pair-triple-barrier|8,2|26268031|2092|7|UNSAT|
|projected-permutation|3,2|59901|338|0|SAT|
|overlap-chain|5,2|48388|64070|2|SAT|
|contradictory-chain|7,2|1529242|2092|13|UNSAT|
|dense-parity-barrier|6,2|5535627|5535627|0|UNSAT|

The D6Z pair-triple obstruction (all pairs at most one 1, first triple at least two 1s) is refuted by seven row deletions in one sweep, for k=4,6,8,10,12,16. The k8 reduced worker costs2092 instead of26268031 transitions. No enumeration by the host reference after contradiction. The projected-permutation cases at m=2,3,4 preserve respectively2,6,12 models and contract respectively3->1,3->2,3->2. For m2 the ternary itself implies three binary permutations. The additional contradictory implication chain is checked as a separate finite case.

## Surviving infinite parity obstruction
For each k>=6, include a parity relation on EVERY triple, with RHS 1 on triple {0,1,2}, RHS 0 on all other triples. Each relation has four allowed binary rows and every proper projection is universal. Distinct triples intersect in at most two variables; all shared projections are universal. Thus GAC and semijoin closure delete no rows, no permutation projection is found, and the complete primal graph admits no split after deleting <=2 vertices. Yet the four equations on triples 012,034,135,245 sum over GF(2) to 0=1, since each of the six variables occurs twice. The formula is UNSAT. These legal forbidden-tuple factors can be encoded by D6Y with polynomial raw length Theta(k^3). The implemented capped-separator/full-tuple fallback therefore examines exactly 2^k candidates, and the unchanged physical exhaustive worker likewise enumerates all 2^k candidates. Independent oracle verifies k6,8,10,12,16 (64,256,1024,4096,65536 candidates); k6 actual physical 5535627 transitions unchanged. Larger parity cases are host only. This is a barrier to these specific preprocessing/enumeration policies, not to arbitrary SAT solvers: Gaussian elimination immediately refutes the example. It also demonstrates why pairwise consistency of arity-three relations, even with every triple represented, is not enough.

## Next D7B
Implement sound affine-relation recognition and GF(2) elimination with independently replayable row-operation certificates and lexicographic witness recovery; explicitly account for mixed non-affine constraints rather than claim general SAT is affine. Investigate a uniform original raw-selector physical normalizer in a separate track. Unrestricted physical polynomial time remains open. Main and PR #248 not modified. D7A dedicated CI configured; completion unconfirmed.
