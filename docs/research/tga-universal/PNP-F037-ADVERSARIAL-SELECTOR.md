# F037 — Symbolic adversarial selector audit

PNP_RESOLUTION_STATUS = OPEN.

The preceding certificate-complexity exact-head replay passed at
6563b565328a3f18b3de797c4c0c5e3907f346b4
(run 45693899592, job 139486173557). All six new declarations
in ProctorChoiceCertificates were reported axiom-free by Lean 4.14.0.
The historical cumulative reported verified count is now 1603;
this is not a progress percentage toward P vs NP.

## Direct discovery falsification instead of another promise solver

Fix n labeled variables and the vocabulary of every distinct
nonempty nontautological clause of width at most three.
It has M=sum_{k=1}^3 2^k binom(n,k)=O(n^3) elements.
Each input formula is represented by M presence bits.
This covers clause-set formulas, not arbitrary multiplicities or
input-order-dependent heuristics. An empty clause can be ignored
for counterexample generation because it precludes a SAT witness.

Fix the deterministic unit-first majority selector from the
single-path experiment: in ascending variable order, prefer a
positive unit on the current variable, then a negative unit, then
the more frequent residual polarity, choosing true on ties.
This is not global unit propagation. Keep one activity bit per
original clause; it is initially its presence bit and remains
true precisely when no earlier chosen literal satisfied it.
At step v an active clause containing v or not v contributes
to the corresponding polarity count, and it is a current unit
precisely when its maximum variable identifier is v. Retain
separate activity bits even when two residual clauses coincide,
matching the reference driver, which does not deduplicate residuals.

The majority comparison p>=q is the threshold test that at least
Q literals in the list of positive-clause activity bits and
negated negative-clause activity bits are true, where Q is the
original number of negative occurrences at v. A threshold circuit
uses the recurrence D(i,j)=D(i-1,j) OR
(bit_i AND D(i-1,j-1)), with D(i,0)=true and D(0,j)=false for j>0.
All choices, activity updates and threshold computations are
Boolean gates, with exact biconditional Tseitin clauses. The
number of gates is O(n M^2), with polynomial bit-length explicit
encoding. The Tseitin formula has no claim of width three
unless long gates are split into bounded fan-in gates.

Add n witness bits and require every present input clause to be
true on those bits. Require at least one final active clause
after the candidate's complete run. The resulting query is
satisfiable iff there exists an input clause set and a genuine
satisfying assignment for which the fixed driver fails.
The forward direction follows by gate determinism and the
witness clauses; the reverse assigns every gate by evaluation
on the given input and witness. Therefore an accepted query
model is a counterexample to the proposed universal selector.
A proof of UNSAT would establish absence of such a counterexample
only at the chosen n and for this vocabulary and driver.
This is an offline bounded verification query, not an efficient
SAT algorithm. Its polynomial construction cost does not imply
polynomial query solving cost.

## Executed validation

Local Python execution of the candidate source passed all 1024
pairs of clause sets and supplied assignments on the full two-bit
vocabulary. It compared the evaluated gate choices to an
independent direct implementation and the complete CNF truth
condition to the expected witness/failure predicate.

The three-variable query had 26 input clause flags, 1067
Boolean variables including gates and 3179 CNF clauses.
SciPy MILP proposed a model; every returned CNF clause was
checked with exact Boolean evaluation, then the original model
and the failing candidate execution were checked separately.
Deletion minimization produced the following four-clause failure:

    (not x2), (x1 OR x2),
    (not x1 OR not x2 OR x3),
    (not x1 OR x2 OR not x3).

The satisfying witness is (true,false,false).
The candidate returns (false,true,true), violating the
negative unit. In particular its first choice is false
by polarity majority; no current-variable unit overrides it.
The result refutes this exact policy, not all unit-propagation
policies. MILP output may vary; CI checks semantic failure
rather than demanding this particular counterexample.
The numerical backend is only a witness generator; timeout,
failure, or lack of a model is not a proof of query UNSAT.

## Research decision

The next direct selector candidate should be tested through a
symbolic failure query rather than repeated small random fixtures.
For arbitrary polynomial-time policies, bounded execution can
likewise be encoded by a suitable circuit simulation; that
general compiler is not implemented here. The central existence
of a universally preserving polynomial selector is still open.
No new Lean credit for this audit, no change to resolution flags
or main. The new repository workflow has not yet been verified.
