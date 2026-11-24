# PNP-F033 — Polarity-equivariant Hall recognition

PNP_RESOLUTION_STATUS = OPEN. PR #157 merged at
133877b0a560f2137cd4ebf3700d6b01b6a48c35. The original head
4fc82dbd57aa43e0a0876688f3834fba26c5cf9d failed the strict axiom
gate (run 45454461153, job 138660049523):
'ProctorHallDeficiency.positive_clause_demand' depends on axioms: [propext, Quot.sound]
'ProctorHallDeficiency.hall_cnf_unsat' depends on axioms: [propext, Quot.sound]
strict axiom check failed: ProctorHallDeficiency.positive_clause_demand
Process completed with exit code 1.
A subsequent repository commit d35c2da11735244a63fee5a33725a95ba4ee5d6a
replaced List.mem_map with constructive list induction. The final
PR run 45459157168 job 138676647424 passed Lean 4.14.0 (410fab728470)
with all seven Hall declarations axiom-free and unchanged strict
gates. Artifact 14952232146.
https://github.com/tltmgnt/MathOS/actions/runs/45454461153/job/138660049523
https://github.com/tltmgnt/MathOS/actions/runs/45459157168/job/138676647424

## Signed recognition policy

Normalize clauses as sets, remove tautologies and duplicates for
occurrence counting. A variable is eligible if exactly one of its
two signed literals occurs once and the other does not occur once.
Orient its unique once-occurring literal positively. Drop clauses
containing any ineligible variable for this inference only, retain
original clause indices, and pass the oriented subset to F033 Hall.
If the subset is refuted, remap every demand/conflict reference to
the original CNF and include the explicit list of complemented IDs.
If not, return UNKNOWN. Any polarity complementation of the input
transforms the selected rare signs equivariantly; eligibility,
oriented subset and matching graph are unchanged for fixed variable
IDs and clause order. In particular the output status and matching
edge count are invariant under independent flips of any variables.
This is not invariance under arbitrary structural encodings.

On unary PHP(h+1,h), h>=2, every variable occurs once in its demand
polarity and h times in the other. Hence all are eligible, and the
normalized oriented CNF is canonical PHP up to variable and row
permutations. The existing Hall engine finds the deficiency with no
branching. For equal-size PHP with h>=3 the same recovery applies;
h=2 has tied occurrence counts and can return UNKNOWN without
recognizing the matching subsystem, which is still sound.
For restricted matching encodings with each resource of size one or
at least three, the same rare-side argument applies. Resources of
size two are ambiguous, so no completeness claim for that broader
class is made.

## Certificate and hybrid

The checker validates an explicit sorted unique list of occurring
variable IDs to complement, transforms the entire original CNF
(not the selected subformula) and invokes the existing Hall checker
on the remapped original clause references. It never recomputes
occurrence counts, matching or the solver's selected subformula.
Complementation induces a bijection of assignments; a model of
the original CNF would give a model of the transformed CNF, which
the Hall certificate excludes. This is a paper-level transport
argument; the Lean theorem from PR #157 covers normalized positive
demands and negative pairs, not the signed Python transport.
A new wrapper tries SIGNED_HALL before the prior Hall and F032
routes. Existing solver entry points and strict gates unchanged.

## Negative result and evidence

Add a shared fresh g and all clauses (x_v OR g) to canonical PHP,
one per original variable. This preserves unsatisfiability and
makes the rare positive polarity occur twice; the opposite occurs
h times. g occurs h(h+1) times on one side and zero on the other.
No variable is eligible, even after arbitrary polarity flips.
The signed rare-side recognizer therefore returns UNKNOWN. The
original positive Hall engine may recover uncomplemented instances;
this is a counterexample to rare-side recognition, not to all
combinatorial methods or the full hybrid. More robust discovery
remains open.

New CI controls: 1600 random sparse CNFs, each solved in original
and independently complemented form, brute-force soundness and
polarity-invariance checks; all 64 polarity assignments for PHP2;
18 shuffled sparse PHP instances through 64 holes at seeds 11/29
with arbitrary signs and zero dynamic/pair budgets; 18 equal-size
controls; six noisy negatives; certificate tamper, original index
transport, normalization and hybrid fallback. Counts and outcomes
await actual CI. Structural matching bound remains polynomial in
explicit input; no total bit-machine cost theorem, executable
refinement, independent review or original scratch port. Main
untouched. No P vs NP promotion.
