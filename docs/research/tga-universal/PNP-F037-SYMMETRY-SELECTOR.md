# F037 — Certified global symmetry choices

PNP_RESOLUTION_STATUS = OPEN.

The previous guarded-choice audit passed at
2422cc3da628cca54cc9cfacdee3309dcab83f44
(run 45689394324, job 139470505013). The single-path preservation
framework remains verified on its separate exact head.

## A direct preservation rule

Group normalized 3-CNF clauses by identical variable support S.
Their conjunction defines an explicitly enumerable relation
A_S contained in GF(2)^S. Compute

    T_S = {b : A_S + b = A_S}.

Translation stabilizers are vector subspaces: zero preserves the
relation and the composition of two preserving translations is their
sum. This also holds for an empty relation. Enumerate the at most
eight local masks and their annihilator equations. A global mask
b preserves each grouped relation precisely when its restriction
to S lies in T_S for every S. Stack the local homogeneous equations
in a global binary matrix. Its kernel is exactly the subgroup of
translations preserving all grouped relations individually.
Gaussian elimination discovers a basis in polynomial time. This
uses local truth tables of bounded size but can find translations
with unbounded global support; it does not query SAT.

If a verified mask toggles variable v, setting v to zero preserves
satisfiability. Indeed any satisfying assignment with v=true can
be translated by the mask to a satisfying assignment with v=false.
For simultaneous choices, row-reduce the mask basis into echelon
form ordered by smallest set bit. Let p_i be each mask's pivot.
Clear pivot values in ascending order by applying that mask only
when the current value is true. Later masks have zero bits at
earlier pivots. Every model is transported to a model with all
pivots false. The converse follows by restriction semantics:
a model of the quotient extends by the fixed zero bits.

The exact checker checks every proposed mask against every
local relation and checks the pivot order. It need not trust the
nullspace algorithm. The quotient makes a batch of safe direct
choices without searching for an input model. It removes d
variables if the discovered subgroup has dimension d. No
completeness claim is made about the remaining quotient or about
semantic symmetries not preserving the individual grouped rows.

For encoded input length N, dense renaming uses at most N distinct
variables. Each local relation has at most eight patterns, so the
number of local equations is O(N). Ordinary binary elimination
and basis extraction use polynomial bit operations on explicit
O(N)-bit rows. The certificate consists of at most n masks of n
bits and the checker has polynomial cost. This is a mathematical
resource argument, not a Lean bit-machine refinement.

## Dense nonlinear example

For each of t blocks with bits a_i,b_i,c_i,d_i, impose both
c_i=a_i XOR b_i and d_i=a_i XOR b_i, each with four ternary
clauses. Impose all negative binary conflicts between output bits
in different blocks. Require c_1=true and either d_1=true (SAT)
or d_1=false (UNSAT). The translations flipping a_i and b_i
together are independent symmetries. For t>=2, each output bit
is fixed by a binary conflict relation having trivial translation
stabilizer, so these t masks form the entire local subgroup.
They survive variable renamings and polarity flips. Fixing a
pivot in each pair turns both XOR constraints into binary
equalities or disequalities. All remaining clauses are binary
and the previous complete 2-SAT solver decides them.

The sole connected primal block requires at least t syntactic
2-CNF backdoor variables, since one ternary support per block
is disjoint from all the others. The primal graph is biconnected:
each block contains triangles sharing the a_i,b_i edge and is
connected to other blocks by both outputs. Deleting a vertex
does not disconnect the remaining graph. Removing s vertices
leaves at least t-s untouched blocks; when t-s>=2 they are
connected by the output edges and contain 4(t-s) vertices.
A 2/3-balanced separator thus needs at least t/3 deletions
(up to the trivial small cases). q-Horn recognition fails
already on an untouched XOR relation: summing the four weight
inequalities gives 6<=4 because each positive/negative literal
appears twice. Thus the example escapes the earlier syntactic
promises and supports genuine coordinated safe choices. It
is not a hard SAT benchmark; other XOR inference also solves it.

## Exact semantic symmetry is not a free strengthening

For arbitrary normalized 3-CNF H(x), form K(y,x,u) by guarding
all clauses with y and splitting any resulting width-four clause
using fresh auxiliaries as in the preceding guarded-choice note.
K restricted to y=false is satisfiable iff H is satisfiable.
K restricted to y=true always has a model. Introduce a fresh v:

    F = K AND (not v OR y).

Both restrictions of F on v are satisfiable, because y=true is
available. Flipping only v preserves the complete Boolean
function F iff H is UNSAT. If H is unsatisfiable, every model
of K has y=true and F is independent of v. If H is satisfiable,
choose a model of K with y=false; setting v=false satisfies F
but flipping v violates the added clause. The construction is
polynomial and keeps width at most three. A witness of failure
of symmetry is one assignment on which F differs after the
specified flip. Hence checking whether a given single-bit
translation is an exact semantic symmetry is coNP-complete,
even for these guaranteed-satisfiable formulas with both
selector values viable.

This does not make finding SOME useful symmetry coNP-hard on
every input, or prove any general complexity lower bound.
It shows why replacing the checked subgroup with an exact
semantic-symmetry oracle would be an unjustified step. Moreover
symmetry is stronger than viability: in this reduction both
choices are safe even when the proposed symmetry is absent.

## Validation

An independent JavaScript implementation compared the discovered
basis span with every possible local translation on 256 random
small formulas, transported all 752 satisfying assignments of
the sample to their canonical zero-pivot representatives and
checked quotient satisfiability by exhaustive evaluation.
Ten random formulas had nontrivial discovered subgroups.
Twelve independently polarity-renamed dense formulas (six
sizes, SAT and UNSAT controls, largest 256 variables) produced
the expected symmetry dimensions and correct binary decisions.
All tests passed. The Python implementation adds three malformed
mask controls and uses the existing 2-CNF solver; its exact-head
replay is pending. Random streams differ between implementations.
The wrapper does not emit a standalone global UNSAT certificate.

## Remaining obligation

This is a sound partial selector based on an established
linear symmetry mechanism, not a proof of a universal selector.
A trivial stabilizer yields no guaranteed choice; no rule for
those cases is established. Universal preservation, total
polynomial cost for unrestricted 3-SAT, and independent review
remain open. No new Lean credit; main unchanged.
