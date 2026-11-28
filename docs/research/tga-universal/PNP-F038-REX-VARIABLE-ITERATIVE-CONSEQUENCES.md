# F038-REX-024D7K — Stratified iterative consequence closure

Parent D7J: 00b04fdfe9600313887b409a4849e87cd0382717. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Model preservation and certificate dependencies

Set F_0=F. At each round run D7J conditional propagation against the current factor database F_t. Collect completed traces deriving distinct unit or binary clauses that are not already present; append the corresponding factors as one stratum to obtain F_{t+1}. No trace in a stratum can reference a factor from that same stratum: every source index is interpreted against F_t, including original factors and all previous verified strata. Consequently F_t entails each appended clause by the D7J trace theorem, so Models(F_{t+1})=Models(F_t)=Models(F). This preserves complete model sets, coordinate identities, and least-witness ordering. Proofs reference prior factors by index rather than recursively expanding their proofs.

The checker independently enumerates original short forbidden-row clauses, checks global uniqueness and nonempty strata, and calls the existing independent conditional verifier against the earlier view for each batch. All appended factors are reconstructed independently. For a terminal unconditional propagation contradiction replay its trace against the final checked view; for a structural contradiction invoke the independent D7I checker against that view. Reversed strata, same-stratum references and duplicate clauses are rejected. Neither the producer's termination reason nor its work counters are needed for soundness.

First try D7I on the original formula. Then try it after each nonempty stratum, including a partial final stratum stopped by the shared budget. Stop on a checked contradiction, a completed round with no new consequences, a configured round limit, or budget exhaustion. A fixed point is only for the implemented restricted rule (empty and single assumptions, co-occurring coordinate pairs, original/current clauses, known-clause and unit-subsumption skipping); it is not a claim that every entailed binary clause has been found. UNKNOWN passes the exact original residual to the inherited D7D fallback with D7H's sparse cardinality screen. The adapter does not use augmentation to select a different SAT witness.

## Polynomial termination and conservative resource bounds

For k explicit Boolean coordinates, the number of distinct non-tautological unit and binary clauses is 2k+4 binom(k,2)=2k^2. Each nonempty stratum adds at least one previously absent clause. Therefore at most 2k^2 nonempty strata and one final empty pass can occur; this is the default round cap. A budget-stopped partial pass does not establish saturation. Every view has at most f+2k^2 factors for f original bounded-arity factors. D7J's per-pass bound is O((k+f+2k^2)^2), so a conservative upper bound on the iterative propagation stage is O((k^2+1)(f+k^2+k)^2) abstract operations. There are at most O(k^2) probes per pass (all signed singletons and pairs); the tighter bound O((k^2+1)^2(f+k^2+k)) is also available by counting O(f+k^2+k) work per probe. Each completed record has at most k forced steps and one conflict; shared factor references give O(k^3) proof words, not exponential proof expansion. Include O(f+k^2) input/database storage, polynomial working memory, and the inherited structural inference/checker costs separately. The shared charged budget counts probe starts and clause inspections across rounds, not index construction, proof checking or structural inference. All bounds assume abstract bounded-cost map operations with polynomial bit overhead. They do not bound general fallback or physical execution.

## Executed evidence

980 exhaustive small-formula comparisons: 665 SAT,315 UNSAT,26087 satisfying model occurrences. Includes 276 local relation types, 256 subsets of the eight two-coordinate unary/binary clauses, 192 seeded small formulas and all 256 independent coordinate complement masks of the eight-coordinate guarded gadget. 665 fixed points checked by another pass; 315 terminal conflicts; 4158 certified consequence records across 893 nonempty strata; maximum two nonempty strata. Every augmented model set matched the exhaustive oracle. Both D7J and D7K certified all 315 UNSAT cases on this selected corpus; no additional small-corpus refutations and no false refutations observed. D7K certificate classes: 310 inherited, four structural, one direct conflict. Five corrupted strata rejected. Local guarded gadget: all 96 models preserved; strata of 10 and 2 records; total 935 work including the final empty pass. One-round and one-unit limits return round-limit and budget respectively; zero rounds returns round-limit.

## Previous 819-coordinate obstruction eliminated

The D7J guarded fixture replaces each original occupancy exclusion by (-x OR -y OR u) and six ternary clauses guarding an inconsistent binary cycle. In the first round each gadget yields ten clauses (-u OR +/-t) for five internal coordinates t. In the second round these imply -u through failed-literal propagation and recover (-x OR -y). A shared verifier checks every dependency and the final D7I/Hall proof. Executed predecessor relational/affine checks retained all coordinates and zero affine equations.

