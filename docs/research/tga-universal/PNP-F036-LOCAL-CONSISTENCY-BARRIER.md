# F036 — Bounded-scope local inference obstruction

PNP_RESOLUTION_STATUS = OPEN.

Status: elementary mathematical derivation, independently enumerated
finite controls, pending repository replay; not a Lean theorem or
a claim of a novel proof-complexity lower bound.

## A precise circuit-local mechanism to challenge

Maintain tables of possible Boolean assignments on every variable scope
of size at most k. Initially include all assignments satisfying the
clauses whose entire support lies in that scope. Delete assignments
that have no consistent extension to another tracked scope (or whose
restriction has already been deleted). Iterate to a fixed point.
This includes ordinary support-consistency propagation over these
scopes, even when the scopes include specified auxiliary gate variables.
For fixed k, the explicit table system and pairwise checks have
polynomial size and cost. A refutation by an empty table is sound.
The hypothesis that this procedure is universally complete is false
for every fixed k, including on 3-CNF with compact prefix OR circuits.

## Scalable counterexample

For k>=3, use k+1 pigeons and k holes. Variables x_(p,j) encode
placement and s_(p,j) encode prefix ORs, with j=0,...,k-1.
Enforce s_(p,0)=x_(p,0) and s_(p,j)=s_(p,j-1) OR x_(p,j)
using their ordinary width-two and width-three gate clauses. Require
s_(p,k-1)=1 and for distinct pigeons p,q forbid both x_(p,j)=1 and
x_(q,j)=1. The resulting 3-CNF has 2k(k+1) variables and
3k(k+1)+k*binom(k+1,2) clauses, polynomial encoded size.
It is unsatisfiable: each pigeon occupies at least one hole,
and no hole can contain two pigeons. The k=2 instance is also
unsatisfiable; its maximum scope cannot inspect a ternary clause.

For any scope S with |S|<=k, let H(S) be the partial assignments
obtained by choosing an injective placement of the pigeons that
have any x or s variable in S into the k holes. For a touched
pigeon assigned hole h, set x_(p,j)=(h=j) and s_(p,j)=(h<=j)
on the variables of S.

H(S) is nonempty because at most k pigeons are touched.
Every fully contained clause is true: the local assignments agree
with the indicated OR circuit for each pigeon, and injectivity
enforces the cross-pigeon constraints. Restricting a member of H(S)
to a smaller scope T gives a member of H(T). Every member of H(S)
can be extended to a member of H(T) whenever S is contained in T
and |T|<=k: keep its witnessing injection and allocate unused holes
to the newly touched pigeons. This does not require any global
injection of k+1 pigeons into k holes. More generally, for two
arbitrary tracked scopes S,T, restrict to their intersection and
extend to T. This supplies a consistent support in H(T) for each
member of H(S).

Therefore all H(S) members survive every deletion rule above,
by induction over the updates. No table becomes empty despite
global unsatisfiability. This rules out universal completeness for
any fixed scope bound for this exact gate vocabulary and rule set,
not arbitrary circuit reasoning with new gate definitions.

## Resolution connection

The same witness family prevents a width-(k-1) resolution proof:
every input clause is locally satisfied when k>=4. Suppose a derived
resolvent of width at most k-1 is falsified by a member of H(S)
on its support. Extend to the support plus the pivot (size <=k).
At least one parent clause is false, contradicting the induction
hypothesis after restricting to that parent's support. Weakening
is also sound in this argument. The empty clause is false in
H(empty), so no such refutation exists. This is a restricted-width
result only; the family admits other kinds of refutations.

## Executed computational cross-check

Independent JavaScript enumeration of every scope, every distinct
retained assignment, every contained clause, every one-variable
restriction and every one-variable extension succeeded:

k | variables | clauses | scopes | states | clause checks | restriction checks | extension checks
2 | 12 | 24 | 79 | 151 | 99 | 279 | 243
3 | 24 | 54 | 2325 | 9061 | 7002 | 26268 | 19164
4 | 40 | 100 | 102091 | 745326 | 666455 | 2924900 | 1990540

The Python fixture independently expresses the same finite enumeration.
The asymptotic argument is mathematical, not inferred from these tests.
The local tables themselves grow with k, so this audit is not a
polynomial-time solver for variable k.

## Decision

Fixed-scope exact local inference is not universally complete,
even with the supplied compact extension circuits. This does not
exclude changing the extension vocabulary, learning global constraints
or a different decision mechanism. In particular a counting inference
on this pigeonhole family can immediately supply the missing global
contradiction. A substantive next conjecture must specify how new
global constraints are generated, and prove a uniform bound rather
than assuming all necessary global consequences are available.
No new verified declaration credit. Main unchanged.
