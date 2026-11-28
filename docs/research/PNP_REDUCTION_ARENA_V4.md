# MathOS v4 — certified reduction / obstruction feedback

The v3 graph-bound engine is extended with three deterministic constructive
profiles: unit propagation, unit/pure/subsumption, and those rules plus bounded
Davis–Putnam variable elimination. The adversarial side generates a paired
SAT/UNSAT family that blocks all these rules at the configured neighbor cap.
This is a restricted reduction experiment, not a P vs NP result.

## Run

    python -m mathos.research.pnp_reduction_arena --checkpoint artifacts/pnp-v4.json
    python -m mathos.research.pnp_reduction_arena --input cnf.json --c 1 --cap 4 --family-size 16
    python -m mathos.research.pnp_reduction_arena --resume artifacts/pnp-v4.json
    python -m unittest discover -s tests -p 'test_pnp_reduction_arena.py' -v

Input matches v3: {"n":4,"clauses":[[1,2,3],[-1,-2,4],[-3,-4]]}.

## Soundness contract

Normalization preserves satisfiability. A unit is forced; a pure variable
can satisfy all clauses containing it without affecting remaining clauses;
a clause containing another clause as a proper subset is redundant.
Davis–Putnam elimination replaces every pair (x OR A), (not x OR B) by
A OR B, discards tautological resolvents, and retains all unaffected
clauses. For an assignment to the other variables, failure to extend
would require both an unsatisfied positive residual and an unsatisfied
negative residual, contradicting a resolvent. Conversely any extension
satisfies all resolvents. The verifier recomputes these exact sets and
checks profile constraints, neighbor cap, non-growth of distinct
resolvents relative to removed clauses, and final variable map.
It checks soundness of a trace, not maximality of preprocessing. The
portfolio generator runs each rule to a fixed point. It does not emit
a reconstruction trace for satisfying assignments beyond the listed
rules and original variable map.

With fixed cap d <= 12, at most 3^d distinct non-tautological resolvents
are possible, and no rule grows the number of clauses; each unit/pure/
resolution removes an active variable, each subsumption removes a clause.
Thus the profile has polynomial overhead under the fixed cap and
non-growth restriction. Work/time/cell limits are cooperative. The
replay and implementation are not generally machine-proved correct.

## Shared family and restricted obstruction

For n >= 5, generate all triples of distinct variables. The SAT family
contains all six mixed-sign clauses for each triple (all-true witness);
the UNSAT family contains both monochromatic clauses for every triple.
Any assignment on five variables has at least three equal bits, violating
one monochromatic clause. The finite verifier checks an explicit
five-variable UNSAT subformula and a witness for the SAT family.

Both have complete primal graph K_n and exact treewidth n-1. Every
variable occurs in both polarities, all clauses have size three, and
there are no strict subsumptions. If n-1 > d, the bounded resolution
rule cannot start. Therefore the configured profiles leave both
normalized formulas unchanged. This family has size O(n^3) in the
input proxy and width n-1; for every fixed c and d, sufficiently large n
exceeds the logarithmic-width condition while remaining blocked.
This is a mathematical argument about these specific rules only, not
about all transformations or algorithms. The CLI finite experiments
are limited to n <= 24, and do not machine-prove the asymptotic family
argument. Neither family is asserted hard for SAT.

The arena tests two explicit hypotheses (every nonempty active CNF is
reduced; every CNF reaches logarithmic width). Only actual replayed
counterexamples mark them refuted. Absence of a counterexample is
not a proof. The selected profile uses certified threshold, upper bound,
output-size ordering; no runtime superiority claim is made. Both E01
and E02 and their original universal obligations stay unresolved.
The next constructive challenge is to generalize the semantic escape route below.

## Formal layer

The Lean file checks local Boolean resolution, pure literal and
subsumption identities, with an axiom-free policy in CI. It does not
formalize the complete multi-clause algorithm, the family theorem, or
the Python implementation. This deterministic engine does not call an
LLM; hypothesis generation is presently a fixed pair of executable
templates, not open-ended autonomous theorem discovery.


## Constructive feedback: semantic escape

The obstruction is immediately challenged by a separate recognizer.
It tries the all-true and all-false assignments, or a fixed five-variable
monochromatic triple core. For a verified satisfying witness it emits
the empty conjunction; for a verified contradictory subformula it emits
one empty clause. The verifier checks the witness against the signed
normalized input, or checks core membership and exhaustively evaluates
at most five core variables. Both paired adversarial formulas reduce
to width zero by this separate route. The recognizer returns no candidate
on unrecognized input; it cannot decide general SAT. The two refuted
hypotheses refer only to the original local-rule profiles, not this
extended semantic recognizer. This is a concrete constructive-obstruction-
constructive feedback cycle, not a universal solution.
