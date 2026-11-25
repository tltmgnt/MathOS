# F037 — q-Horn recognition beyond structural separators

PNP_RESOLUTION_STATUS = OPEN.

The preceding balanced separator audit passed at
4733af9d961f50dc04c7fca548095ba89df66c5f
(run 45686828202, job 139461507323).

## A different tractable promise

Use the established q-Horn class (Boros, Crama, Hammer; see Boros,
Hammer and Sun, Recognition of q-Horn formulae in linear time,
Discrete Applied Mathematics 55 (1994), 1–13,
https://doi.org/10.1016/0166-218X(94)90033-7).
The point of this experiment is integration with the existing exact
2-CNF checker, not a new SAT complexity class.

Assign literal weights z(l) in {0,1/2,1}, with z(l)+z(-l)=1
and sum of the weights in each normalized clause <=1.
Recognition is possible by rational LP: relax each positive
variable weight to [0,1], retaining the complement and clause
constraints. Round every weight below 1/2 to 0, every weight
above 1/2 to 1, and retain equality at 1/2. Complementarity is
preserved. If a clause has a weight above 1/2, all its other
weights must be below 1/2, so its rounded sum is at most 1.
Otherwise at most two weights equal 1/2, so again the rounded
sum is at most 1. The reverse implication is immediate.
Thus rational LP feasibility exactly recognizes the class in
polynomial time. The cited literature gives a faster recognizer.

The prototype uses SciPy/HiGHS floating-point feasibility to
propose weights, then verifies the doubled integer weights
exactly on every clause. Numerical failure or an invalid
candidate yields UNKNOWN. No certified rational LP implementation
or worst-case polynomial bound for HiGHS is claimed.

## Complete decision given a checked partition

Rename the integral-weight variables H so that their positive
literal has weight 1. Other variables Q have both weights 1/2.
Every H-only clause is Horn. Every clause mentioning Q contains
at most two Q literals and only negative H literals.

Compute the least Horn model by forward chaining. Each fired
positive head is forced in every model of the H-only constraints;
a fired negative-only clause proves contradiction. If no Horn
contradiction occurs, the least assignment satisfies all H-only
clauses (any violated clause would fire). Any full model must
contain its forced-true H variables. Because mixed clauses use
H variables only negatively, changing any extra true H bits to
false cannot invalidate a mixed clause. Consequently a full
model exists iff the 2-CNF residual obtained by assigning the
least Horn model is satisfiable. Solve that residual with the
existing complete 2-SAT procedure at backdoor budget zero.

The UNSAT certificate includes checked partition weights, a
sequence of forced Horn heads, and either a fired negative-only
Horn clause or the existing binary UNSAT certificate. Every
Horn head is independently replayed. Even an incomplete
forced-head sequence is sufficient for the residual UNSAT
check: clauses surviving the assignment have all their negative
H antecedents forced false in every model. SAT assignments
are unrenamed and checked against the original CNF. Given a
partition, work and certificate length are polynomial.

## Dense family outside earlier structural promises

For t triples of variables a_i,b_i,c_i, add disjoint Horn
ternaries (-a_i OR -b_i OR c_i). Add every negative binary
clause between variables in different triples. The primal
graph on these 3t variables is a clique. Add two units a_1,b_1,
and mixed clauses (-c_1 OR p), (-c_1 OR q). The final clause
is either (-p OR -q) (UNSAT) or (p OR q) (SAT control).
The Horn deduction forces c_1, activating the mixed
binary constraints. All variables in the first triple
can be true while other triples are false in the SAT control.

Give H literals weights 1/0 and p,q weights 1/2.
This is a valid q-Horn partition for every t, preserved under
arbitrary variable renamings and polarity flips. The connected
primal graph has 3t+2 vertices, and the original t disjoint
ternaries need at least t backdoor variables. Any separator
leaving components of size at most 2(3t+2)/3 must delete
at least t-1 vertices from the clique: the remaining clique
is connected and has at least 3t-s vertices. Thus fixed
separator size and logarithmic syntactic 2-CNF backdoor
budget both fail for sufficiently large t at the root.
The q-Horn promise has no such obstruction on this family.
This is a separation of structural promises, not hard SAT
instances or a lower bound for other decision algorithms.

## Evidence

Independent JavaScript execution enumerated all three-valued
weight assignments on 256 random small CNFs, checking the
decision against exhaustive original truth evaluation for
every valid partition (1274 partitions). Results: 113 SAT,
51 UNSAT, 92 UNKNOWN (no eligible partition). Ten dense
instances (five sizes with SAT/UNSAT controls, largest 98
variables) also passed using supplied partitions.
The new Python candidate additionally attempts LP discovery,
tests polarity flips and renaming, rechecks each returned
certificate, and rejects three malformed mixed proofs.
The Python exact-head replay is pending. Random streams differ.
The independent execution does not verify numerical discovery.

## Remaining gate

q-Horn is not all 3-CNF. For instance, all eight distinct
sign patterns of a triple cannot have a feasible weight
assignment: summing their eight inequalities would require
12 <= 8. The class oracle must reject such inputs (although
other mechanisms can solve them). Arbitrary joint Horn/2-CNF
constraints do not obey the one-way condition used here.
No general completeness proof, no new Lean credit, no main
change. The next meaningful step is to test whether a uniformly
discoverable combination of semantic and structural promises
has any generality theorem, rather than merely accumulate
known tractable subclasses.
