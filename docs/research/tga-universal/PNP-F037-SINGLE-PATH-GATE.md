# F037 — Direct single-path completeness gate

PNP_RESOLUTION_STATUS = OPEN.

The portfolio obstruction replay succeeded at
399aadd8f171d7f412f85f96b873fbfba3c7f4b8
(run 45687521990, job 139463936750).

## Direct target, without full semantic compilation

A selector p takes a residual formula R and a variable v and
returns one Boolean value. Its sole semantic obligation is

    SAT(R) implies SAT(R restricted by v=p(R,v)).

A deterministic driver takes the list of distinct occurring
variables and repeatedly restricts the current formula to the
selected value. After the list ends, check the resulting assignment
against the original CNF. The driver never accepts an invalid
assignment. If the preservation obligation holds on every input,
induction proves it accepts every satisfiable input. With a
polynomial-time selector on the encoded residual formula, there
are at most n calls on inputs of size polynomial in the original
encoding length, so total deterministic time including restriction
and model checking is polynomial. No exponential branch enumeration
or complete truth-function representation is necessary.

Conversely, a deterministic polynomial-time SAT decision algorithm
gives a polynomial-time selector: choose false if the false
restriction is satisfiable, and true otherwise. Shannon restriction
establishes preservation. Thus existence of such a uniformly
polynomial-time selector is equivalent to P=NP by SAT completeness.
This is a standard self-reduction, not a newly solved mathematical
obligation. The actual universal selector is missing.

The candidate Lean module ProctorSinglePathGate establishes the
logical implication, its converse for all covering variable lists,
the reference construction from a correct decider and a
counterexample rule. It reuses previously formalized restriction
and coverage results. These declarations do not assert the existence
of a preserving polynomial-time selector, and they do not establish
a formal machine-cost theorem. Kernel replay is pending.

## Audit interface and failure witness

Any fixed polynomial-time candidate selector can be tested without
a general UNSAT oracle: a formula plus a known satisfying assignment
is a certificate of failure if the driver's returned assignment
does not satisfy the formula. Recompute the deterministic run and
check both assignments. This is polynomial-time verification for a
uniformly polynomial candidate. For a finite fixture one may obtain
witnesses by exhaustive search, but generating counterexamples in
general is not assumed efficient. A failed candidate run without
a model of the original input is UNKNOWN, not proven UNSAT.
Deletion-minimization of a known failure can keep the supplied model
and retest the candidate after each clause deletion; this preserves
a checkable failure and terminates in polynomially many tests.

Independent JavaScript execution enumerated the same 4096 three-bit
fixture formulas used previously, comprising 1280 SAT and 2816 UNSAT.
Majority polarity selected satisfying models on 1104 SAT cases and
failed on 176. Unit-first majority passed all 1280 SAT fixtures,
but the following satisfiable formula defeats both:

    (-1 OR 2), (-1 OR -2), (1 OR 3), (1 OR 4), (1 OR 5).

The model 1=false, 2=false, 3=true, 4=true, 5=true satisfies all
clauses. Both candidates select 1=true first (there are no units,
and three positive occurrences versus two negative occurrences).
That choice produces opposite units on variable 2 and no
satisfying completion. A reference selector using exhaustive
residual SAT evaluation passes all 4096 fixtures but is exponential.
The Python fixture adds independent failure-witness and
deletion-minimality checks; exact-head replay is pending.

## Decision

The direct mathematical gate is now a precise witness-preservation
obligation for a uniform polynomial-time policy, not a count of
restricted promise classes or a claim that passing finite tests
ensures completeness. Even a policy passing every tested small
formula can fail on a larger formula, as above. There is no known
candidate here with a universal preservation proof and polynomial
bit-cost theorem. No new Lean credit until exact-head success,
no unrestricted P vs NP conclusion, and no main change.
