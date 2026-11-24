# PNP-F028 — Resolution-oriented research gates and Horn backdoors

Baseline: F027 at de95cf7dfed22facbeec15d85b4184ba62b3c404, descended
from F025/F026. Existing milestone sources are retained unchanged.
F027 proves local Boolean identities and implements syntactic affine
backdoors; it already falsifies universal logarithmic primal-graph
covers. F028 addresses that obstruction with a larger residual class.
**P versus NP remains open. No mathematical novelty or independent
review is established.**

## Track A: deterministic polynomial-time SAT target

For a fixed standard bit encoding of arbitrary signed 3-CNF, construct
a total deterministic machine A with A(F)=SAT iff F is satisfiable and
T_A(F) <= C(1+|enc(F)|)^d for fixed input-independent constants C,d.
A verified bridge from standard NP-completeness of 3-SAT would imply P=NP.
Reject malformed strings, and include decoding, preprocessing, discovery,
branching, residual decisions, and output in the same uniform bound.

F028 is a restricted-parameter step: remove duplicates and tautologies
as in F027, choose a global sign orientation p in {+1,-1}, and connect
each pair of distinct positive literals in every oriented clause.
A vertex cover B leaves at most one positive literal after any assignment
to B, so every residual is Horn. Negative orientation complements all
variables and yields the dual-Horn alternative. Use the existing matching
2-approximation for each graph, choosing the smaller cover deterministically.
The chosen cardinality is at most twice the minimum over these two
syntactic cover models, not over all semantic or renamable-Horn backdoors.

Horn solving: interpret each residual as a rule body -> head or
body -> false. Start with the empty true set and repeatedly fire enabled
rules. Every fired head belongs to every satisfying assignment by induction.
A fired headless rule refutes the branch. If a complete scan makes no
change and no conflict fires, the resulting true set satisfies all rules.
Complement the assignment back if necessary and check the original CNF.

UNSAT traces list original clause indices in derivation order for every
cover assignment, ending with a headless conflict. The independent
replay routine reconstructs each cited residual from the original clauses,
checks premises and rejects missing assignments. It does not trust the
matching or scan counters. SAT checks the original witness. UNKNOWN is
never treated as a decision or a certificate.

## Cost contract

For explicit n variables, m input clauses, m' retained clauses, k cover
variables and L branch budget, at most min(L,2^k) branches are processed.
Each branch performs at most n+1 complete rule scans (or stops earlier),
with at most m' rules of width <=3, plus residual setup and witness work.
The trace has at most n+1 indices per branch. Certificate replay must
include every branch for UNSAT, with at most n+1 indices each. Cover
construction is polynomial in n+m in the abstract finite-list model.
The exact representation includes literal IDs of O(log(n+1)) bits and
indices of O(log(m+1)) bits. These scan bounds are not actual bit-machine
transition counts; Python sets/dicts and explicit n allocation need a
machine refinement. An encoded n in binary could be larger than the
actual input length; renumber occurring variables (or use an explicit
unary n encoding with a polynomial translation) before claiming a
standard complexity bound. Budgeted UNKNOWN is not a total SAT decider.
A bound k=O(log |enc(F)|) plus polynomial bit-cost implementation and
a sufficiently large polynomial budget would suffice; it is not proved.

## Track B: falsification before promotion

All positive triples on 12 variables had F027 cover size 11. F028 chooses
dual-Horn, k=0. This improves that specific case, not all instances.

New counterfamily for t>=3: n=2t-1, positive triples over {1,...,t},
negative triples over {t,...,2t-1}. The original primal graph is connected
through t. For either global orientation the positive-pair graph is K_t
plus isolated vertices. Any cover of K_t contains at least t-1 vertices
(otherwise two omitted vertices leave an uncovered edge), and t-1 suffice.
Thus both minimum cover sizes are t-1 while the explicit input has
O(t^3 log t) bits. The ratio to log(input length) is unbounded.
The formula is trivially SAT by setting 1,...,t true and the rest false.
This disproves a universal logarithmic cover for this particular
two-orientation representation, not a runtime lower bound on all SAT
algorithms, not a P != NP proof. Early SAT termination is possible.
Per-variable renaming, propagation, alternate tractable residual classes,
or different representations may defeat this family.

## Mandatory promotion gates (open unless specifically evidenced)

| Milestone | Requirement | State |
|---|---|---|
| F027 | compression and local affine identities | inherited; machine refinement open |
| F028 | broader Horn residual and replay, explicit counterfamily | implemented; new checks pending |
| F029 | uniform polynomial constructibility with standard encoding | open |
| F030 | adversarial families, semantic/renamable backdoor comparisons | partial: two-orientation counterfamily only |
| F031 | total recursion, certificate and bit-machine costs | open |
| F032 | relativization, algebrization, natural proofs where applicable | open |
| F033 | universal polynomial-time mechanism or relevant lower bound | open; syntactic small-cover conjecture refuted |
| F034 | end-to-end correctness, totality, bit-time and standard class bridge | open |
| F035 | independent reconstruction, literature novelty and semantic review | open |
| F036 | unconditional P=NP or P!=NP theorem | open |

Prioritize F029/F030: renamable-Horn or other tractable residual classes
with a constructive discovery algorithm, then seek counterexamples.
Do not assume a small parameter in a theorem and present the conditional
result as resolution. Track B lower bounds must identify their model;
a method obstruction does not separate complexity classes. Analyze
barriers on the actual proof strategy, not by checklist alone.
Natural proofs is primarily a circuit-lower-bound barrier.

Strict acceptance: pinned Lean replay; explicit theorem names and
transitive axiom audit; no sorry/admit/custom axioms or oracle costs;
statement fidelity; independent review; standard bit encoding and
fixed exponents; no promotion from finite tests. Classical logic, if
ever used, must be disclosed and separated from executable algorithms.
The new Lean file checks an abstract forced-head/conflict invariant;
it does not certify the Python implementation or the graph theorem.

## Reproduction

    python -m unittest discover -s tests -p 'test_tga_proctor_resolution_gates.py' -v
    python -m mathos.research.tga_proctor_resolution_gates
    lean -DwarningAsError=true formal/ProctorHornTrace.lean

The CI workflow replays F027 and runs F028 tests plus the exact Lean
axiom-line gate. Controls enumerate 4,162 bounded formulas and four
counterfamily sizes, not all formulas. A passing run verifies only the
specified tests and local theorem declarations. Keep actual CI evidence
separate from this design document.
