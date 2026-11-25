# F037 — A forced choice invisible to bounded local consistency

PNP_RESOLUTION_STATUS = OPEN.

## Motivation

The direct single-path gate is now kernel checked, with all six
declarations axiom-free at d73b3c53bff889609863da5197aa3453e21b8de8
(run 45689218464, job 139469884359). The initial exact-head replay
failed on a redundant rewrite after case reduction in
decision_preserves. The repair changes the tactic only, not the
statement. All 4096 Python selector fixtures also passed their
expected outcome checks. No existence of a polynomial preserving
selector is proved.

## Satisfiable counterexample family

Take the prefix-OR pigeonhole 3-CNF P_k for k+1 pigeons and k holes.
A placement bit x_(p,j) indicates the selected hole. A prefix bit
s_(p,j) indicates that the hole is at most j. Encode s_(p,0)=x_(p,0),
s_(p,j)=s_(p,j-1) OR x_(p,j), and require s_(p,k-1). Add negative
binary clauses forbidding distinct pigeons in the same hole.
P_k is UNSAT since each pigeon must select some hole and no hole
can hold two pigeons; this remains true if a pigeon selects several.

Introduce a fresh selector z and pick either guard literal g=z or
g=not z. For every original clause C, impose g OR C. Clauses of
width at most two remain within width three. Split each guarded
width-three clause g OR a OR b OR c into
    (g OR a OR u) AND (not u OR b OR c)
with a fresh auxiliary u for that clause. These two clauses have
exactly the intended existential meaning: if both g and a are
false, u must be true and b OR c must hold; otherwise u=false
satisfies the second clause and the first is already true.

When g is true, assign every nonselector variable false, including
all fresh auxiliaries. This is a model. When g is false, any model
would satisfy P_k by eliminating the fresh auxiliaries. Therefore
the satisfiable guarded formula has exactly one viable selector
value. Either polarity is possible. There are O(k^2) variables
and O(k^3) clauses, all of width at most three.

## Wrong branch survives every k-scope consistency test

In the wrong restriction g=false, label each placement and prefix
variable by its pigeon. Each fresh split auxiliary also belongs
to a single pigeon, because all original ternary clauses encode
prefix gates within a single pigeon. For a scope S of at most k
remaining variables, assign injectively the pigeons touched by S
to holes. Use the indicated placement and prefix values, and set
each split auxiliary u to the negation of the literal a in its
split clause. Let H(S) be the set of all resulting restrictions.

Every H(S) is nonempty: at most k pigeons are touched. Every
contained clause holds, since a gate or split clause is valid
under the chosen hole, and a collision clause is satisfied by
injectivity. Restricting a pattern to a smaller scope stays in
the corresponding H. Every pattern extends to any larger scope
of at most k variables: keep the injection that produced the
pattern, and allocate unused holes to newly touched pigeons.
Consequently H survives any local consistency deletion procedure
requiring agreement and extension among these scopes; none of
the tracked tables becomes empty. The correct branch has a
genuine model, hence also survives.

For any fixed scope limit r, choose k>=max(2,r). Both branch
viability tests based only on whether the specified local
consistency closure rejects return the same nonrejection
outcome. A fixed tie preference based solely on those two
outcomes cannot preserve satisfiability on both guard polarities.
This does NOT prove that no algorithm can distinguish the
formulas by syntax, by table contents, by counting, or by
other invariants. The pigeonhole substructure has the independent
global counting certificate. Nor does it prove that an adaptive
choice of a different variable first must fail. The conclusion
is specifically about choosing the selector variable from
bounded-scope rejection flags. It supplies a falsifiable failure
family for that proposed preservation proof.

## Validation and scope

The Python fixture explicitly builds both guard polarities at
k=2 and k=3, checks the known good assignment, enumerates the
H(S) tables, verifies all contained clauses and checks every
one-variable extension via equality of projections. Its new
exact-head replay is pending; the mathematical family is not
inferred from the finite fixture. No new Lean credit is sought
for this note. Main unchanged.

## Next decision

The six verified logical bridge theorems reduce the positive
route to universal preservation plus polynomial bit cost.
The proposed rejection-flag selector lacks preservation.
A new candidate must give an explicit choice rule and prove
preservation independently of testing, rather than assume a
bounded rejection test identifies a viable branch. The central
existence claim remains open.
