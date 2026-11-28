# MathOS v26 — barrier-aware hypothesis evaluation

v25 passed computational and formal CI (46152616872): eight sizes,
eight algebraic promise controls, seven cancellation counterexamples,
no barrier avoidance claim.

## New constructive result: component parity

Recognize normalized CNF blocks on identical variable scopes, arity
one through eight. Each block must exclude exactly one parity class;
every active variable must occur in exactly two distinct equation
scopes. Build the multigraph with an equation as vertex and a variable
as edge. Multiple edges are allowed, but distinct scope blocks are
required by the recognizer. This is not arbitrary affine CNF recognition.

A component's XOR sum cancels its edge variables. Odd total charge
in any component proves UNSAT. Conversely, in an even component,
choose a spanning tree, set nontree edges to zero, and process leaves
toward the root, choosing the parent edge to satisfy each vertex.
The root is satisfied by the even charge invariant. Hence SAT iff
each connected component has even charge. The argument is uniform,
with polynomial bit overhead for bounded arity, not limited to prism
graphs. The implementation is subject to the existing input limits.
It independently verifies local truth tables, exact scope coverage,
incidence, union-find components and either a checked XOR identity
or a complete original-CNF satisfying assignment.

Two disconnected odd prism components give global even charge but
UNSAT. This refutes the unrestricted global-even sufficiency
hypothesis and motivates the component-local replacement. Four
sizes and all four charge combinations exercise the distinction;
random sparse renamings and degree-eight expander controls test
recognition beyond the training shape. The theorem is documented
mathematically; full formalization of the graph argument is absent.

## Fixed hypothesis grammar and obligations

Six explicitly authored hypotheses/claims are evaluated. Evidence
types distinguish finite refutation, documented scoped theorem,
documented asymptotic counterfamily, invalid inference rule and
unresolved universal conjecture. This is bounded evaluation of a
fixed grammar, not autonomous invention of arbitrary mathematical
statements or an automated barrier-avoidance checker.

The graph-twin control independently replays exact treewidth seven
and opposite 2-SAT decisions. v24's audited expander/padding/parity
reports supply the documented counterfamily to lower-bound
preservation by arbitrary polynomial SAT-preserving reductions.
A uniform transformation can recognize the explicitly generated
odd/even family by enumerating the polynomially many possible
sizes matching the input and compare canonical encodings, decide
by parity, and otherwise return the original CNF. This preserves
SAT and erases the restricted lower bound on that family. The
asymptotic argument still imports v23's published spectral and
width-size theorems. The same evidence invalidates the inference
from a restricted resolution lower bound to a SAT lower bound
without a simulation covering arbitrary algorithms.

A DAG keeps U01-U04 (uniformity, correctness, bit cost, logarithmic
width, total transformation) and L01-L02 (universal lower-bound
quantification and simulation overhead) unresolved. U05 and L03
are conditional inference steps, not closed proof nodes. The
unrestricted transformation is equivalent to P=NP: if P=NP,
decide and emit a constant formula; conversely, solve the certified
log-width output by polynomial-time elimination. Merely proposing
this transformation is therefore not progress on its existence.

The three barrier assessments remain not_assessed. Their published
definitions and assumptions must be checked against an actual
universal argument. A validator prevents claims from being upgraded
on the strength of bounded controls. Lean checks three abstract
logical lemmas, not the component theorem or the universal DAG.

## Reproduce

    python -m mathos.research.pnp_proof_simulation_frontier --checkpoint artifacts/v24.json
    python -m mathos.research.pnp_barrier_frontier --checkpoint artifacts/v25.json
    python -m mathos.research.pnp_hypothesis_obligations --simulation artifacts/v24.json --barriers artifacts/v25.json --checkpoint artifacts/v26.json
    python -m mathos.research.pnp_hypothesis_obligations --simulation artifacts/v24.json --barriers artifacts/v25.json --audit artifacts/v26.json

Audit verifies both upstream reports and their hashes, all component
certificates, graph twins, exact hypothesis mapping and unresolved
statuses. The experiment is not a benchmark of runtime or a proof
of novelty. No universal obligation is closed.
