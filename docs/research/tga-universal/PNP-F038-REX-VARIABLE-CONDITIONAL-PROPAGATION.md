# F038-REX-024D7J — Certified conditional unit propagation

Parent D7I: ce7aeec11ed7b681db2cd8b645949712793a0b92. Research only. PNP_RESOLUTION_STATUS=OPEN; PROMOTION=NONE; global routes 0/4; Omega obligations 0/6.

## Inference theorem and certificate contract

For a valid explicit Boolean arity-at-most-three factor formula F, convert each forbidden row to its exact clause. For a set A of zero, one or two literals on distinct coordinates, assume all literals in A true. Unit propagation may assign an unassigned literal p only from a source clause whose other literals are false. A terminal conflict must be a source clause with every literal false. Induction on the trace proves that F AND A is inconsistent; hence F entails the disjunction of the complements of A. Empty A proves original UNSAT; one or two assumptions produce a unit or binary clause.

The producer uses occurrence lists indexed by signed literals, a queue of newly true literals, and an initial scan of unit clauses. Every newly false literal triggers inspection of its occurrence list. Any unit or conflict becomes visible when its last required falsification occurs, unless a conflict has already stopped the probe. The independent checker reconstructs each referenced original forbidden row, replays every forced assignment, checks assumptions are distinct and valid, and checks the final conflict. It does not trust the queue or the producer's decision. All probes use only original source clauses; derived records are not fed back into subsequent probes.

The candidate portfolio consists of the empty assumption set, both signs of every coordinate, and all four sign choices for every distinct coordinate pair co-occurring in an original nontrivial clause. Skip already present consequences and binary candidates subsumed by a known unit. This is deliberately narrower than all coordinate pairs. A fixed work budget (default 2,000,000) counts probes plus clause inspections; on exhaustion retain only completed traces. Index construction, map costs, sorting, inherited inference and verification are outside this counter.

The augmented view appends independently certified implied clauses to the unchanged original factors. It has exactly the same full model set, not just existential equisatisfiability. Run inherited D7I before probing, then on the augmented view if any records were produced. Check nested D7I proofs against an independently reconstructed augmented instance. On UNKNOWN, pass the unmodified residual to D7D with the D7H sparse cardinality screen. Preserve the original residual and witness map if fallback is unresolved. A contradiction always maps to the inherited one-coordinate empty unary stream.

## Polynomial resource bounds

For k explicit coordinates and f bounded-arity factors, there are O(f) source clauses and at most 3 per clause distinct candidate coordinate pairs. At most 1+2k+4 min(3*8f, binom(k,2)) probes are attempted. Each assigns a coordinate at most once; each occurrence is visited at most once per probe, plus initial unit inspections. Thus O(k+f) abstract operations per probe, O((k+f)^2) total for this restricted single pass, O(k+f) working storage plus O(k(k+f)) explicit certificate records/words. A trace has at most k forced steps, each with a bounded-width source reference. Independent trace checking is linear in its explicit length under bounded-cost map operations. Inherited D7I and nested structural discovery retain their separate polynomial bounds; unrestricted fallback is not polynomially bounded. The budget is an abstract charged counter, not a complete runtime bound.

## Previous obstruction and executed evidence

For each concealed conflict gadget (-x OR -y OR u), (-x OR -u OR v), (-y OR -u OR -v), the co-occurring pair x,y is probed, forcing u then v and conflicting on the remaining clause. Each isolated gadget has ten satisfying assignments and projects to the three allowed occupancy pairs. This proof is invariant under coordinate complements and scope order; a sufficient budget guarantees the local probe unless the conflict is already known/subsumed or unconditional contradiction is found. No completeness theorem for global Hall selection or arbitrary 3-CNF follows.

932 exhaustive small-instance comparisons: 467 SAT, 465 UNSAT, 1954 satisfying model occurrences, all 276 local relation types, 256 two-coordinate clause subsets, 384 seeded formulas and all 16 complement masks of the local gadget. The producer found 439 unconditional propagation conflicts and 493 augmented views; all checked against complete model sets. 1215 derived records checked. D7I certified 458 cases; D7J 465 (seven additional: five direct propagation and two nested conditional proofs). Zero observed false refutations. Five damaged traces/views rejected. A one-unit budget stopped with no completed records and exact model preservation. This selected corpus is not a completeness proof for arbitrary formulas.

