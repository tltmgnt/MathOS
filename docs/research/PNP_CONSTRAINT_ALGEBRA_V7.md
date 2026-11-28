# MathOS v7 — generalized Boolean constraint algebra

This extension moves beyond v6's complementary triple relation. It
recognizes arbitrary local Boolean relations of arity at most four
(after normalization), provided that all relations on exact clause
supports admit a common affine or bijunctive representation. It also
implements a bounded, one-variable conditioning route for mixed formulas.
This is a restricted certificate compiler, not a general SAT solver.

## Run

    python -m mathos.research.pnp_algebra_frontier --checkpoint artifacts/pnp-v7.json
    python -m mathos.research.pnp_algebra_frontier --input cnf.json
    python -m mathos.research.pnp_algebra_frontier --resume artifacts/pnp-v7.json
    python -m unittest discover -s tests -p 'test_pnp_constraint_algebra.py' -v

Input is JSON with n and clauses (signed nonzero integers 1..n).
Outputs are constant yes/no CNFs only when a decision certificate exists.
Unknown is neither UNSAT nor evidence of hardness. The finite input,
resource and conditioning limits are operational, not complexity claims.

## Representation and exact equivalence

Group normalized clauses by their exact variable support S. A group
defines the set R of satisfying assignments on S. Enumerate at most 16
assignments. In bijunctive mode, emit unary and binary clauses excluding
every forbidden unary/pair projection of R. In affine mode, emit every
nonempty subset parity equation constant across R; encode the empty
relation separately as 0=1. In either mode compare the conjunction of
these constraints against R on all assignments. If unequal, the mode
does not apply. This is complete for each local relation admitting the
respective representation: any binary clause valid on R is implied by
the emitted projections, and any linear equation valid on R is in the
enumerated family (or is a tautology). The recognizer is not complete
for globally equivalent formulas whose exact-support blocks do not
individually admit the chosen representation.

The independent verifier enumerates local source/target truth tables
using true-literal sets, rejects missing scopes and forged constraints,
and reconstructs the global conjunction. Hence local equivalence implies
global pointwise equivalence, including overlapping scopes. Bijunctive
mode reuses v5's certified SCC decision. Affine mode uses Gaussian
elimination over GF(2), tracking each row as an XOR of original equations.
A SAT certificate is a Boolean assignment; an UNSAT certificate is a
set of distinct original row indices whose XOR derives 0=1. Replay uses
set symmetric difference and independently evaluates the right hand side,
not Gaussian elimination. SAT witnesses also get checked on the original
normalized formula.

## Mixed algebra and bounded obstruction escape

If neither whole-formula mode applies, try conditioning on one variable
from up to eight deterministic candidates (most literal occurrences first).
A fixed assignment removes true clauses and false literals. For SAT, one
certified satisfiable residual suffices. For UNSAT, both values of the
same split must have certified contradictory residuals. Replay independently
restricts the original formula and checks the branch proof(s). No deeper
recursive splitting is attempted.

The algebra arena includes a genuine 3-variable XOR relation, which cannot
be expressed by a 2-CNF on those variables, and a binary OR relation,
which is not affine. Together they defeat both direct modes on the
connected mixed control. Conditioning turns the XOR into a binary parity
relation and permits a certificate. A contradictory mixed variant requires
both branches. Two disjoint ordinary ternary OR clauses remain unrecognized
even though they are satisfiable and easy; this explicitly marks a limitation
of the grammar, not of SAT algorithms.

## Complexity and verification scope

For fixed local arity, truth tables and emitted local constraints have
constant size. Grouping and normalization are polynomial in input length;
the assembled relation representation grows at most linearly in groups.
2-SAT and Gaussian elimination with provenance have polynomial overhead.
At most sixteen residuals plus two direct modes are attempted; the number
of branches is a fixed constant, not an unbounded search. These are
mathematical complexity arguments, not verified asymptotic machine models.
The budget is cooperative, logical provenance cells are capped, and input
normalization may impose tighter bounds. No arbitrary mixed affine/2-CNF
system is asserted tractable by this approach.

Lean checks five scoped facts about parity addition/cancellation,
contradiction from incompatible row sums, and SAT/UNSAT Boolean case
splits. It does not verify the full compiler, Gaussian elimination,
matrix provenance or asymptotic complexity. The executable report does
not claim to have performed formal checking; the separate CI job verifies
the Lean source with an axiom-free policy. The finite regression suite
tests all 256 ternary truth tables against independent closure predicates,
random affine and mixed systems, invalid certificates and resource
exhaustion. Universal E01/E02 remain unresolved.
