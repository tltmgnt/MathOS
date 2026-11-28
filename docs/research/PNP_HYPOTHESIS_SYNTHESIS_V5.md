# MathOS v5 — bounded counterexample-guided hypothesis synthesis

This extends v4's fixed reduction arena with a finite route grammar,
certificate-producing semantic recognizers, counterexample-guided program
selection, deletion minimization, and separate heldout controls. It is
deterministic program synthesis over existing mathematical methods, not an
LLM or autonomous invention of new theorems. Both P versus NP pathways
remain open. Earlier v4 Lean proof failures were corrected on main before
this extension (v4 scoped and formal workflow subsequently passed).

## Run

    python -m mathos.research.pnp_hypothesis_synthesis --checkpoint artifacts/pnp-v5.json
    python -m mathos.research.pnp_hypothesis_synthesis --input cnf.json --seed 5205
    python -m mathos.research.pnp_hypothesis_synthesis --resume artifacts/pnp-v5.json
    python -m unittest discover -s tests -p 'test_pnp_hypothesis_synthesis.py' -v
    lean -DwarningAsError=true formal/PnpHypothesisRules.lean

The optional input JSON has n and clauses fields, using signed nonzero
integer literals in 1..n. Certificates use normalized variable identifiers.
A satisfying witness produces an empty conjunction; an UNSAT certificate
produces one empty clause. A missing certificate is not an UNSAT decision.

## Certified grammar

1. Constant assignment: all-true or all-false witness.
2. 2-CNF: implication graph, strongly connected components, and a satisfying
   assignment or two paths between opposite literals. The verifier checks
   each implication against the original normalized clause set; empty clauses
   have a separate certificate.
3. Horn: least-model forward chaining. UNSAT traces record the indices of
   forced unit clauses followed by a falsified clause. The verifier checks
   the units directly against the original signed clauses.
4. Renamable Horn: construct a 2-CNF on flip bits. A literal l is positive
   after renaming iff the signed literal -l evaluates true on those bits.
   Prohibit two simultaneous positives using (l_i OR l_j) for each pair in
   each clause. A satisfying flip vector produces a Horn formula. Its least
   model lifts through the inverse flips, or its forced unit trace proves
   contradiction. The verifier checks both the Horn property and the actual
   witness/trace in the original normalized formula.
5. Bounded contradictory core: for n <= 12 enumerate all supports of size
   min(n,5) and test the contained clauses. A core certificate contains at
   most 32 clauses (one violated clause per assignment to at most five
   variables), and is checked by subformula membership and exhaustive
   evaluation. The v4 fixed five-variable core recognizer is also retained
   for larger n.

The first four routes have polynomial overhead on their recognized classes:
SCC is linear in graph size apart from deterministic neighbor sorting,
Horn propagation needs at most n productive rounds, and renaming constraints
are quadratic in clause length. The fixed-five core search has a polynomial
support-count bound but is deliberately capped. None decides arbitrary SAT.
Budgets are cooperative and the cell cap is logical, not hard RSS.

## Synthesis and obstruction feedback

Start with one constant-only control. Enumerate all subsets of the five-route
grammar in ascending cardinality, with fixed order/tie-breaking. A constructive
program must cover every current training example by a replayed certificate.
The adversary searches a finite suite of structured examples and seeded
random CNFs. If the current program misses an example that another grammar
route can certify, greedily delete clauses while preserving both the reference
SAT decision and the coverage counterexample. Add the minimized result to
training and synthesize again. Each such iteration excludes the failing
program; the finite grammar has only 32 subsets.

Deletion minimization is bounded (64 trials by default). The report marks
deletion minimality only if a full final single-clause deletion pass completed.
This is relative to the observed route predicates and normalization, not
global minimum formula size. A separate holdout seed and sign variants are
not used for synthesis. All finite control decisions are independently
cross-checked by brute force, and all accepted route artifacts are replayed.
Target execution uses the selected program only; it does not silently
fall back to brute force.

The explicit controls distinguish four indispensable routes in this grammar:

- constant-only satisfiable mixed-sign complete triple family;
- six-variable inconsistent binary parity cycle, with no five-variable
  contradictory core and no Horn renaming;
- non-Horn but renamable-Horn satisfiable formula with no uniform witness;
- contradictory five-variable triple core shifted away from variable labels
  1..5, with two other variables present.

A fifth control flips one variable in the mixed-sign satisfiable triple
family. Its satisfying assignments are nonuniform, its clauses are ternary,
and its pairwise renaming constraints are contradictory. It is SAT but
unrecognized by every current route. This is a counterexample to coverage
of the configured grammar, not to general polynomial-time SAT solving.
Unrecognized examples are archived with minimized versions and retained
obligations rather than being labeled hard or unsatisfiable.

The program is smallest by number of routes for the observed training
constraints, not an optimized runtime algorithm. Coverage on these designed
finite tests is not a representative distribution, a statistical claim,
or a proof of completeness. Holdout misses and grammar gaps are explicitly
retained. No formal proof of general implementation correctness is claimed.

## Formal verification and governance

Lean 4.14.0 checks local sign-flip invariance, implication propagation,
and opposite-literal contradiction, with an axiom-free policy in CI.
These are separate scoped Boolean lemmas, not formalization of the SCC,
Horn, renaming reduction, or bounded synthesis algorithms. The JSON report
records that it has not performed formal verification, and universal E01/E02
proof obligations remain unresolved. No theorem novelty is asserted.

The next mathematical task is to expand the certificate grammar beyond
uniform witnesses, 2-SAT, renamable Horn and bounded UNSAT cores, or establish
precise restrictions on a broader transformation class. A failure in this
grammar does not establish an algorithm-independent lower bound.