All six rows passed actual relational and affine predecessor processing, independent affine checks, and independent conditional/nested proof verification. All original coordinates remained free and zero affine equations extracted. No assignment enumeration for these decisions.

|holes|complemented|coordinates|factors|derived exclusions|forced trace steps|charged work|
|---:|---|---:|---:|---:|---:|---:|
|3|no|48|58|18|36|3379|
|6|no|315|406|126|252|32383|
|6|yes|315|406|126|252|32383|
|8|no|693|918|288|576|86719|
|12|yes|2145|2938|936|1872|364963|
|20|no|9177|12978|4200|8400|2391131|

The 315-coordinate row is D7I's prior obstruction: 3991 probes, 28392 clause visits, 9198 assignments (with repetitions), 840 candidate pair scopes, 126 certified exclusions, and seven groups/six resources. No D7D indexed resolution or tree invoked. The 9177-coordinate row used an explicitly raised four-million-unit propagation budget, 123691 probes, 2267440 visits, 288960 assignments, 26334 pair scopes, 21 groups/20 resources. A preliminary integrated run under default two-million budget returned structural UNKNOWN with 3555 completed records; the four-million run succeeded. Budget increase is disclosed, not a change to the default. All six large proofs are independently verified; the largest case has 4200 two-step traces plus their conflicts.

## Physical replay

|fixture|affine residual worker|D7J worker|
|---|---:|---:|
|small conditional conflict (already reduced by predecessor)|2092|2092|
|satisfiable ternary gadget|17285|17285|
|315-coordinate previous obstruction|not executed|2092|
|315-coordinate signed version|not executed|2092|

The integrated adapter was executed for all four fixtures and its exact residual factor tables were recorded. Due to connector call limits, physical execution was performed separately on those exact tables rather than executing the combined audit's physical section in one call. Four original/minimized agreements, six exact clock comparisons and four one-short cutoffs passed. SAT least witness 0,0,0,0. Two paired fixtures tie at 19377 aggregate transitions; no new measured physical saving asserted. Larger cases execute only the ten-symbol contradiction stream; host inference/checking excluded. Unchanged descriptor 3683 minimized states, 180471 bits.

## New surviving policy obstruction: guarded propagation rounds

Replace each original exclusion (-x OR -y) by (-x OR -y OR u) and six ternary guarded clauses (-u OR C) for the inconsistent binary cycle system C:
    (-a OR b), (-b OR c), (-c OR -a),
    (a OR e), (-e OR g), (-g OR a).

Use six fresh coordinates u,a,b,c,e,g per exclusion. The cycle system forces a -> -a and -a -> a, so u must be false; choosing u=false satisfies all guarded clauses and the link exactly when x,y are not both true. Local 256-assignment oracle confirms 96 satisfying assignments and three projected occupancy pairs. With x,y true, u becomes true but the remaining residual binary system has no unit clause. A single source-only pass therefore misses this pair's direct exclusion. The local first pass derives ten binary clauses of form (-u OR +/-t) for internal t; D7I implies -u, but the current adapter does not feed derived facts back into ternary propagation. A second local pass on the augmented formula independently derives -u and (-x OR -y), preserving all 96 local models. This is a local experiment, not a full second-round solver.

Full seven-pigeon/six-hole guarded instance: 819 coordinates, 910 ternary factors, all free after relational/affine stages, zero equations. Conditional single pass completes at 46831 work units, 9031 probes, 37800 visits, 21672 assignment events, 1260 derived records, 1848 pair scopes; nested structural inference UNKNOWN. D7D indexed resolution and tree each exhaust 2,000,000 units (12136 generated resolution records, 14834 processed pairs; 2519 tree nodes, 440 conflicts, 471 splits, 1607 units). Exact original residual retained. This is a configured-policy obstruction, not a proof-system lower bound or a general SAT complexity result.

## Next

Investigate stratified iterative conditional propagation with independently checked dependencies on earlier derived clauses, bounded monotone closure over unit/binary consequences, and compact proofs. Test the 819-coordinate guarded obstruction and find any genuine surviving limitations. Direct physical raw-selector normalization and end-to-end physical resource accounting remain open. Main and PR #248 untouched; remote Proctor completion not claimed.