|holes|complemented|coordinates|factors|first stratum|second stratum|charged work|core groups/holes|
|---:|---|---:|---:|---:|---:|---:|---|
|3|no|120|130|180|36|12002|4/3|
|6|no|819|910|1260|252|89630|7/6|
|6|yes|819|910|1260|252|89630|7/6|
|8|no|1845|2070|2880|576|212222|9/8|
|12|yes|5889|6682|9360|1872|738662|13/12|

For the prior barrier, 9031+7267 probes and 37800+35532 inspections yield 1512 verified consequences (including 126 guard units and 126 occupancy exclusions in stratum two). The nested Hall certificate proves seven groups/six holes, before either adaptive budget is invoked. The signed fixture also succeeds. Largest completed integrated audit is the 5889-coordinate guarded instance: 11232 consequence records; 13 groups/12 holes. No complete assignment enumeration in these five decisions. Attempts at 20 and 16 holes timed out in the connector runtime; they were removed from the committed audit portfolio, not counted as successful or as mathematical obstructions. No increase to the default shared two-million-unit budget is needed for any completed row.

## Physical replay

The exact adapter result for the local SAT fixture was executed and its residual tables recorded; the three guarded UNSAT certificates were independently verified in the large audit. By the adapter's verified contradiction contract, their residual is the constant empty unary stream. Due to connector tool-call limits, physical replay was executed separately on these exact streams rather than running the combined physical audit section in one call.

|fixture|affine residual worker|D7K worker|
|---|---:|---:|
|local guarded SAT|122463|122463|
|120-coordinate guarded PHP|not executed|2092|
|819-coordinate guarded PHP|not executed|2092|
|819-coordinate signed guarded PHP|not executed|2092|

Four original/minimized agreements, five exact clock comparisons, four one-short cutoffs. Local SAT least witness is eight zeros, matching the exhaustive oracle. No incremental measured physical savings in this stage; host costs excluded. Descriptor unchanged (3683 minimized states,180471 bits). Larger unreduced physical runs not attempted.

## Genuine structural fixed-point limitation: linear NAE triple systems

A linear triple system has distinct three-coordinate scopes with any two sharing at most one coordinate. Put the not-all-equal (NAE) relation on every triple. Under zero or one assumption, unit propagation cannot start. Under two assumptions on distinct coordinates, at most one triple contains both. If they differ, that triple is satisfied; if equal, it forces its third coordinate to the opposite value. No second triple can contain two of these three coordinates, by linearity. Thus no conflict can occur and no unit/binary consequence is derived by the D7J rule. This argument holds for every independent coordinate complement. Iteration reaches a fixed point immediately, even when the formula is UNSAT.

A Steiner triple system on v points covers every unordered pair exactly once. Each nonmonochromatic triple contains exactly one same-color pair. If there were an NAE coloring with r red and v-r blue points, the number of same-color pairs would be binom(r,2)+binom(v-r,2)=v(v-1)/6. For odd v>=7 the left side is at least (v-1)^2/4, strictly greater than v(v-1)/6. This gives a counting contradiction. The explicit audited Bose construction uses v=21, points (x,i) in Z_7 x Z_3, triples {(x,0),(x,1),(x,2)} and {(x,i),(y,i),((x+y)/2 mod 7,i+1 mod 3)} for x<y. The 70 triples cover all 210 pairs exactly once (checked by the audit); any coloring has at least 100 same-color pairs, but NAE would require exactly 70. All 21 coordinates remain free after predecessor preprocessing; zero affine equations. D7K fixed point after 22303 units,883 probes,21420 inspections, no derived clauses. Indexed resolution exhausts 2,000,000 units (5734 records,6897 pairs). **Inherited adaptive tree inference succeeds**: 4737 units,107 nodes,8 conflict leaves,7 splits,92 unit nodes; independent tree check passed. This is a proved limitation of iterative structural closure, NOT an unresolved full-pipeline instance or an unrestricted SAT lower bound. Additional exploratory Bose instances on 33,39,51,57,69,75,93 coordinates also reached empty structural fixed points (the 93-coordinate case used 1993735 charged units), and adaptive tree found refutations. Only the 21-coordinate case is pinned in the audit.

## Next

Investigate independently certified pair-counting/weighted cut bounds for NAE hypergraphs, starting from the exact Steiner pair-coverage identity. Distinguish polynomial certificate discovery for recognized designs from general Max-Cut/NAE-SAT optimization. Test nonuniform and incomplete pair coverage and seek genuine limits. Direct raw-selector physical normalization, on-tape inference and end-to-end physical accounting remain open. Main and PR #248 unchanged. Remote Proctor completion unconfirmed.
