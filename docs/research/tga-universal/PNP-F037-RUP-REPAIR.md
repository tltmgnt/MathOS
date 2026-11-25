# F037 — RUP-checked constant overwrite

PNP_RESOLUTION_STATUS = OPEN.

Previous checked folding replay passed at
79054ae36f0d4c77796d6b64ced43449c0d31548
(run 45691397982, job 139477486299), with 695 accepted maps and
1984 model transports in the Python sample.

## Sound repair rule

For normalized CNF F and a nonempty partial assignment A, consider
each touched clause C. If A satisfies it, no check is needed.
Otherwise let D consist of its untouched literals. Require a
reverse unit propagation (RUP) proof of D: unit propagation on
F with every literal of D assumed false must reach contradiction.
This implies F entails D, because unit propagation is sound.
For every model x of F, overwriting its A coordinates gives
another model: untouched clauses are unchanged, directly satisfied
clauses hold, and all remaining touched clauses hold by D.

Therefore SAT(F) iff SAT(F restricted by A). This sufficient
condition strictly includes the autarky checker, since an autarky
directly satisfies every touched clause. It can also discover a
safe forced value through unit consequences. Simultaneous
overwrites can be stronger than single overwrites: the formula
x=y has no model-preserving single constant overwrite but
both joint constant settings pass this check.

For fixed r, enumerate all partial assignments of at most r
occurring variables, at most sum_{j=1}^r binom(n,j)2^j.
Each check performs at most m unit-propagation tests, each
with at most n assignments and polynomial input scans.
A successful step removes at least one occurring variable.
Repeat at most n times. This is a polynomial bit-cost
argument for fixed r, using ordinary finite lists and integer
identifiers; no LP, SAT oracle or implicit exponential
representation is needed. It is not a formal machine refinement.
The Python checker reruns all propagation obligations and then
checks the final leaf proof. A failed search returns the original
residual for the next solver; unsupported leaves give UNKNOWN.

## Separation fixture

In each of t blocks let a,b,c be a one-hot triple. Add
(a OR u), (not u OR v), (not v OR a). No unit is present.
Assuming a=false propagates u=true, v=true and then a=true.
Thus a is forced, and the original one-hot constraints force
b=c=false. The overwrite a=true passes the RUP check:
the unsatisfied negative one-hot clauses reduce to not b and
not c, each RUP by assuming the opposite and propagating.
Connect blocks with negative binary conflicts between their
second-color variables. For the UNSAT control also conflict
the first-color bits in blocks one and two. The SAT control
sets all first-color bits true and the other bits false.
The UNSAT control has incompatible forced first-color bits.

Every one-hot gadget forces the linear-autarky coordinates
on a,b,c to zero by the three pair inequalities and the
positive triple inequality. The added chain forces
0<=z_u<=z_v<=0, hence all coordinates zero. Every support
contains a single clause, so the preceding grouped translation
stabilizer is trivial. No syntactic gadget fold succeeds:
each first-color bit has two private chain clauses, one with
positive u and one with negative v; replacing it with a
literal of another gadget cannot produce an original
subsuming witness. The only signed one-hot triples recognized
are the original gadgets. The RUP rule eliminates these
instances at budget one (with binary leaf budget zero).
This is a simple forced-literal example, not a hard SAT
family or a novelty claim.

## Test evidence

Independent JavaScript execution on 128 random small formulas
enumerated all one- and two-variable overwrite candidates.
2185 accepted overwrites and 3083 satisfying-model transports
were checked, with exhaustive original/restricted satisfiability
comparison. All eight family cases (t=2,4,8,16; SAT and UNSAT)
passed, largest 80 variables. SAT controls reduced to no
clauses; UNSAT controls reached an empty clause. A preliminary
independent test incorrectly required all remaining clauses
to be binary even after reaching an empty clause; the audit
was corrected to accept the explicit contradiction first.
The fixture was also changed from two clauses sharing a
support to a distinct-support implication chain to remove
an incidental translation symmetry. The Python candidate
rechecks earlier selectors on the family and three malformed
repairs, and replays leaf evidence. Exact-head replay pending.

## Unresolved gate

This is a restricted sufficient condition (related to
unit-propagation-based redundancy and substitution rules).
It has no universal progress guarantee: long equality chains,
for example, admit no nonempty constant overwrite of proper
support preserving every model, because the all-zero and
all-one models cannot both be transported to a constant
coordinate without changing all remaining coordinates.
Other mechanisms handle such chains. The point is that
bounded overwrites, not SAT itself, are incomplete.
The established universal preservation and bit-cost gates
remain open; no additional Lean credit, main unchanged.
