# F037 — Bounded-lookahead selector barrier

PNP_RESOLUTION_STATUS = OPEN.

## Previous evidence

The symbolic adversarial selector audit passed at
012404232baca0284c008e25881adc0c8f8b5d07
(run 45694635403, job 139488700241).
The three-variable counterexample and all 1024 circuit checks
were reproduced.

## Stronger explicit candidate

For each proposed bit at the next variable, apply global unit
propagation and explore both child assignments recursively to a
maximum of d binary decisions along any path. Each leaf returns
REJECT on an empty clause, MODEL on an empty formula, or OPEN
on exhaustion of its decision budget. A parent returns MODEL
if either child does, REJECT if both do, and OPEN otherwise.
Prefer a branch with MODEL, then avoid a branch with REJECT,
then select majority polarity with a fixed tie rule.
The implementation probes with ascending or descending variable
order. For fixed d, or d=O(log N) in encoded input length N,
this is a uniform polynomial-time bounded probe. It is not
a complete SAT decider.

## Adversarial family

Let k=d+3 and take the guarded prefix-OR pigeonhole formula
from F037 guarded choice. Its selector is variable 1, and
literal g is true exactly at the correct value. The restriction
g=false enforces injection of k+1 pigeons into k holes and is
unsatisfiable. The restriction g=true has a known model with
all pigeon and split auxiliary bits false.

Add more fresh binary clauses (not g OR w_i) than there are
occurrences of g in the guarded formula. Add d+1 fresh clauses
(not g OR a_i OR b_i) with pairwise disjoint pairs of variables.
All fresh variables are distinct from the guarded formula.
All added clauses disappear on the wrong branch. On the
correct branch, the binary padding clauses become positive
units and the d+1 fresh ternary clauses become disjoint
positive binary clauses. Extend the known correct model by
setting all fresh bits true. The resulting formula is SAT,
width at most three, has no initial units, and majority
polarity for variable 1 is strictly biased toward the wrong
value. Both orientations of the correct value are possible.

No probe of depth at most d can return MODEL on the correct
branch: the d+1 disjoint positive binary clauses require at
least one explicit decision involving a member of each pair
before they can all be deleted. Unit propagation elsewhere
cannot affect them; before a decision on either member,
neither has a unit occurrence. The correct branch cannot be
REJECT by soundness.

## Wrong branch cannot be refuted by bounded branching plus UP

This follows from the injective-placement local family H(S)
of the earlier guarded-choice proof. For every scope S of
at most k variables in the wrong restriction, H(S) is the
nonempty collection of patterns obtained by placing the
pigeons touched by S injectively into holes and evaluating
their tagged placement, prefix and split bits.
Every pattern satisfies contained clauses. Projection to a
subscope stays in H, and every pattern extends to any larger
scope of at most k variables.

Fix decisions on a set D with |D|<=d, and choose a pattern
alpha in H(D). For any S with |D union S|<=k use the
patterns on S obtained by extending alpha within H(D union S).
These conditioned tables remain nonempty and retain the
projection and extension properties.

Maintain the following invariant throughout unit propagation:
each assigned unit literal is true in every conditioned
singleton pattern for its variable (and every explicit
decision is consistent with alpha). To propagate a literal
from an original clause C, use the conditioned table on
the full scope of C. It exists since |D|+|C|<=d+3=k.
All other literals of C are false in that table by projection
and the preceding invariant; the remaining literal is true
because every pattern satisfies C. Projection from this
table covers the entire conditioned singleton table, so the
unit invariant is preserved. An empty residual clause would
have every literal false in its nonempty conditioned table,
contradicting local satisfaction. In particular UP cannot
report a contradiction at this state.

Whenever an adaptive binary probe chooses a fresh unassigned
variable, extend alpha to that variable using H(D union {v}),
and follow the branch with the extended value. Prior unit
assignments remain valid in the smaller conditioned tables.
Continue to depth d. A surviving path cannot report REJECT
and therefore the complete probe cannot reject the wrong
branch. It cannot report MODEL either, since the branch
is UNSAT and unit propagation plus explicit decisions is sound.
The argument works for arbitrary adaptive variable choices
inside the probe, not just the two implemented orders.

Thus both branches return OPEN and majority selects the
wrong value. This falsifies the candidate for each d without
requiring exhaustive solution of the generated pigeonhole
instances. The selector can never recover that lost model
existence without backtracking.

There are O(k^2) core variables and O(k^3) core clauses;
padding adds O(k^3) variables and clauses. With binary
identifiers the input length is O(k^3 log k). For any
prescribed logarithmic-depth bound c log N, sufficiently
large d dominates that bound; the same adversary defeats
probes up to d. Hence simply increasing the probe budget
from constant to logarithmic does not repair this policy.
This is not an exponential time lower bound for general
DPLL or a lower bound for every polynomial SAT algorithm.

## Validation

Independent JavaScript execution constructed ten satisfiable
adversaries (d=0..4 and both guard polarities), checked their
explicit models, ran the two branch probes with both variable
orders and counted 456 probe nodes in total. Every pair
returned OPEN/OPEN and the strict majority chose the wrong
bit. The largest case had 536 variables and 782 clauses.
The Python implementation also includes three tiny control
probes with REJECT, MODEL and OPEN outcomes.
Its exact-head replay is pending.

The mathematical result is an obstruction to a specified
selector and a proof system of bounded-depth branching plus
unit propagation, not to global counting. The wrong branch
has a recognizable pigeonhole contradiction and the correct
branch has an easy explicit model; an algorithm exploiting
this structure or a different outer variable order can
bypass this particular construction. The disjoint padding
also deliberately defeats a probe that stops only on an
empty residual; a component solver or another model-finding
test can remove that limitation. No universal progress
claim, no new Lean credit and no change to main.

## Research decision

The previous majority policy failed on three variables.
The stronger polynomial bounded-probe policy now fails
on a scalable analytically proved family, rather than
only on sampled inputs. This identifies a specific missing
ingredient: a decision invariant beyond bounded branching
and propagation, or an entirely different uniform algorithm.
The direct preservation and polynomial-bit-cost obligations
remain open. Further increasing this exact probe depth
within logarithmic budgets is not a route to completeness.
